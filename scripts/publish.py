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
import time
from pathlib import Path
from urllib.parse import quote

import requests
import yaml

LINKEDIN_POSTS_API = "https://api.linkedin.com/rest/posts"
LINKEDIN_IMAGES_API = "https://api.linkedin.com/rest/images?action=initializeUpload"
LINKEDIN_DOCUMENTS_API = "https://api.linkedin.com/rest/documents?action=initializeUpload"
LINKEDIN_USERINFO_API = "https://api.linkedin.com/v2/userinfo"
LINKEDIN_SOCIAL_ACTIONS_API = "https://api.linkedin.com/rest/socialActions"
LINKEDIN_SOCIAL_ACTIONS_V2 = "https://api.linkedin.com/v2/socialActions"
LINKEDIN_VERSION = "202607"
COMMENTARY_MAX_CHARS = 3000

# Il campo commentary usa il formato "little text": i caratteri riservati vanno
# escapati con backslash, altrimenti il parser tronca il post al primo carattere
# non atteso (es. "(" viene letto come inizio della URN di una mention).
LITTLE_RESERVED = re.compile(r"([\\|{}@\[\]()<>#*_~])")
# Un hashtag valido (#parola) è un elemento supportato e va lasciato intatto.
HASHTAG = re.compile(r"(?<![\w#])#(\w+)", re.UNICODE)
PLACEHOLDER = re.compile(r"\x00HT(\d+)\x00")

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


def escape_little_text(text: str) -> str:
    """Escapa i caratteri riservati del formato little, preservando gli hashtag."""
    stashed = []

    def stash(match):
        stashed.append(match.group(1))
        return f"\x00HT{len(stashed) - 1}\x00"

    escaped = LITTLE_RESERVED.sub(r"\\\1", HASHTAG.sub(stash, text))
    return PLACEHOLDER.sub(lambda m: "#" + stashed[int(m.group(1))], escaped)


class ErroreLinkedIn(RuntimeError):
    """Errore di un caricamento, con il codice HTTP: serve a capire se riprovare
    o ripiegare (403 = il token non ha il permesso)."""

    def __init__(self, messaggio: str, status: int = None):
        super().__init__(messaggio)
        self.status = status


def _carica(api: str, chiave: str, nome: str, percorso, person_id: str, access_token: str) -> str:
    """initializeUpload dà l'indirizzo di caricamento e la URN, poi il file va
    mandato con un PUT. Vale per le immagini e per i documenti (i caroselli PDF)."""
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {"initializeUploadRequest": {"owner": f"urn:li:person:{person_id}"}}
    response = requests.post(api, headers=headers, json=payload, timeout=30)
    if response.status_code != 200:
        raise ErroreLinkedIn(
            f"initializeUpload {nome} fallito {response.status_code}: {response.text}",
            response.status_code)
    value = response.json()["value"]

    with open(percorso, "rb") as f:
        dati = f.read()
    response = requests.put(
        value["uploadUrl"],
        headers={"Authorization": f"Bearer {access_token}"},
        data=dati,
        timeout=120,
    )
    if response.status_code not in (200, 201):
        raise ErroreLinkedIn(
            f"caricamento {nome} fallito {response.status_code}: {response.text}",
            response.status_code)
    return value[chiave]


def upload_image(png_path, person_id: str, access_token: str) -> str:
    """Carica un'immagine con la Images API e restituisce la sua URN.

    Con il solo scope w_member_social non si può leggere lo stato dell'immagine
    (la GET su /rest/images è negata), quindi se il post parte mentre LinkedIn la
    sta ancora elaborando lo si riprova in publish_post."""
    return _carica(LINKEDIN_IMAGES_API, "image", "immagine", png_path, person_id, access_token)


def upload_document(pdf_path, person_id: str, access_token: str) -> str:
    """Carica il PDF del carosello con la Documents API e restituisce la sua URN.

    LinkedIn elabora i documenti in modo asincrono (il caricamento sincrono non
    esiste per i documenti): il post si riprova finché il documento è pronto."""
    return _carica(LINKEDIN_DOCUMENTS_API, "document", "documento", pdf_path, person_id,
                   access_token)


