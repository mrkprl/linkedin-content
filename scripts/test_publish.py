#!/usr/bin/env python3
"""Test dell'escaping little text. Esegui: python3 scripts/test_publish.py"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from publish import HASHTAG, escape_little_text, parse_post_file

CASES = [
    # (input, atteso, descrizione)
    ("mentre tu (dovresti) guardare", r"mentre tu \(dovresti\) guardare",
     "parentesi tonde — il bug del 2026-08-10"),
    ("#AI #ClaudeCode #Produttività", "#AI #ClaudeCode #Produttività",
     "hashtag validi restano intatti"),
    ("email marco@example.com", r"email marco\@example.com", "chiocciola"),
    ("array[0] e dict{k}", r"array\[0\] e dict\{k\}", "quadre e graffe"),
    ("a > b < c", r"a \> b \< c", "maggiore e minore"),
    ("path C:\\temp", "path C:\\\\temp", "backslash letterale raddoppiato"),
    ("*bold* _under_ ~tilde~", r"\*bold\* \_under\_ \~tilde\~", "asterisco underscore tilde"),
    ("a | b", r"a \| b", "pipe"),
    ("il 50% e 3,14", "il 50% e 3,14", "percentuale e virgola non toccate"),
    ("https://claude.com/blog/auto-mode", "https://claude.com/blog/auto-mode",
     "URL senza riservati resta intatto"),
    ('"virgolette" e accenti àèìòù', '"virgolette" e accenti àèìòù', "punteggiatura e accenti"),
    ("emoji 🤖 e newline\n\nparagrafo", "emoji 🤖 e newline\n\nparagrafo", "emoji e a capo"),
    ("testo (con) #tag insieme", r"testo \(con\) #tag insieme",
     "hashtag preservato mentre il resto viene escapato"),
]


RESERVED = r"|{}@[]()<>#*_~\\"


def validate(commentary: str) -> list:
    """Scorre il commentary come lo farebbe il parser little: ogni riservato deve
    essere preceduto da backslash, ogni backslash deve introdurne uno. Unica
    eccezione: #parola, che è un HashtagElement valido."""
    problems, i = [], 0
    while i < len(commentary):
        ch = commentary[i]
        if ch == "\\":
            if i + 1 >= len(commentary) or commentary[i + 1] not in RESERVED:
                problems.append(f"backslash che non escapa nulla in posizione {i}")
            i += 2
            continue
        if ch == "#":
            match = HASHTAG.match(commentary, i)
            if not match:
                problems.append(f"cancelletto nudo non seguito da una parola in posizione {i}")
            i = match.end() if match else i + 1
            continue
        if ch in RESERVED:
            problems.append(f"{ch!r} non escapato in posizione {i}: "
                            f"{commentary[max(0, i - 30):i + 20]!r}")
        i += 1
    return problems


def run():
    failures = []

    for text, expected, label in CASES:
        actual = escape_little_text(text)
        status = "OK " if actual == expected else "FAIL"
        if actual != expected:
            failures.append((label, expected, actual))
        print(f"  [{status}] {label}")

    # Idempotenza inversa: rimuovendo i backslash si torna al testo originale.
    for text, _, label in CASES:
        if escape_little_text(text).replace("\\", "") != text.replace("\\", ""):
            failures.append((f"round-trip: {label}", text, escape_little_text(text)))

    # Casi reali: ogni post nel repo deve produrre un commentary valido.
    repo = Path(__file__).parent.parent
    for folder in ("published", "approved", "pending", "archive", "examples"):
        for post in sorted((repo / folder).glob("*.md")):
            text = parse_post_file(str(post))["text"]
            problems = validate(escape_little_text(text))
            if len(text) > 3000:
                problems.append(f"{len(text)} caratteri, oltre il limite di 3000")
            print(f"  [{'OK ' if not problems else 'FAIL'}] "
                  f"{folder}/{post.name} — {len(text)} caratteri")
            for p in problems:
                failures.append((f"{folder}/{post.name}", "commentary valido", p))

    if failures:
        print(f"\n{len(failures)} test falliti:")
        for label, expected, actual in failures:
            print(f"  {label}\n    atteso:  {expected!r}\n    ottenuto: {actual!r}")
        return 1
    print("\nTutti i test passati.")
    return 0


if __name__ == "__main__":
    sys.exit(run())
