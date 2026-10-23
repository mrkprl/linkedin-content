#!/usr/bin/env python3
"""Prepara il messaggio da incollare nell'app di ChatGPT per disegnare le illustrazioni
di un carosello, senza usare l'API (rientra nell'abbonamento ChatGPT).

Uso:
    python scripts/prompt_chatgpt.py programmati/2026-10-24.md
    python scripts/prompt_chatgpt.py programmati/*.md

Per ogni post stampa:
- quali immagini servono e in che pagina vanno (1 = copertina);
- il messaggio per ChatGPT, con lo stesso stile di scripts/illustrazione.py e le
  scene scritte nel blocco `carosello:`.

Nei post con `personaggio: true` il messaggio chiede di allegare
assets/personaggio.jpg, così il fattorino resta uguale.

Le immagini scaricate da ChatGPT si mettono al loro posto con
scripts/importa_illustrazioni.py.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from publish import parse_post_file  # noqa: E402
from render_carousel import scene  # noqa: E402

STILE = """Stile, uguale per tutte: illustrazione editoriale piatta, in stile vettoriale, con contorni neri decisi, forme semplici e ombre leggere. Sfondo avorio caldo (#F4F2EC). Colore principale terracotta (#D97757), poi beige kraft (#D4B28C), crema (#FBF8F3), un verde salvia tenue e nero inchiostro (#141413). Disegna gli oggetti della scena, niente decorazioni astratte.

Composizione: formato orizzontale (3:2), soggetto al centro con molto spazio vuoto sopra, sotto e ai lati. Niente di importante vicino ai bordi, perché l'immagine verrà tagliata in una fascia larga e bassa.

Vietato: testo, lettere, numeri, etichette o schermi leggibili; loghi e marchi; persone riconoscibili (al massimo mani o figure di spalle, senza volto)."""

PERSONAGGIO = """Ti allego l'immagine del personaggio, il fattorino: in ogni scena deve comparire identico (stesse proporzioni, stessi colori, cappellino terracotta e borsa a tracolla). È l'unico personaggio della scena."""


def nome_pagina(pagina: int) -> str:
    return "copertina" if pagina == 1 else f"pagina {pagina}"


def messaggi(post: Path) -> tuple:
    """Restituisce (pagine, messaggi): le pagine che hanno un'illustrazione e un
    messaggio per ognuna, da mandare uno alla volta nella stessa chat. Chiedere
    tutte le scene insieme non funziona: ChatGPT fa un collage e lo taglia col
    codice, oppure ripete la prima scena."""
    meta = parse_post_file(str(post))["meta"] or {}
    carosello = meta.get("carosello")
    da_fare = scene(carosello)
    if not da_fare:
        return [], []
    pagine = sorted(da_fare)
    n = len(pagine)
    testi = [" ".join(da_fare[p].split()) for p in pagine]
    primo = [
        f"Mi servono {n} illustrazioni per un carosello LinkedIn, che ti chiederò una "
        "per messaggio. Ora genera solo la prima, UNA immagine.",
        "",
        STILE,
    ]
    if isinstance(carosello, dict) and carosello.get("personaggio") is True:
        primo += ["", PERSONAGGIO]
    primo += ["", f"Scena 1: {testi[0]}"]
    altri = [
        f"Ora UNA sola immagine, stesso stile e formato: scena {i}. {t}"
        for i, t in enumerate(testi[1:], 2)
    ]
    return pagine, ["\n".join(primo)] + altri


def messaggio(post: Path) -> tuple:
    """Come messaggi(), ma con tutto in un testo solo (per anteprima e test)."""
    pagine, testi = messaggi(post)
    return pagine, "\n\n---\n\n".join(testi)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("post", nargs="+", help="file dei post, es. programmati/2026-10-24.md")
    args = parser.parse_args(argv)
    for i, percorso in enumerate(args.post):
        post = Path(percorso)
        pagine, testo = messaggio(post)
        if i:
            print("\n" + "=" * 72 + "\n")
        if not pagine:
            print(f"{post}: nessuna illustrazione da disegnare")
            continue
        ordine = ", ".join(f"{j} = {nome_pagina(p)}" for j, p in enumerate(pagine, 1))
        print(f"{post} · {len(pagine)} immagini ({ordine})")
        meta = parse_post_file(str(post))["meta"] or {}
        if (meta.get("carosello") or {}).get("personaggio") is True:
            print("Allega assets/personaggio.jpg al messaggio.")
        print("Manda un messaggio alla volta nella stessa chat, aspettando ogni immagine.")
        _, testi = messaggi(post)
        for j, t in enumerate(testi, 1):
            print(f"\n--- messaggio {j} ---\n{t}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
