#!/usr/bin/env python3
"""Chiede a OpenAI (la generazione immagini di ChatGPT) le illustrazioni del carosello.

Uso:
    python scripts/illustrazione.py approved/2026-10-24.md
    python scripts/illustrazione.py approved/2026-10-24.md --forza

Per ogni scena del blocco `carosello:` (la copertina e le slide di testo con il
campo `illustrazione`, scritte dalla routine) mette la scena dentro un prompt di
stile fisso e salva l'immagine in images/<data>/: illustrazione.jpg per la
copertina, illustrazione-NN.jpg per la pagina NN. Accanto a ogni immagine salva
un .txt con il prompt usato: se il prompt non cambia, lo script non richiama
l'API, così un secondo push sullo stesso branch non paga le immagini due volte.
Se Marco corregge una scena nella PR, si rifà solo quella.

Serve la variabile OPENAI_API_KEY (nella Action è il secret con lo stesso nome).
Senza chiave, o se l'API risponde con un errore, lo script lo dice ed esce con 0:
quella pagina esce con il solo testo e il post parte lo stesso.

Il personaggio: nei post sugli agenti il blocco ha `personaggio: true`. Allora ogni
scena ha dentro il fattorino, il robottino scelto da Marco il 2026-10-23, e per
tenerlo uguale da un'immagine all'altra lo script manda a OpenAI anche
assets/personaggio.jpg come riferimento (endpoint delle modifiche, /images/edits).
Se quella chiamata fallisce riprova senza riferimento, con la sola descrizione.

Variabili facoltative:
    OPENAI_IMAGE_MODEL    default gpt-image-2.5-flare
    OPENAI_IMAGE_QUALITY  default medium (low, medium, high, xhigh, max, auto)
"""

import argparse
import base64
import io
import os
import sys
from pathlib import Path

import requests
from PIL import Image

sys.path.insert(0, str(Path(__file__).parent))
from publish import parse_post_file  # noqa: E402
from render_carousel import percorso_illustrazione, scene  # noqa: E402

API = "https://api.openai.com/v1/images/generations"
API_MODIFICHE = "https://api.openai.com/v1/images/edits"
RIFERIMENTO = Path(__file__).resolve().parent.parent / "assets" / "personaggio.jpg"
MODELLO_DEFAULT = "gpt-image-2.5-flare"
QUALITA_DEFAULT = "medium"
# Orizzontale: i riquadri del carosello sono più larghi che alti, e il taglio al
# centro perde poco.
DIMENSIONE = "1536x1024"

STILE = (
    "Editorial illustration for a LinkedIn carousel about AI news.\n"
    "Scene (described in Italian): {scena}\n\n"
    "Style: clean flat vector look, confident black outlines, simple shapes, soft "
    "shading. Warm ivory background (#F4F2EC). Main accent terracotta (#D97757), with "
    "kraft beige (#D4B28C), cream (#FBF8F3), muted sage green and near-black ink "
    "(#141413). Draw the objects of the scene, not abstract decorations.\n"
    "Composition: landscape, the subject centered with generous empty margins, nothing "
    "important near the edges because the image will be cropped.\n"
    "Strictly no text: no letters, words, numbers, labels or readable screens. No logos, "
    "brand marks or real products. No recognizable people: if people are needed, show "
    "only hands or figures seen from behind, without faces."
)


PERSONAGGIO = (
    "\n\nRecurring character: the scene features \"il fattorino\", the mascot of this "
    "series. Draw it exactly as in the reference image: a small friendly robot with a "
    "rounded sage-green body and limbs, a big round head with a round ear disc on the "
    "side, a white oval face visor with two small black oval eyes and no mouth, a "
    "terracotta baseball cap and charcoal feet; when it fits the scene it carries a "
    "kraft-brown messenger bag with blank envelopes. Same proportions, colors and line "
    "style in every image. It is the only character in the scene."
)


def prompt_per(scena: str, personaggio: bool = False) -> str:
    prompt = STILE.format(scena=" ".join(str(scena).split()))
    return prompt + PERSONAGGIO if personaggio else prompt


def con_personaggio(post: Path) -> bool:
    meta = parse_post_file(str(post))["meta"] or {}
    carosello = meta.get("carosello")
    return isinstance(carosello, dict) and carosello.get("personaggio") is True


def scene_del_post(post: Path) -> dict:
    meta = parse_post_file(str(post))["meta"] or {}
    return scene(meta.get("carosello"))


def messaggio_errore(response) -> str:
    try:
        return response.json()["error"]["message"]
    except (ValueError, KeyError, TypeError):
        return response.text[:300]


