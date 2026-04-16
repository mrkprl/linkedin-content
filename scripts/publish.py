#!/usr/bin/env python3
"""
Pubblica i post approvati su LinkedIn.
Legge i file .md da approved/, esegue il post via LinkedIn API v2, 
poi il workflow sposta i file in published/.
"""

import os
import sys
import re
import json
import requests
import yaml

LINKEDIN_API = "https://api.linkedin.com/rest/posts"
LINKEDIN_VERSION = "202411"

ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
PERSON_ID = os.environ.get("LINKEDIN_PERSON_ID")
NEW_FILES = os.environ.get("NEW_FILES", "").split()


def parse_post_file(filepath: str) -> dict:
    """Estrae frontmatter e testo del post da un file .md."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    # Separa frontmatter (---...---) dal testo
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.+)", content, re.DOTALL)
    if not match:
        raise ValueError(f"Formato non valido in {filepath} — manca il frontmatter ---")

    frontmatter = yaml.safe_load(match.group(1))
    post_text = match.group(2).strip()

    return {"meta": frontmatter, "text": post_text}


def publish_post(text: str, person_id: str, access_token: str) -> str:
    """Invia il post a LinkedIn API. Restituisce l'ID del post creato."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }

    payload = {
        "author": f"urn:li:person:{person_id}",
        "commentary": text,
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }

    response = requests.post(LINKEDIN_API, headers=headers, json=payload, timeout=30)

    if response.status_code not in (200, 201):
        raise RuntimeError(
            f"LinkedIn API error {response.status_code}: {response.text}"
        )

    post_id = response.headers.get("x-restli-id", "unknown")
    return post_id


def main():
    if not ACCESS_TOKEN:
        print("ERROR: LINKEDIN_ACCESS_TOKEN non impostato")
        sys.exit(1)
    if not PERSON_ID:
        print("ERROR: LINKEDIN_PERSON_ID non impostato")
        sys.exit(1)
    if not NEW_FILES:
        print("Nessun file nuovo da pubblicare.")
        return

    errors = []
    for filepath in NEW_FILES:
        filepath = filepath.strip()
        if not filepath or not filepath.endswith(".md"):
            continue

        print(f"\n→ Processo: {filepath}")
        try:
            post = parse_post_file(filepath)
            post_id = publish_post(post["text"], PERSON_ID, ACCESS_TOKEN)
            print(f"  ✓ Pubblicato su LinkedIn — ID: {post_id}")
            print(f"  Topic: {post['meta'].get('topic', 'N/A')}")
        except Exception as e:
            print(f"  ✗ Errore: {e}")
            errors.append(filepath)

    if errors:
        print(f"\nFalliti: {errors}")
        sys.exit(1)

    print("\nDone.")


if __name__ == "__main__":
    main()
