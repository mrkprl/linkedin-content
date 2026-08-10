#!/usr/bin/env python3
"""Misura la leggibilità di un post e i segnali di scrittura artificiosa.

Le soglie vengono dalle fonti citate in SETUP.md. Gulpease è la formula tarata
sull'italiano (Lucisano e Piemontese, 1988): usa le lettere invece delle sillabe,
quindi si calcola senza sillabazione.
"""

import re

PAROLA = re.compile(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ']+")
NON_ALFANUM = re.compile(r"[^0-9A-Za-zÀ-ÖØ-öø-ÿ]")
FINE_FRASE = re.compile(r"[.!?;:]+")

# Soglie: vedi SETUP.md per la fonte di ciascuna.
GULPEASE_MIN = 60          # sotto: non leggibile in autonomia con la licenza media
PAROLE_PER_FRASE_MAX = 25  # Direttiva 8/5/2002 regola 1; Cortelazzo regola 12
MEDIA_PAROLE_MAX = 18
HOOK_MAX_CHARS = 80        # la prima riga è anche lo slug dell'URL del post
CARATTERI_MIN = 1600       # target di scrittura 1800-2400, qui la banda di tolleranza
CARATTERI_MAX = 2600       # oltre i 3000 LinkedIn rifiuta il post

# Costrutti che fanno "suonare" il testo come generato da un modello.
STILEMI = [
    (re.compile(r"—"), "trattino lungo"),
    (re.compile(r"→"), "freccia"),
    (re.compile(r"\bnon (?:è |si tratta )?(?:solo|soltanto|più) (?:una |un |di )?\w+[,.]? ma\b", re.I),
     "costrutto 'non solo X ma Y'"),
    (re.compile(r"\bnon è (?:più )?(?:una )?questione di\b", re.I), "formula 'non è questione di'"),
    (re.compile(r"\bin un (?:mondo|'?epoca|era) in cui\b", re.I), "attacco 'in un mondo in cui'"),
    (re.compile(r"\bnell'era (?:dell|di)\w*\b", re.I), "attacco 'nell'era di'"),
    (re.compile(r"\bla vera domanda è\b", re.I), "formula 'la vera domanda è'"),
    (re.compile(r"\bnon è un caso che\b", re.I), "formula 'non è un caso che'"),
    (re.compile(r"\bed è qui che entra in gioco\b", re.I), "formula 'entra in gioco'"),
    (re.compile(r"\brappresenta un(?:a)? (?:vero|vera|svolta|punto)\b", re.I), "enfasi 'rappresenta una svolta'"),
    (re.compile(r"\bsi configura come\b|\bfunge da\b", re.I), "verbo gonfio al posto di 'è'"),
    (re.compile(r"\bnonostante (?:le difficoltà|tutto), \w+ continua\b", re.I), "chiusa formulaica"),
]


def gulpease(testo: str) -> float:
    """89 + (300*frasi - 10*lettere) / parole. Scala 0-100, 100 = più leggibile."""
    parole_lista = PAROLA.findall(testo)
    if not parole_lista:
        return 0.0
    lettere = sum(len(NON_ALFANUM.sub("", p)) for p in parole_lista)
    t = testo.strip()
    frasi = max(len(FINE_FRASE.findall(t)) + (0 if FINE_FRASE.search(t[-1:]) else 1), 1)
    return 89 + (300 * frasi - 10 * lettere) / len(parole_lista)


def analizza(testo: str) -> dict:
    righe = [r for r in testo.split("\n")]
    paragrafi = [r.strip() for r in righe if r.strip()]
    frasi = [f.strip() for f in re.split(r"[.!?;:\n]+", testo) if f.strip()]
    per_frase = [len(PAROLA.findall(f)) for f in frasi] or [0]

    return {
        "caratteri": len(testo),
        "parole": len(PAROLA.findall(testo)),
        "gulpease": round(gulpease(testo), 1),
        "paragrafi": len(paragrafi),
        "media_parole_frase": round(sum(per_frase) / len(per_frase), 1),
        "frase_piu_lunga": max(per_frase),
        "frasi_lunghe": [f for f, n in zip(frasi, per_frase) if n > PAROLE_PER_FRASE_MAX],
        "hook": righe[0].strip() if righe else "",
        "stilemi": [nome for pattern, nome in STILEMI if pattern.search(testo)],
    }


def problemi(testo: str) -> list:
    """Violazioni delle soglie. Lista vuota = il testo passa."""
    m = analizza(testo)
    out = []

    if m["gulpease"] < GULPEASE_MIN:
        out.append(f"Gulpease {m['gulpease']} sotto {GULPEASE_MIN}: "
                   f"non si legge in autonomia con la licenza media")
    if m["media_parole_frase"] > MEDIA_PAROLE_MAX:
        out.append(f"media di {m['media_parole_frase']} parole per frase, il massimo è {MEDIA_PAROLE_MAX}")
    for f in m["frasi_lunghe"]:
        out.append(f"frase da {len(PAROLA.findall(f))} parole (max {PAROLE_PER_FRASE_MAX}): «{f[:70]}...»")
    if not m["hook"]:
        out.append("prima riga vuota: è l'hook e diventa lo slug dell'URL")
    elif len(m["hook"]) > HOOK_MAX_CHARS:
        out.append(f"hook di {len(m['hook'])} caratteri, il massimo è {HOOK_MAX_CHARS}")
    if m["hook"].startswith("#"):
        out.append("l'hook inizia con un hashtag: genera uno slug URL generico")
    if not (CARATTERI_MIN <= m["caratteri"] <= CARATTERI_MAX):
        out.append(f"{m['caratteri']} caratteri, fuori dalla fascia {CARATTERI_MIN}-{CARATTERI_MAX}")
    if m["paragrafi"] < 12:
        out.append(f"solo {m['paragrafi']} paragrafi: servono blocchi corti, almeno 12")
    if "http://" in testo or "https://" in testo:
        out.append("link nel corpo del post: costa circa il 27% di impression, va nel commento")
    for s in m["stilemi"]:
        out.append(f"stilema da testo generato: {s}")
    return out


def main():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from publish import parse_post_file

    for percorso in sys.argv[1:]:
        testo = parse_post_file(percorso)["text"]
        m = analizza(testo)
        print(f"\n{percorso}")
        print(f"  {m['caratteri']} caratteri · {m['parole']} parole · {m['paragrafi']} paragrafi")
        print(f"  Gulpease {m['gulpease']} · {m['media_parole_frase']} parole/frase "
              f"· frase più lunga {m['frase_piu_lunga']}")
        print(f"  hook ({len(m['hook'])} car.): {m['hook'][:80]}")
        for p in problemi(testo):
            print(f"  ! {p}")


if __name__ == "__main__":
    main()
