#!/usr/bin/env python3
"""Dice a che ora (ora di Roma) va pubblicato il post programmato di una data.

Uso:
    python scripts/orario.py 2026-11-09          # stampa per esempio 12:00

Ordine: `ora: "HH:MM"` nel frontmatter di programmati/<data>.md, poi il giorno
della settimana in orari.yaml, poi le 8:00. Solo libreria standard: gira prima
che il workflow installi le dipendenze.
"""

import datetime as dt
import re
import sys
from pathlib import Path

RADICE = Path(__file__).resolve().parent.parent
GIORNI = ["lunedi", "martedi", "mercoledi", "giovedi", "venerdi", "sabato", "domenica"]
PREDEFINITO = "08:00"
FORMATO = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _valore(testo: str, chiave: str):
    m = re.search(rf'^{chiave}:\s*["\']?([0-9:]+)["\']?\s*(#.*)?$', testo, re.M)
    if m and FORMATO.match(m.group(1)):
        return m.group(1)
    return None


def orario(data: str, radice: Path = RADICE) -> str:
    giorno = dt.date.fromisoformat(data)
    post = radice / "programmati" / f"{data}.md"
    if post.is_file():
        parti = post.read_text(encoding="utf-8").split("---")
        if len(parti) >= 3:
            ora = _valore(parti[1], "ora")
            if ora:
                return ora
    orari = radice / "orari.yaml"
    if orari.is_file():
        ora = _valore(orari.read_text(encoding="utf-8"), GIORNI[giorno.weekday()])
        if ora:
            return ora
    return PREDEFINITO


if __name__ == "__main__":
    print(orario(sys.argv[1]))