def _chiedi(url: str, payload: dict, chiave: str):
    headers = {"Authorization": f"Bearer {chiave}", "Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, timeout=300)


def _una(post: Path, pagina: int, scena: str, chiave: str, forza: bool,
         personaggio: bool = False) -> Path:
    """Disegna l'illustrazione di una pagina. Restituisce il file, o None se non c'è."""
    nome = "copertina" if pagina == 1 else f"pagina {pagina}"
    prompt = prompt_per(scena, personaggio)
    destinazione = percorso_illustrazione(post, pagina)
    file_prompt = destinazione.with_suffix(".txt")
    esiste = destinazione.exists()
    if esiste and not forza and file_prompt.exists() \
            and file_prompt.read_text(encoding="utf-8").strip() == prompt.strip():
        print(f"  OK: {nome}, già disegnata con questo prompt")
        return destinazione
    if not chiave:
        print(f"  ? {nome}: OPENAI_API_KEY non impostata, "
              + ("tengo l'illustrazione di prima" if esiste else "esce con il solo testo"))
        return destinazione if esiste else None

    modello = os.environ.get("OPENAI_IMAGE_MODEL", "").strip() or MODELLO_DEFAULT
    qualita = os.environ.get("OPENAI_IMAGE_QUALITY", "").strip() or QUALITA_DEFAULT
    payload = {
        "model": modello,
        "prompt": prompt,
        "size": DIMENSIONE,
        "quality": qualita,
        "background": "opaque",
        "output_format": "jpeg",
        "output_compression": 88,
        "n": 1,
    }
    response, con_riferimento = None, False
    if personaggio and RIFERIMENTO.is_file():
        # Con l'immagine di riferimento il fattorino resta uguale da un post all'altro.
        dati_rif = base64.b64encode(RIFERIMENTO.read_bytes()).decode()
        con_rif = {**payload,
                   "images": [{"image_url": f"data:image/jpeg;base64,{dati_rif}"}]}
        try:
            response = _chiedi(API_MODIFICHE, con_rif, chiave)
        except requests.RequestException as e:
            print(f"  ~ {nome}: riferimento del personaggio non accettato ({e}), "
                  "riprovo con la sola descrizione")
            response = None
        if response is not None and response.status_code != 200:
            print(f"  ~ {nome}: riferimento del personaggio non accettato "
                  f"({response.status_code}: {messaggio_errore(response)}), "
                  "riprovo con la sola descrizione")
            response = None
        con_riferimento = response is not None
    if response is None:
        try:
            response = _chiedi(API, payload, chiave)
        except requests.RequestException as e:
            print(f"  ! {nome}: OpenAI non risponde ({e})")
            return destinazione if esiste else None
    if response.status_code != 200:
        print(f"  ! {nome}: OpenAI ha risposto {response.status_code}: {messaggio_errore(response)}")
        return destinazione if esiste else None
    try:
        dati = base64.b64decode(response.json()["data"][0]["b64_json"])
        Image.open(io.BytesIO(dati)).verify()
    except Exception as e:  # noqa: BLE001
        print(f"  ! {nome}: risposta di OpenAI senza un'immagine valida ({e})")
        return destinazione if esiste else None

    destinazione.parent.mkdir(parents=True, exist_ok=True)
    destinazione.write_bytes(dati)
    file_prompt.write_text(prompt + "\n", encoding="utf-8")
    via = " con il riferimento del fattorino" if con_riferimento else ""
    print(f"  OK: {nome} salvata in {destinazione} ({modello}, qualità {qualita}{via})")
    return destinazione


def genera(post: Path, forza: bool = False, chiave: str = None) -> dict:
    """Disegna le illustrazioni che mancano. Restituisce {pagina: file o None}."""
    da_fare = scene_del_post(post)
    if not da_fare:
        print(f"{post}: nessuna illustrazione da disegnare")
        return {}
    chiave = (os.environ.get("OPENAI_API_KEY", "") if chiave is None else chiave).strip()
    personaggio = con_personaggio(post)
    print(f"{post}{' (con il fattorino)' if personaggio else ''}")
    return {pagina: _una(post, pagina, scena, chiave, forza, personaggio)
            for pagina, scena in da_fare.items()}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("post", help="file del post, es. approved/2026-10-24.md")
    parser.add_argument("--forza", action="store_true",
                        help="rifà le illustrazioni anche se il prompt non è cambiato")
    args = parser.parse_args(argv)
    genera(Path(args.post), forza=args.forza)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
