#!/usr/bin/env python3
"""Test di scripts/orario.py: ora nel post, orari.yaml per giorno, valore predefinito."""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from orario import orario  # noqa: E402


def main() -> int:
    falliti = []
    with tempfile.TemporaryDirectory() as tmp:
        r = Path(tmp)
        (r / "programmati").mkdir()
        # 2026-11-09 è lunedì, 2026-11-10 martedì, 2026-11-11 mercoledì
        (r / "orari.yaml").write_text('lunedi: "12:00"\nmartedi: "08:30"  # mattina\nmercoledi: "25:99"\n')
        (r / "programmati" / "2026-11-10.md").write_text('---\ndate: 2026-11-10\nora: "17:15"\n---\ntesto con ora: 9:00\n')
        (r / "programmati" / "2026-11-09.md").write_text("---\ndate: 2026-11-09\n---\ntesto\n")
        casi = [
            ("2026-11-10", "17:15", "ora nel post vince"),
            ("2026-11-09", "12:00", "giorno da orari.yaml"),
            ("2026-11-11", "08:00", "orario non valido: predefinito"),
            ("2026-11-12", "08:00", "giorno mancante: predefinito"),
        ]
        for data, atteso, label in casi:
            ok = orario(data, r) == atteso
            print(f"  [{'OK ' if ok else 'FAIL'}] {label}")
            if not ok:
                falliti.append((label, atteso, orario(data, r)))
    reale = {d: orario(d) for d in ("2026-11-09", "2026-11-10")}
    print(f"  orari reali: {reale}")
    if falliti:
        print(f"\n{len(falliti)} test falliti: {falliti}")
        return 1
    print("Tutti i test passati.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
