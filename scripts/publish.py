#!/usr/bin/env python3
"""
Pubblica i post approvati su LinkedIn.
Secrets necessari:
  - LINKEDIN_ACCESS_TOKEN (obbligatorio)
  - LINKEDIN_PERSON_ID    (opzionale — se non impostato viene recuperato via API)
"""

import os
import sys
import re
import requests
import yaml

LINKEDIN_POSTS_API = "https://api.linkedin.com/rest/posts"
LINKEDIN_USERINFO_API = "https://api.linkedin.com/v2/userinfo"
LINKEDIN_VERSION = "202411"

ACCESS_TOKEN = os.environ.get("LINKEDIN_ACCESS_TOKEN")
PERSON_ID_OVERRIDE = os.environ.get("LINKEDIN_PERSON_ID", "").strip()
NEW_FILES = os.environ.get("NEW_FILES", "").split()


def get_person_id(access_token: str) -> str:
    """Recupera il person ID via /v2/userinfo (richiede scope openid+profile)."""
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(LINKEDIN_USERINFO_API, headers=headers, timeout=15)
    if response.status_code != 200:
        raise RuntimeError(
            f"API userinfo fallita ({response.status_code}): {response.text}\n"
            "→ Aggiungi il secret LINKEDIN_PERSON_ID con il tuo person ID numerico,\n"
            "  oppure rigenera il token con scope: openid profile w_member_social"
        )
    return response.json()["sub"]


def parse_post_file(filepath: str) -> dict:
    """Estrae frontmatter e testo del post da un file .md."""
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

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
    response = requests.post(LINKEDIN_POSTS_API, headers=headers, json=payload, timeout=30)
    if response.status_code not in (200, 201):
        raise RuntimeError(f"LinkedIn API error {response.status_code}: {response.text}")
    return response.headers.get("x-restli-id", "unknown")


def main():
    if not ACCESS_TOKEN:
        print("ERROR: LINKEDIN_ACCESS_TOKEN non impostato")
        sys.exit(1)
    if not NEW_FILES or NEW_FILES == [""]:
        print("Nessun file nuovo da pubblicare.")
        return

    # Recupera person ID: prima dal secret, poi dall'API
    if PERSON_ID_OVERRIDE:
        person_id = PERSON_ID_OVERRIDE
        print(f"→ Person ID da secret: {person_id}")
    else:
        print("→ Recupero person ID dal token...")
        try:
            person_id = get_person_id(ACCESS_TOKEN)
            print(f"  ✓ Person ID: {person_id}")
        except RuntimeError as e:
            print(f"  ✗ {e}")
            sys.exit(1)

    errors = []
    for filepath in NEW_FILES:
        filepath = filepath.strip()
        if not filepath or not filepath.endswith(".md"):
            continue
        print(f"\n→ Processo: {filepath}")
        try:
            post = parse_post_file(filepath)
            post_id = publish_post(post["text"], person_id, ACCESS_TOKEN)
            print(f"  ✓ Pubblicato — LinkedIn post ID: {post_id}")
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
