#!/usr/bin/env python3
"""Test del carosello, delle illustrazioni e della pubblicazione come documento.
Esegui: python3 scripts/test_carousel.py

Non chiama né LinkedIn né OpenAI: le risposte sono simulate. Controlla che
- ogni post del repo con un blocco `carosello:` si disegni, al massimo in 4 pagine,
  e il PDF abbia tutte le pagine;
- i blocchi sbagliati vengano rifiutati con un messaggio chiaro;
- le parole fra ** vengano riconosciute, con la punteggiatura attaccata;
- le illustrazioni finiscano nella pagina giusta, e senza illustrazione la pagina
  resti di solo testo, senza cubi decorativi;
- ogni illustrazione si chieda una volta sola per lo stesso prompt, e senza chiave
  si salti;
- il post con carosello mandi a LinkedIn il documento giusto, e con un 403 ripieghi
  sulla sola copertina.
"""

import base64
import io
import re
import sys
import tempfile
from pathlib import Path
from unittest import mock

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))

import illustrazione  # noqa: E402
import publish  # noqa: E402
import render_carousel  # noqa: E402
from publish import parse_post_file  # noqa: E402
from render_carousel import (  # noqa: E402
    PAGINE_MAX, ErroreImmagine, H, W, disegna_carosello, nome_illustrazione,
    parole_evidenziate, salva_pdf, testo_semplice,
)
from render_image import KRAFT, KRAFT_SCURO  # noqa: E402

BASE = {
    "copertina": {"titolo": "Titolo con **parola**", "illustrazione": "una scrivania"},
    "slide": [
        {"titolo": "Uno", "testo": "Testo della prima slide.", "illustrazione": "un telefono"},
        {"titolo": "Due", "frase": "Scrivi questa frase."},
    ],
    "alt": "Descrizione",
}
TESTO = {"titolo": "T", "testo": "x"}


def con(**modifiche):
    return {**BASE, **modifiche}


SBAGLIATI = [
    ("riga sola", "carosello: sì"),
    ("manca la copertina", {k: v for k, v in BASE.items() if k != "copertina"}),
    ("manca l'illustrazione della copertina", con(copertina={"titolo": "Titolo"})),
    ("illustrazione troppo lunga", con(copertina={"titolo": "T", "illustrazione": "a" * 501})),
    ("asterischi non chiusi", con(copertina={"titolo": "Titolo **aperto", "illustrazione": "x"})),
    ("nessuna slide", con(slide=[])),
    ("quattro slide", con(slide=[TESTO] * 4)),
    ("tre slide e la chiusura: 5 pagine", con(slide=[TESTO] * 3, chiusura="Fine.")),
    ("slide senza contenuto", con(slide=[{"titolo": "Vuota"}])),
    ("titolo della slide troppo lungo", con(slide=[{"titolo": "t" * 61, "testo": "x"}])),
    ("numero senza testo", con(slide=[{"titolo": "N", "numero": "5"}])),
    ("due contenuti nella stessa slide",
     con(slide=[{"titolo": "N", "numero": "5", "testo": "x", "frase": "y"}])),
    ("illustrazione su una slide con la frase",
     con(slide=[{"titolo": "F", "frase": "y", "illustrazione": "z"}])),
    ("confronto con una voce",
     con(slide=[{"titolo": "C", "voci": [{"nome": "A", "valore": 1, "testo": "1"}]}])),
    ("manca alt", {k: v for k, v in BASE.items() if k != "alt"}),
    ("titolo che non ci sta", con(copertina={"titolo": "parola " * 60, "illustrazione": "x"})),
    ("testo che non ci sta", con(slide=[{"titolo": "L", "testo": "parola " * 400}])),
    ("fonte troppo lunga", con(fonte="esempio.com/" + "a" * 120)),
]


class Risposta:
    def __init__(self, status, json=None, headers=None, text=""):
        self.status_code = status
        self._json = json or {}
        self.headers = headers or {}
        self.text = text

    def json(self):
        return self._json


