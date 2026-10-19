#!/usr/bin/env python3
"""Verifica che il token possa caricare immagini, senza pubblicare niente.

Disegna l'immagine dell'esempio di riferimento e la carica con la Images API.
L'immagine resta su LinkedIn senza essere collegata a nessun post: non la vede
nessuno.

Uso:  python scripts/smoke_image.py
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from publish import (  # noqa: E402
    ACCESS_TOKEN,
    PERSON_ID_OVERRIDE,
    get_person_id,
    parse_post_file,
    upload_image,
)
from render_image import disegna  # noqa: E402

ESEMPIO = Path(__file__).parent.parent / "examples" / "funzione-progetti.md"


def main():
    if not ACCESS_TOKEN:
        print("Serve LINKEDIN_ACCESS_TOKEN")
        return 1
    person_id = PERSON_ID_OVERRIDE or get_person_id(ACCESS_TOKEN)
    meta = parse_post_file(str(ESEMPIO))["meta"]
    with tempfile.TemporaryDirectory() as tmp:
        png = Path(tmp) / "prova.png"
        disegna(meta["immagine"]).save(png)
        print(f"→ Carico l'immagine di prova ({png.stat().st_size // 1024} KB)")
        try:
            urn = upload_image(png, person_id, ACCESS_TOKEN)
        except RuntimeError as e:
            print(f"  ✗ Caricamento NON permesso: {e}")
            print("\n  Se l'errore è 403, il token va rigenerato con lo scope w_member_social.")
            print("  Finché non funziona, i post con immagine non partono.")
            return 1
    print(f"  ✓ Immagine caricata: {urn}")
    print("  Il token può pubblicare post con immagine.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
