#!/usr/bin/env python3
"""Chiede a OpenAI l'illustrazione per la copertina del carosello.

Uso:
    python scripts/illustrazione.py approved/2026-10-24.md
    python scripts/illustrazione.py approved/2026-10-24.md --forza

Legge `carosello.copertina.illustrazione` (la scena, scritta dalla routine), la
inserisce in un prompt di stile fisso e salva images/<data>/illustrazione.jpg.
Accanto salva illustrazione.txt con il prompt usato: se il prompt non cambia, lo
script non richiama l'API, così un secondo push sullo stesso branch non paga una
seconda immagine. Se Marco corregge la scena nella PR, il prompt cambia e
l'illustrazione si rifà.

Serve la variabile OPENAI_API_KEY (nella Action è il secret con lo stesso nome).
Senza chiave, o se l'API risponde con un errore, lo script lo dice ed esce con 0:
la copertina esce con i cubi al posto dell'illustrazione e il post parte lo stesso.

Variabili facoltative:
    OPENAI_IMAGE_MODEL    default gpt-image-2.5-flare
    OPENAI_IMAGE_QUALITY  default medium (low, medium, high, xhigh, max, auto)
"""

import argparse
import base64
import io
import os
import sys
from pathlib import Path

import requests
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from publish import parse_post_file  # noqa: E402
from render_carousel import percorso_illustrazione  # noqa: E402

API = "https://api.openai.com/v1/images/generations"
MODELLO_DEFAULT = "gpt-image-2.5-flare"
QUALITA_DEFAULT = "medium"
# Orizzontale: il riquadro della copertina è più largo che alto, e il taglio al
# centro perde poco.
DIMENSIONE = "1536x1024"

STILE = (
    "Flat editorial illustration for the cover of a LinkedIn carousel.\n"
    "Scene (described in Italian): {scena}\n\n"
    "Style: clean flat vector look, thick and even black outlines, simple geometric "
    "shapes, soft shading only. Warm ivory background (#F4F2EC). Main accent terracotta "
    "(#D97757), with kraft beige (#D4B28C), cream (#FBF8F3) and near-black ink (#141413). "
    "A few small isometric cubes with black outlines may appear as a decorative motif.\n"
    "Composition: landscape, the subject centered with generous empty margins, nothing "
    "important near the edges because the image will be cropped.\n"
    "Strictly no text: no letters, words, numbers, labels or readable screens. No logos, "
    "brand marks or real products. No recognizable people: if people are needed, show "
    "only hands or figures seen from behind, without faces."
)


def prompt_per(scena: str) -> str:
    return STILE.format(scena=" ".join(str(scena).split()))


def scena_del_post(post: Path) -> str:
    meta = parse_post_file(str(post))["meta"] or {}
    carosello = meta.get("carosello")
    if not isinstance(carosello, dict) or not isinstance(carosello.get("copertina"), dict):
        return ""
    return str(carosello["copertina"].get("illustrazione") or "").strip()


def messaggio_errore(response) -> str:
    try:
        return response.json()["error"]["message"]
    except (ValueError, KeyError, TypeError):
        return response.text[:300]


def genera(post: Path, forza: bool = False, chiave: str = None) -> Path:
    """Restituisce il percorso dell'illustrazione, oppure None se non c'è."""
    scena = scena_del_post(post)
    if not scena:
        print(f"{post}: nessuna illustrazione da disegnare (manca carosello.copertina.illustrazione)")
        return None
    prompt = prompt_per(scena)
    destinazione = percorso_illustrazione(post)
    file_prompt = destinazione.with_suffix(".txt")
    esiste = destinazione.exists()
    if esiste and not forza and file_prompt.exists() \
            and file_prompt.read_text(encoding="utf-8").strip() == prompt.strip():
        print(f"{post}\n  OK: illustrazione già disegnata con questo prompt, non la rifaccio")
        return destinazione

    chiave = (os.environ.get("OPENAI_API_KEY", "") if chiave is None else chiave).strip()
    if not chiave:
        print(f"{post}\n  ? OPENAI_API_KEY non impostata: la copertina "
              + ("tiene l'illustrazione di prima" if esiste else "esce con i cubi"))
        return destinazione if esiste else None

    modello = os.environ.get("OPENAI_IMAGE_MODEL", "").strip() or MODELLO_DEFAULT
    qualita = os.environ.get("OPENAI_IMAGE_QUALITY", "").strip() or QUALITA_DEFAULT
    payload = {
        "model": modello,
        "prompt": prompt,
        "size": DIMENSIONE,
        "quality": qualita,
        "background": "opaque",
        "output_format": "jpeg",
        "output_compression": 88,
        "n": 1,
    }
    headers = {"Authorization": f"Bearer {chiave}", "Content-Type": "application/json"}
    try:
        response = requests.post(API, headers=headers, json=payload, timeout=300)
    except requests.RequestException as e:
        print(f"{post}\n  ! OpenAI non risponde ({e}): la copertina esce senza illustrazione nuova")
        return destinazione if esiste else None
    if response.status_code != 200:
        print(f"{post}\n  ! OpenAI ha risposto {response.status_code}: {messaggio_errore(response)}")
        return destinazione if esiste else None
    try:
        dati = base64.b64decode(response.json()["data"][0]["b64_json"])
        Image.open(io.BytesIO(dati)).verify()
    except Exception as e:  # noqa: BLE001
        print(f"{post}\n  ! risposta di OpenAI senza un'immagine valida ({e})")
        return destinazione if esiste else None

    destinazione.parent.mkdir(parents=True, exist_ok=True)
    destinazione.write_bytes(dati)
    file_prompt.write_text(prompt + "\n", encoding="utf-8")
    print(f"{post}\n  OK: illustrazione salvata in {destinazione} ({modello}, qualità {qualita})")
    return destinazione


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("post", help="file del post, es. approved/2026-10-24.md")
    parser.add_argument("--forza", action="store_true",
                        help="rifà l'illustrazione anche se il prompt non è cambiato")
    args = parser.parse_args(argv)
    genera(Path(args.post), forza=args.forza)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