def publish_post(text: str, person_id: str, access_token: str, image: dict = None,
                 tentativi: int = 3, attesa: float = 5.0) -> str:
    """Invia il post a LinkedIn API. Restituisce l'ID del post creato.

    image è il blocco media, se c'è: {"id": "urn:li:image:...", "altText": "..."}
    per un'immagine, {"id": "urn:li:document:...", "title": "..."} per un carosello."""
    if len(text) > COMMENTARY_MAX_CHARS:
        raise ValueError(
            f"Testo troppo lungo: {len(text)} caratteri, il massimo è {COMMENTARY_MAX_CHARS}"
        )
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
        "LinkedIn-Version": LINKEDIN_VERSION,
        "X-Restli-Protocol-Version": "2.0.0",
    }
    payload = {
        "author": f"urn:li:person:{person_id}",
        "commentary": escape_little_text(text),
        "visibility": "PUBLIC",
        "distribution": {
            "feedDistribution": "MAIN_FEED",
            "targetEntities": [],
            "thirdPartyDistributionChannels": [],
        },
        "lifecycleState": "PUBLISHED",
        "isReshareDisabledByAuthor": False,
    }
    if image:
        payload["content"] = {"media": dict(image)}
    # Senza immagine un errore è definitivo. Con un'immagine o un documento può
    # voler dire che LinkedIn lo sta ancora elaborando: un rifiuto non crea il
    # post, quindi riprovare non rischia doppioni.
    for tentativo in range(1, (tentativi if image else 1) + 1):
        response = requests.post(LINKEDIN_POSTS_API, headers=headers, json=payload, timeout=30)
        if response.status_code in (200, 201):
            return response.headers.get("x-restli-id", "unknown")
        if tentativo < (tentativi if image else 1):
            print(f"  … post rifiutato ({response.status_code}), riprovo fra {attesa:.0f} s")
            time.sleep(attesa)
    raise RuntimeError(f"LinkedIn API error {response.status_code}: {response.text}")


def source_comment(meta: dict) -> str:
    """Testo del primo commento: le fonti stanno qui, non nel post.
    Un link nel corpo costa circa il 27% di impression sui profili personali."""
    if meta.get("comment"):
        return str(meta["comment"]).strip()
    sources = meta.get("sources") or []
    if not sources:
        return ""
    righe = ["Fonte:" if len(sources) == 1 else "Fonti:"]
    righe += [str(s).strip() for s in sources if str(s).strip()]
    return "\n".join(righe)


def publish_comment(text: str, post_urn: str, person_id: str, access_token: str) -> str:
    """Commenta un post appena pubblicato. Il campo message.text è testo semplice:
    NON usa il formato little, quindi qui non va applicato nessun escaping.

    L'endpoint versionato /rest/socialActions è riservato ai partner e risponde 403
    (partnerApiSocialActions) con un'app standard, quindi si parte dal /v2 legacy,
    che rientra nello scope w_member_social."""
    encoded = quote(post_urn, safe="")
    payload = {
        "actor": f"urn:li:person:{person_id}",
        "object": post_urn,
        "message": {"text": text},
    }
    errori = []
    for base, versionato in ((LINKEDIN_SOCIAL_ACTIONS_V2, False),
                             (LINKEDIN_SOCIAL_ACTIONS_API, True)):
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
            "X-Restli-Protocol-Version": "2.0.0",
        }
        if versionato:
            headers["LinkedIn-Version"] = LINKEDIN_VERSION
        response = requests.post(
            f"{base}/{encoded}/comments", headers=headers, json=payload, timeout=30
        )
        if response.status_code in (200, 201):
            return response.headers.get("x-restli-id", "unknown")
        errori.append(f"{base}: {response.status_code} {response.text[:200]}")
    raise RuntimeError("LinkedIn API error — " + " | ".join(errori))


def prepare_image(filepath: str, meta: dict, person_id: str, warnings: list):
    """Ridisegna l'infografica dal frontmatter e la carica. Restituisce il blocco
    media per il post, oppure None se il post non ha un'immagine.

    Si ridisegna sempre, anche se il PNG è già nel repo: se Marco corregge il
    blocco immagine nella PR, esce l'immagine corretta e non l'anteprima vecchia.
    Un blocco sbagliato era già segnalato nella PR, che Marco ha approvato
    comunque: si pubblica il testo da solo. Un errore di LinkedIn invece blocca
    il post, così si può rilanciare il workflow."""
    if "immagine" not in (meta or {}):
        return None
    from render_image import ErroreImmagine, disegna, percorso_immagine

    try:
        img = disegna(meta["immagine"])
    except ErroreImmagine as e:
        warnings.append(filepath)
        print(f"  ! Immagine non valida ({e}): pubblico solo il testo")
        return None
    png = percorso_immagine(Path(filepath))
    png.parent.mkdir(parents=True, exist_ok=True)
    img.save(png, "PNG", optimize=True)
    urn = upload_image(png, person_id, ACCESS_TOKEN)
    print(f"  ✓ Immagine caricata: {urn}")
    return {"id": urn, "altText": str(meta["immagine"]["alt"]).strip()}