def controlla(failures, label, ok, dettaglio=""):
    print(f"  [{'OK ' if ok else 'FAIL'}] {label}")
    if not ok:
        failures.append((label, "vero", dettaglio or "falso"))


def pagine_pdf(percorso: Path) -> int:
    return len(re.findall(rb"/Type\s*/Page(?!s)", percorso.read_bytes()))


def ha_cubi(img: Image.Image) -> bool:
    """I cubi decorativi hanno le facce kraft: se quei colori ci sono, ci sono i cubi."""
    colori = {c for _, c in img.getcolors(maxcolors=1 << 20)}
    return KRAFT in colori or KRAFT_SCURO in colori


def test_rendering(failures):
    repo = Path(__file__).parent.parent
    trovati = 0
    for folder in ("published", "approved", "pending", "archive", "examples"):
        for post in sorted((repo / folder).glob("*.md")):
            meta = parse_post_file(str(post))["meta"] or {}
            if "carosello" not in meta:
                continue
            trovati += 1
            try:
                car = meta["carosello"]
                pagine = disegna_carosello(car, render_carousel.cartella_post(post))
                attese = 1 + len(car["slide"]) + (1 if car.get("chiusura") else 0)
                assert len(pagine) == attese <= PAGINE_MAX, f"{len(pagine)} pagine"
                assert all(p.size == (W, H) for p in pagine)
                with tempfile.TemporaryDirectory() as tmp:
                    pdf = Path(tmp) / "c.pdf"
                    salva_pdf(pagine, pdf)
                    assert pagine_pdf(pdf) == attese, f"PDF con {pagine_pdf(pdf)} pagine"
                print(f"  [OK ] {folder}/{post.name} — {attese} pagine")
            except Exception as e:  # noqa: BLE001
                # Solo gli esempi devono disegnarsi per forza: un post sbagliato esce
                # col solo testo e la PR lo aveva già detto.
                if folder == "examples":
                    failures.append((f"{folder}/{post.name}", "carosello valido", str(e)))
                    print(f"  [FAIL] {folder}/{post.name}: {e}")
                else:
                    print(f"  [AVVISO] {folder}/{post.name}: {e} (esce senza carosello)")
    if not trovati:
        failures.append(("esempi", "almeno un post con carosello", "nessuno"))


def test_validazione(failures):
    for label, blocco in SBAGLIATI:
        try:
            disegna_carosello(blocco)
        except ErroreImmagine as e:
            print(f"  [OK ] rifiutato: {label} ({e})")
            continue
        failures.append((label, "ErroreImmagine", "accettato"))
        print(f"  [FAIL] accettato: {label}")
    # Una slide sola e la chiusura facoltativa sono permesse.
    try:
        n = len(disegna_carosello(con(slide=[TESTO], chiusura="Fine.")))
        controlla(failures, "una slide con la chiusura: 3 pagine", n == 3, str(n))
    except ErroreImmagine as e:
        controlla(failures, "una slide con la chiusura: 3 pagine", False, str(e))


