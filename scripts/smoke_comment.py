#!/usr/bin/env python3
"""Verifica che il token possa commentare, senza lasciare traccia.

Crea un commento su un post esistente e lo cancella subito. Serve a sapere se il
token ha lo scope w_member_social_feed, che è diverso da quello usato per pubblicare.

Uso:  POST_URN=urn:li:share:123 python scripts/smoke_comment.py
"""

import os
import sys
from urllib.parse import quote

import requests

from publish import (
    ACCESS_TOKEN,
    LINKEDIN_SOCIAL_ACTIONS_API,
    LINKEDIN_VERSION,
    PERSON_ID_OVERRIDE,
    get_person_id,
    publish_comment,
)


def main():
    post_urn = os.environ.get("POST_URN", "").strip()
    if not ACCESS_TOKEN or not post_urn:
        print("Servono LINKEDIN_ACCESS_TOKEN e POST_URN")
        return 1

    person_id = PERSON_ID_OVERRIDE or get_person_id(ACCESS_TOKEN)
    print(f"→ Provo a commentare {post_urn}")

    try:
        comment_id = publish_comment("test", post_urn, person_id, ACCESS_TOKEN)
    except RuntimeError as e:
        print(f"  ✗ Commento NON permesso: {e}")
        print("\n  Il token va rigenerato aggiungendo lo scope w_member_social_feed.")
        print("  Finché non lo fai, i post escono senza le fonti nel primo commento.")
        return 1

    print(f"  ✓ Commento creato: {comment_id}")

    response = requests.delete(
        f"{LINKEDIN_SOCIAL_ACTIONS_API}/{quote(post_urn, safe='')}/comments/{comment_id}",
        headers={
            "Authorization": f"Bearer {ACCESS_TOKEN}",
            "LinkedIn-Version": LINKEDIN_VERSION,
            "X-Restli-Protocol-Version": "2.0.0",
        },
        params={"actor": f"urn:li:person:{person_id}"},
        timeout=30,
    )
    if response.status_code in (200, 204):
        print("  ✓ Commento di prova cancellato")
    else:
        print(f"  ! Commento NON cancellato ({response.status_code}): {response.text}")
        print(f"    Cancellalo a mano dal post.")
        return 1

    print("\nLo scope funziona: le fonti finiranno nel primo commento.")
    return 0


if __name__ == "__main__":
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    sys.exit(main())