def prepare_carousel(filepath: str, meta: dict, person_id: str, warnings: list):
    """Ridisegna il carosello dal frontmatter, con l'illustrazione già salvata nella
    PR (non la rigenera: esce quella che Marco ha visto), e carica il PDF.

    Restituisce il blocco media e le opzioni per publish_post. Un blocco sbagliato
    era già segnalato nella PR: si pubblica il solo testo. Se LinkedIn rifiuta i
    documenti per un problema di permessi (401/403), esce la sola copertina come
    immagine; qualunque altro errore blocca il post, così si può rilanciare."""
    from render_carousel import (ErroreImmagine, disegna_carosello, percorso_illustrazione,
                                 percorso_pdf, salva_pdf, testo_semplice)

    post = Path(filepath)
    carosello = meta["carosello"]
    try:
        pagine = disegna_carosello(carosello, percorso_illustrazione(post))
    except ErroreImmagine as e:
        warnings.append(filepath)
        print(f"  ! Carosello non valido ({e}): pubblico solo il testo")
        return None, {}
    pdf = percorso_pdf(post)
    salva_pdf(pagine, pdf)
    titolo = testo_semplice(carosello["copertina"]["titolo"])
    try:
        urn = upload_document(pdf, person_id, ACCESS_TOKEN)
    except ErroreLinkedIn as e:
        if e.status not in (401, 403):
            raise
        warnings.append(filepath)
        print(f"  ! LinkedIn non accetta il documento ({e}): pubblico la sola copertina")
        png = pdf.with_suffix(".png")
        pagine[0].save(png, "PNG", optimize=True)
        urn = upload_image(png, person_id, ACCESS_TOKEN)
        return {"id": urn, "altText": str(carosello["alt"]).strip()}, {}
    print(f"  ✓ Carosello caricato: {urn} ({len(pagine)} pagine)")
    # I documenti ci mettono più delle immagini a essere pronti.
    return {"id": urn, "title": titolo}, {"tentativi": 8, "attesa": 10.0}


def prepare_media(filepath: str, meta: dict, person_id: str, warnings: list):
    """Carosello se il post ne ha uno, altrimenti l'infografica singola dei post
    precedenti, altrimenti niente."""
    if "carosello" in (meta or {}):
        return prepare_carousel(filepath, meta, person_id, warnings)
    return prepare_image(filepath, meta, person_id, warnings), {}


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

    errors, warnings = [], []
    for filepath in NEW_FILES:
        filepath = filepath.strip()
        if not filepath or not filepath.endswith(".md"):
            continue
        print(f"\n→ Processo: {filepath}")
        try:
            post = parse_post_file(filepath)
            media, opzioni = prepare_media(filepath, post["meta"], person_id, warnings)
            post_id = publish_post(post["text"], person_id, ACCESS_TOKEN, media, **opzioni)
            print(f"  ✓ Pubblicato — LinkedIn post ID: {post_id}")
            print(f"  Topic: {post['meta'].get('topic', 'N/A')}")

            # Il commento con le fonti è un extra: se fallisce il post resta online,
            # quindi va segnalato senza far fallire la pubblicazione.
            commento = source_comment(post["meta"])
            if commento:
                try:
                    comment_id = publish_comment(commento, post_id, person_id, ACCESS_TOKEN)
                    print(f"  ✓ Fonti nel primo commento — ID: {comment_id}")
                except Exception as e:
                    warnings.append(filepath)
                    print(f"  ! Post pubblicato ma commento fallito: {e}")
                    print("    → Aggiungi il commento a mano; se l'errore è 403, il token")
                    print("      va rigenerato includendo lo scope w_member_social_feed.")
        except Exception as e:
            print(f"  ✗ Errore: {e}")
            errors.append(filepath)

    if errors:
        print(f"\nFalliti: {errors}")
        sys.exit(1)
    if warnings:
        print(f"\nPubblicati con un avviso (commento, immagine o carosello mancante): {warnings}")
    print("\nDone.")


if __name__ == "__main__":
    main()
