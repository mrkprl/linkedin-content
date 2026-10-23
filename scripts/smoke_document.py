#!/usr/bin/env python3
"""Verifica che il token possa caricare documenti (i caroselli PDF), senza pubblicare niente.

Disegna il carosello dell'esempio di riferimento e lo carica con la Documents API.
Il documento resta su LinkedIn senza essere collegato a nessun post: non lo vede
nessuno.

Uso:  python scripts/smoke_document.py
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
    upload_document,
)
from render_carousel import disegna_carosello, salva_pdf  # noqa: E402

ESEMPIO = Path(__file__).parent.parent / "examples" / "carosello-excel.md"


def main():
    if not ACCESS_TOKEN:
        print("Serve LINKEDIN_ACCESS_TOKEN")
        return 1
    person_id = PERSON_ID_OVERRIDE or get_person_id(ACCESS_TOKEN)
    meta = parse_post_file(str(ESEMPIO))["meta"]
    with tempfile.TemporaryDirectory() as tmp:
        pdf = Path(tmp) / "prova.pdf"
        salva_pdf(disegna_carosello(meta["carosello"]), pdf)
        print(f"→ Carico il carosello di prova ({pdf.stat().st_size // 1024} KB)")
        try:
            urn = upload_document(pdf, person_id, ACCESS_TOKEN)
        except RuntimeError as e:
            print(f"  ✗ Caricamento NON permesso: {e}")
            print("\n  Se l'errore è 403, il token non può caricare documenti: i post")
            print("  escono con la sola copertina finché non si risolve.")
            return 1
    print(f"  ✓ Documento caricato: {urn}")
    print("  Il token può pubblicare caroselli.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