def test_pagine(failures):
    parole = parole_evidenziate("Fai i **conti** sul tuo **Excel**.")
    controlla(failures, "parole evidenziate riconosciute",
              parole[2] == [("conti", True)] and parole[5] == [("Excel", True), (".", False)],
              str(parole))
    controlla(failures, "due parole nello stesso riquadro",
              [p[0][1] for p in parole_evidenziate("**A te** resta")] == [True, True, False])
    controlla(failures, "titolo del documento senza asterischi",
              testo_semplice("Fai i **conti** sul tuo **Excel**.") == "Fai i conti sul tuo Excel.")

    blu, verde = (0, 128, 255), (0, 200, 90)
    with tempfile.TemporaryDirectory() as tmp:
        cartella = Path(tmp)
        Image.new("RGB", (1536, 1024), blu).save(cartella / nome_illustrazione(1), "PNG")
        Image.new("RGB", (1536, 1024), verde).save(cartella / nome_illustrazione(2), "PNG")
        # .jpg di nome, PNG di contenuto: Pillow lo apre lo stesso e i colori restano esatti.
        con_foto = disegna_carosello(BASE, cartella)
        senza = disegna_carosello(BASE, cartella / "manca")
    controlla(failures, "copertina con l'illustrazione nel riquadro",
              con_foto[0].getpixel((W // 2, H - 400)) == blu, str(con_foto[0].getpixel((W // 2, H - 400))))
    controlla(failures, "slide di testo con l'illustrazione in alto",
              con_foto[1].getpixel((W // 2, 300)) == verde, str(con_foto[1].getpixel((W // 2, 300))))
    controlla(failures, "senza illustrazioni le pagine escono di solo testo",
              senza[0].getpixel((W // 2, H - 400)) != blu and senza[1].getpixel((W // 2, 300)) != verde)
    controlla(failures, "niente cubi decorativi, con o senza illustrazioni",
              not any(ha_cubi(p) for p in con_foto + senza))
    confronto = disegna_carosello(con(slide=[{"titolo": "C", "voci": [
        {"nome": "A", "valore": 1, "testo": "1"}, {"nome": "B", "valore": 3, "testo": "3"}]}]))
    controlla(failures, "i cubi restano nei confronti", ha_cubi(confronto[1]))


def jpeg_finto() -> str:
    buf = io.BytesIO()
    Image.new("RGB", (32, 32), (200, 100, 50)).save(buf, "JPEG")
    return base64.b64encode(buf.getvalue()).decode()


def test_illustrazione(failures):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        post = tmp / "2026-01-01.md"
        post.write_text(
            "---\ndate: 2026-01-01\ncarosello:\n  copertina:\n    titolo: T\n"
            "    illustrazione: una scrivania con un portatile\n  slide:\n"
            "    - titolo: Uno\n      testo: x\n      illustrazione: un telefono\n"
            "    - titolo: Due\n      frase: y\n---\n\nTesto\n", encoding="utf-8")
        chiamate = []

        def finto_post(url, headers=None, json=None, timeout=None):
            chiamate.append((url, headers, json))
            return Risposta(200, {"data": [{"b64_json": jpeg_finto()}]})

        with mock.patch.object(render_carousel, "IMAGES", tmp / "images"), \
             mock.patch.object(illustrazione.requests, "post", finto_post):
            nessuna = illustrazione.genera(post, chiave="")
            controlla(failures, "senza chiave non chiama OpenAI",
                      not chiamate and all(v is None for v in nessuna.values()))

            prima = illustrazione.genera(post, chiave="sk-test")
            controlla(failures, "con la chiave salva copertina e slide di testo",
                      sorted(prima) == [1, 2] and all(p and p.exists() for p in prima.values())
                      and prima[2].name == "illustrazione-02.jpg" and len(chiamate) == 2,
                      str(prima))
            url, headers, payload = chiamate[0]
            controlla(failures, "chiamata con modello, formato e prompt giusti",
                      url == illustrazione.API and headers["Authorization"] == "Bearer sk-test"
                      and payload["model"] == illustrazione.MODELLO_DEFAULT
                      and payload["size"] == "1536x1024"
                      and "una scrivania con un portatile" in payload["prompt"]
                      and "no text" in payload["prompt"].lower()
                      and "cube" not in payload["prompt"].lower(), str(payload)[:200])

            illustrazione.genera(post, chiave="sk-test")
            controlla(failures, "stessi prompt: non le rifà", len(chiamate) == 2)

            post.write_text(post.read_text(encoding="utf-8").replace("un telefono", "una tazza"),
                            encoding="utf-8")
            illustrazione.genera(post, chiave="sk-test")
            controlla(failures, "scena di una slide cambiata: rifà solo quella",
                      len(chiamate) == 3 and "una tazza" in chiamate[-1][2]["prompt"])

        def errore(*a, **k):
            return Risposta(400, {"error": {"message": "prompt rifiutato"}})

        with mock.patch.object(render_carousel, "IMAGES", tmp / "altre"), \
             mock.patch.object(illustrazione.requests, "post", errore):
            esito = illustrazione.genera(post, chiave="sk-test")
            controlla(failures, "errore di OpenAI: niente illustrazioni, nessuna eccezione",
                      all(v is None for v in esito.values()))


def test_pubblicazione(failures):
    repo = Path(__file__).parent.parent
    esempio = repo / "examples" / "carosello-excel.md"
    meta = parse_post_file(str(esempio))["meta"]

    def scenario(status_documento):
        chiamate = []

        def finto_post(url, headers=None, json=None, timeout=None):
            chiamate.append(("POST", url, json))
            if "documents" in url:
                if status_documento != 200:
                    return Risposta(status_documento, text="forbidden")
                return Risposta(200, {"value": {"uploadUrl": "https://upload.example/d",
                                                "document": "urn:li:document:DOC"}})
            if "images" in url:
                return Risposta(200, {"value": {"uploadUrl": "https://upload.example/i",
                                                "image": "urn:li:image:IMG"}})
            # Il primo tentativo fallisce: il documento è ancora in elaborazione.
            if sum(1 for c in chiamate if c[1] == publish.LINKEDIN_POSTS_API) == 1:
                return Risposta(422, text="media not ready")
            return Risposta(201, headers={"x-restli-id": "urn:li:share:1"})

        def finto_put(url, headers=None, data=None, timeout=None):
            chiamate.append(("PUT", url, data[:5]))
            return Risposta(201)

        with tempfile.TemporaryDirectory() as tmp, \
             mock.patch.object(render_carousel, "IMAGES", Path(tmp)), \
             mock.patch.object(publish, "ACCESS_TOKEN", "TOKEN"), \
             mock.patch.object(publish.requests, "post", finto_post), \
             mock.patch.object(publish.requests, "put", finto_put), \
             mock.patch.object(publish.time, "sleep", lambda s: None):
            avvisi = []
            media, opzioni = publish.prepare_media(str(esempio), meta, "PERSONA", avvisi)
            post_id = publish.publish_post("testo", "PERSONA", "TOKEN", media, **opzioni)
        return chiamate, media, avvisi, post_id

    chiamate, media, avvisi, post_id = scenario(200)
    put = [c for c in chiamate if c[0] == "PUT"]
    post = [c for c in chiamate if c[1] == publish.LINKEDIN_POSTS_API]
    controlla(failures, "carosello caricato come documento PDF",
              put and put[0][1] == "https://upload.example/d" and put[0][2] == b"%PDF-")
    controlla(failures, "post con il documento e il titolo senza asterischi",
              post[-1][2]["content"] == {"media": {"id": "urn:li:document:DOC",
                                                   "title": "Claude fa i conti sul tuo Excel"}},
              str(post[-1][2].get("content")))
    controlla(failures, "post riprovato finché il documento è pronto",
              len(post) == 2 and post_id == "urn:li:share:1" and not avvisi)

    chiamate, media, avvisi, post_id = scenario(403)
    controlla(failures, "con 403 sui documenti esce la sola copertina come immagine",
              media == {"id": "urn:li:image:IMG", "altText": meta["carosello"]["alt"]}
              and avvisi and post_id == "urn:li:share:1", str(media))

    try:
        scenario(500)
        controlla(failures, "con 500 sui documenti il post si blocca", False, "nessun errore")
    except RuntimeError:
        controlla(failures, "con 500 sui documenti il post si blocca", True)


def run():
    failures = []
    test_rendering(failures)
    test_validazione(failures)
    test_pagine(failures)
    test_illustrazione(failures)
    test_pubblicazione(failures)
    if failures:
        print(f"\n{len(failures)} test falliti:")
        for label, atteso, ottenuto in failures:
            print(f"  - {label}: atteso {atteso!r}, ottenuto {ottenuto!r}")
        return 1
    print("\nTutti i test passati.")
    return 0


if __name__ == "__main__":
    raise SystemExit(run())
