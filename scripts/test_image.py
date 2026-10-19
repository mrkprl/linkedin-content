#!/usr/bin/env python3
"""Test dell'infografica e del suo caricamento. Esegui: python3 scripts/test_image.py

Non chiama LinkedIn: le risposte dell'API sono simulate. Controlla che
- ogni post del repo con un blocco `immagine:` si disegni senza errori;
- i blocchi sbagliati vengano rifiutati con un messaggio chiaro;
- il post con immagine mandi a LinkedIn la URN e il testo alternativo giusti.
"""

import sys
import tempfile
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).parent))

import publish  # noqa: E402
from publish import parse_post_file  # noqa: E402
from render_image import ErroreImmagine, H, W, disegna  # noqa: E402

BASE = {"modello": "frase", "titolo": "Titolo", "frase": "Ciao", "alt": "Descrizione"}

SBAGLIATI = [
    ("riga sola", "immagine: sì"),
    ("modello sconosciuto", {**BASE, "modello": "torta"}),
    ("manca il titolo", {k: v for k, v in BASE.items() if k != "titolo"}),
    ("manca alt", {k: v for k, v in BASE.items() if k != "alt"}),
    ("alt troppo lungo", {**BASE, "alt": "a" * 301}),
    ("numero senza didascalia", {**BASE, "modello": "numero", "numero": "5"}),
    ("confronto con una voce", {**BASE, "modello": "confronto",
                                "voci": [{"nome": "A", "valore": 1, "testo": "1"}]}),
    ("valore non numerico", {**BASE, "modello": "confronto", "voci": [
        {"nome": "A", "valore": "tanto", "testo": "x"},
        {"nome": "B", "valore": 2, "testo": "y"}]}),
    ("due voci in evidenza", {**BASE, "modello": "confronto", "voci": [
        {"nome": "A", "valore": 1, "testo": "x", "evidenza": True},
        {"nome": "B", "valore": 2, "testo": "y", "evidenza": True}]}),
    ("titolo che non ci sta", {**BASE, "titolo": "parola " * 60}),
    ("fonte troppo lunga", {**BASE, "fonte": "esempio.com/" + "a" * 120}),
]


class Risposta:
    def __init__(self, status, json=None, headers=None, text=""):
        self.status_code = status
        self._json = json or {}
        self.headers = headers or {}
        self.text = text

    def json(self):
        return self._json


def test_rendering(failures):
    repo = Path(__file__).parent.parent
    trovati = 0
    for folder in ("published", "approved", "pending", "archive", "examples"):
        for post in sorted((repo / folder).glob("*.md")):
            meta = parse_post_file(str(post))["meta"] or {}
            if "immagine" not in meta:
                continue
            trovati += 1
            try:
                img = disegna(meta["immagine"])
                assert img.size == (W, H), img.size
                print(f"  [OK ] {folder}/{post.name} — immagine {W}x{H}")
            except Exception as e:  # noqa: BLE001
                failures.append((f"{folder}/{post.name}", "immagine valida", str(e)))
                print(f"  [FAIL] {folder}/{post.name}: {e}")
    if not trovati:
        failures.append(("esempi", "almeno un post con immagine", "nessuno"))


def test_validazione(failures):
    for label, blocco in SBAGLIATI:
        try:
            disegna(blocco)
        except ErroreImmagine as e:
            print(f"  [OK ] rifiutato: {label} ({e})")
            continue
        failures.append((label, "ErroreImmagine", "accettato"))
        print(f"  [FAIL] accettato: {label}")


def test_caricamento(failures):
    chiamate = []

    def finto_post(url, headers=None, json=None, timeout=None):
        chiamate.append(("POST", url, headers, json))
        if "images" in url:
            return Risposta(200, {"value": {"uploadUrl": "https://upload.example/x",
                                            "image": "urn:li:image:ABC"}})
        # Il primo tentativo di post fallisce: l'immagine è ancora in elaborazione.
        if sum(1 for c in chiamate if c[1] == publish.LINKEDIN_POSTS_API) == 1:
            return Risposta(422, text="media not ready")
        return Risposta(201, headers={"x-restli-id": "urn:li:share:1"})

    def finto_put(url, headers=None, data=None, timeout=None):
        chiamate.append(("PUT", url, headers, len(data)))
        return Risposta(201)

    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "prova.png"
        disegna(BASE).save(png)
        with mock.patch.object(publish.requests, "post", finto_post), \
             mock.patch.object(publish.requests, "put", finto_put), \
             mock.patch.object(publish.time, "sleep", lambda s: None):
            urn = publish.upload_image(png, "PERSONA", "TOKEN")
            post_id = publish.publish_post("testo", "PERSONA", "TOKEN",
                                           {"id": urn, "altText": "Descrizione"})

    init, put = chiamate[0], chiamate[1]
    post = [c for c in chiamate if c[1] == publish.LINKEDIN_POSTS_API]
    controlli = [
        ("initializeUpload con owner persona",
         init[3] == {"initializeUploadRequest": {"owner": "urn:li:person:PERSONA"}}),
        ("initializeUpload con LinkedIn-Version", init[2].get("LinkedIn-Version")),
        ("PUT sull'indirizzo ricevuto, con il token",
         put[0] == "PUT" and put[1] == "https://upload.example/x"
         and put[2] == {"Authorization": "Bearer TOKEN"} and put[3] > 0),
        ("post riprovato dopo il primo rifiuto", len(post) == 2 and post_id == "urn:li:share:1"),
        ("post con content.media giusto",
         post[-1][3].get("content") == {"media": {"id": "urn:li:image:ABC",
                                                  "altText": "Descrizione"}}),
    ]
    for label, ok in controlli:
        print(f"  [{'OK ' if ok else 'FAIL'}] {label}")
        if not ok:
            failures.append((label, "vero", "falso"))

    # Senza immagine non si riprova e il payload non ha content.
    chiamate.clear()
    with mock.patch.object(publish.requests, "post",
                           lambda *a, **k: chiamate.append(k) or Risposta(422, text="no")):
        try:
            publish.publish_post("testo", "PERSONA", "TOKEN")
            failures.append(("errore senza immagine", "RuntimeError", "nessun errore"))
        except RuntimeError:
            pass
    ok = len(chiamate) == 1 and "content" not in chiamate[0]["json"]
    print(f"  [{'OK ' if ok else 'FAIL'}] senza immagine: un tentativo solo, niente content")
    if not ok:
        failures.append(("senza immagine", "1 tentativo senza content", str(chiamate)))


def run():
    failures = []
    test_rendering(failures)
    test_validazione(failures)
    test_caricamento(failures)
    if failures:
        print(f"\n{len(failures)} test falliti:")
        for label, atteso, ottenuto in failures:
            print(f"  - {label}: atteso {atteso!r}, ottenuto {ottenuto!r}")
        return 1
    print("\nTutti i test passati.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
