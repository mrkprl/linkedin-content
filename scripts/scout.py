#!/usr/bin/env python3
"""Raccoglie gli spunti per il post: le idee di Marco in IDEE.md, poi le uscite
recenti delle fonti in fonti.yaml. Stampa solo, non decide niente.

Uso: python scripts/scout.py [giorni]   (default 7)
"""

import html
import json
import re
import sys
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

import yaml

RADICE = Path(__file__).resolve().parent.parent
# Reddit risponde vuoto agli user agent generici: vuole un nome descrittivo.
USER_AGENT = "linux:linkedin-content-scout:v1.0 (by /u/mrkprl)"
PER_FONTE = 8
ATOM = "{http://www.w3.org/2005/Atom}"
TAG = re.compile(r"<[^>]+>")


def scarica(url: str) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as r:
        return r.read()


def pulisci(testo: str, n: int) -> str:
    testo = html.unescape(TAG.sub(" ", html.unescape(testo or "")))
    testo = re.sub(r"\s+", " ", testo).strip()
    return testo if len(testo) <= n else testo[:n].rsplit(" ", 1)[0] + "…"


def data(testo: str):
    if not testo:
        return None
    testo = testo.strip()
    try:
        d = parsedate_to_datetime(testo)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(testo.replace("Z", "+00:00"))
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def testo_di(nodo, *nomi):
    for nome in nomi:
        trovato = nodo.find(nome)
        if trovato is not None:
            return trovato.text or trovato.get("href") or ""
    return ""


def leggi_feed(url: str) -> list:
    radice = ET.fromstring(scarica(url))
    voci = []
    for it in radice.iter("item"):
        voci.append({
            "titolo": testo_di(it, "title"),
            "link": testo_di(it, "link"),
            "data": data(testo_di(it, "pubDate", "{http://purl.org/dc/elements/1.1/}date")),
            "testo": testo_di(it, "description"),
        })
    for e in radice.iter(f"{ATOM}entry"):
        link = e.find(f"{ATOM}link")
        voci.append({
            "titolo": testo_di(e, f"{ATOM}title"),
            "link": link.get("href", "") if link is not None else "",
            "data": data(testo_di(e, f"{ATOM}published", f"{ATOM}updated")),
            "testo": testo_di(e, f"{ATOM}summary", f"{ATOM}content",
                              "{http://search.yahoo.com/mrss/}group/{http://search.yahoo.com/mrss/}description"),
        })
    return voci


def leggi_hn(parola: str, dal: datetime) -> list:
    filtri = f"created_at_i>{int(dal.timestamp())},points>50"
    url = ("https://hn.algolia.com/api/v1/search?tags=story&query="
           f"{urllib.parse.quote(parola)}&numericFilters={urllib.parse.quote(filtri)}")
    risultati = json.loads(scarica(url))["hits"]
    return [{
        "titolo": f"{h['title']} ({h['points']} punti)",
        "link": h.get("url") or f"https://news.ycombinator.com/item?id={h['objectID']}",
        "data": data(h["created_at"]),
        "testo": "",
    } for h in risultati]


def idee_gia_usate() -> set:
    usate = set()
    for cartella in ("approved", "published", "archive"):
        for post in (RADICE / cartella).glob("*.md"):
            m = re.search(r"^idea:\s*(.+)$", post.read_text(encoding="utf-8"), re.M)
            if m:
                usate.add(normalizza(yaml.safe_load(m.group(1)) or ""))
    return usate


def normalizza(riga: str) -> str:
    return re.sub(r"\s+", " ", str(riga).lstrip("-* ").strip()).lower()


def idee_da_usare() -> str:
    percorso = RADICE / "IDEE.md"
    if not percorso.exists():
        return ""
    blocco = re.search(r"^## Da usare\s*\n(.*?)(?=^## |\Z)", percorso.read_text(encoding="utf-8"),
                       re.M | re.S)
    usate = idee_gia_usate()
    righe = [r for r in (blocco.group(1) if blocco else "").splitlines()
             if r.strip() and not r.lstrip().startswith("<!--") and normalizza(r) not in usate]
    return "\n".join(righe)


def main() -> int:
    giorni = int(sys.argv[1]) if len(sys.argv) > 1 else 12
    dal = datetime.now(timezone.utc) - timedelta(days=giorni)
    fonti = yaml.safe_load((RADICE / "fonti.yaml").read_text(encoding="utf-8"))

    print("# IDEE.md, sezione Da usare (hanno la precedenza)\n")
    print(idee_da_usare() or "(vuota)")

    da_leggere = []
    for ruolo in ("ufficiale", "stampa", "spunto"):
        print(f"\n\n# Fonti: {ruolo}")
        for f in (f for f in fonti if f["ruolo"] == ruolo):
            if f["tipo"] == "pagina":
                da_leggere.append(f)
                continue
            print(f"\n## {f['nome']}")
            try:
                voci = leggi_hn(f["url"], dal) if f["tipo"] == "hn" else leggi_feed(f["url"])
            except Exception as e:  # una fonte giù non deve fermare le altre
                print(f"  non raggiungibile: {type(e).__name__}: {str(e)[:120]}")
                continue
            recenti = [v for v in voci if v["data"] is None or v["data"] >= dal]
            recenti.sort(key=lambda v: v["data"] or dal, reverse=True)
            if not recenti:
                print(f"  niente negli ultimi {giorni} giorni")
            for v in recenti[:PER_FONTE]:
                quando = v["data"].strftime("%Y-%m-%d") if v["data"] else "senza data"
                print(f"- {quando} | {pulisci(v['titolo'], 140)}\n  {v['link']}")
                riassunto = pulisci(v["testo"], 220)
                if riassunto:
                    print(f"  {riassunto}")
            time.sleep(0.5)

    print("\n\n# Pagine senza feed: leggile con WebFetch")
    for f in da_leggere:
        print(f"- [{f['ruolo']}] {f['nome']}: {f['url']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
