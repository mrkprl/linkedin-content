#!/usr/bin/env python3
"""Mette al loro posto le illustrazioni disegnate nell'app di ChatGPT.

Uso:
    python scripts/importa_illustrazioni.py programmati/2026-10-24.md img1.png img2.png img3.png img4.png

Le immagini vanno date nello stesso ordine delle scene che stampa
scripts/prompt_chatgpt.py (1 = copertina, poi le slide di testo con un'illustrazione).
Lo script le converte in JPEG, le rimpicciolisce a 1536 px di larghezza al massimo e
le salva in images/<data>/ con i nomi che usa render_carousel.py. Accanto a ognuna
scrive il .txt con il prompt di stile, così scripts/illustrazione.py le considera già
fatte e non le ridisegna con l'API.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from illustrazione import prompt_per  # noqa: E402
from publish import parse_post_file  # noqa: E402
from render_carousel import percorso_illustrazione, scene  # noqa: E402

LARGHEZZA_MAX = 1536


def importa(post: Path, immagini: list) -> list:
    meta = parse_post_file(str(post))["meta"] or {}
    carosello = meta.get("carosello")
    da_fare = scene(carosello)
    pagine = sorted(da_fare)
    if len(immagini) != len(pagine):
        raise SystemExit(f"{post}: servono {len(pagine)} immagini, ne hai date {len(immagini)}")
    personaggio = isinstance(carosello, dict) and carosello.get("personaggio") is True
    salvate = []
    for pagina, sorgente in zip(pagine, immagini):
        destinazione = percorso_illustrazione(post, pagina)
        destinazione.parent.mkdir(parents=True, exist_ok=True)
        with Image.open(sorgente) as img:
            img = img.convert("RGB")
            if img.width > LARGHEZZA_MAX:
                alto = round(img.height * LARGHEZZA_MAX / img.width)
                img = img.resize((LARGHEZZA_MAX, alto), Image.LANCZOS)
            img.save(destinazione, "JPEG", quality=88, optimize=True)
        destinazione.with_suffix(".txt").write_text(
            prompt_per(da_fare[pagina], personaggio) + "\n", encoding="utf-8")
        salvate.append(destinazione)
        print(f"  OK: {sorgente} → {destinazione}")
    return salvate


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("post", help="file del post, es. programmati/2026-10-24.md")
    parser.add_argument("immagini", nargs="+", help="le immagini, nell'ordine delle scene")
    args = parser.parse_args(argv)
    importa(Path(args.post), [Path(i) for i in args.immagini])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
