#!/usr/bin/env python3
"""Disegna il carosello di un post a partire dal blocco `carosello:` del frontmatter.

Uso:
    python scripts/render_carousel.py approved/2026-10-24.md
    python scripts/render_carousel.py approved/2026-10-24.md --pdf /tmp/prova.pdf

Scrive:
- images/<data>/slide-01.jpg, slide-02.jpg, ...: le anteprime che la PR mostra
  (720 px di larghezza, così il repo non cresce troppo);
- images/<data>.pdf: il documento a piena risoluzione che LinkedIn pubblica come
  carosello. Non va nel repo: publish.py lo ridisegna al momento del Merge.

Esce con 0 se ha disegnato il carosello o se il post non ne ha uno, con 1 se il
blocco è sbagliato o un testo non ci sta: in quel caso stampa cosa correggere,
come readability.py.

Al massimo 4 pagine (dal 2026-10-23): la copertina, da 1 a 3 slide e, se resta
posto, una chiusura facoltativa.

Lo stile è quello chiaro delle infografiche (render_image.py): fondo avorio,
titoli neri pesanti, testi con le grazie, terracotta come accento. In più:
- le parole fra **due asterischi** nel titolo della copertina e nella chiusura
  finiscono in un riquadro terracotta; nei titoletti e nei testi delle slide
  cambiano solo colore (i passaggi chiave);
- le illustrazioni le disegna ChatGPT (scripts/illustrazione.py): una per la
  copertina e una per ogni slide di testo che ha il campo `illustrazione`. Stanno
  in images/<data>/illustrazione.jpg (copertina) e illustrazione-NN.jpg (pagina NN).
  Se un'illustrazione manca, la pagina esce con il solo testo;
- i cubi isometrici restano solo nei confronti (`voci`), dove sono il grafico:
  niente cubi decorativi.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

sys.path.insert(0, str(Path(__file__).parent))
from publish import parse_post_file  # noqa: E402
from render_image import (  # noqa: E402
    ALT_MAX, ARGILLA, ARGILLA_SCURA, CREMA, IMAGES, INCHIOSTRO, LARGHEZZA, LINEA,
    MARGINE, SECONDARIO, SERIF, SERIF_TESTO, SFONDO, TITOLO, TRATTO, VALORE, W,
    ErroreImmagine, adatta, campo, corpo_confronto, corpo_numero, font, larghezza,
    scrivi, valida,
)

# Quadrato (dal 2026-10-23): sul telefono occupa metà schermo invece di due terzi,
# ed è il formato che Marco vede usare di più nei caroselli. L'infografica dei post
# vecchi (render_image.py) resta 1080x1080.
H = 1080
PAGINE_MAX = 4
SLIDE_MIN, SLIDE_MAX = 1, 3
TITOLETTO_MAX = 60
ILLUSTRAZIONE_MAX = 500
SALVA = "Salva il post per quando ti serve."
ANTEPRIMA_W = 720
PIEDE_Y = H - MARGINE - 26          # riga del piede: fonte a sinistra, pagina a destra
FONDO = PIEDE_Y - 64                # sotto questa y non si disegna il contenuto
ALTO_FOTO = 430                     # l'illustrazione in cima alle slide di testo


# --- parole evidenziate -------------------------------------------------------------

def parole_evidenziate(testo: str) -> list:
    """Spezza il testo in parole. Ogni parola è una lista di pezzi (testo, evidenziato):
    «**Excel**.» diventa [("Excel", True), (".", False)], così la punteggiatura resta
    attaccata alla parola ma fuori dal riquadro."""
    if testo.count("**") % 2:
        raise ErroreImmagine(f"asterischi non chiusi in «{testo}»: usa **parola**")
    parole, corrente, pezzo, evidenza, i = [], [], "", False, 0
    while i < len(testo):
        if testo.startswith("**", i):
            if pezzo:
                corrente.append((pezzo, evidenza))
                pezzo = ""
            evidenza = not evidenza
            i += 2
            continue
        ch = testo[i]
        if ch.isspace():
            if pezzo:
                corrente.append((pezzo, evidenza))
                pezzo = ""
            if corrente:
                parole.append(corrente)
                corrente = []
        else:
            pezzo += ch
        i += 1
    if pezzo:
        corrente.append((pezzo, evidenza))
    if corrente:
        parole.append(corrente)
    return parole


def testo_semplice(testo: str) -> str:
    """Il testo senza gli asterischi: serve per il titolo del documento su LinkedIn."""
    return " ".join("".join(p for p, _ in parola) for parola in parole_evidenziate(testo))


def scrivi_evidenziato(draw, xy, testo: str, nome_font: str, sizes, max_w: int,
                       max_righe: int, nome_campo: str, interlinea: float = 1.1,
                       riquadro: bool = True, colore_evidenza=None) -> int:
    """Come scrivi(), ma le parole fra ** si vedono.

    Con riquadro=True (titoli di copertina e chiusura) finiscono in un riquadro
    terracotta con il testo chiaro, e due parole evidenziate vicine sulla stessa
    riga condividono il riquadro. Con riquadro=False (titoletti e testi delle
    slide) cambiano solo colore, come i passaggi chiave nei caroselli di notizie.
    Restituisce la y sotto l'ultima riga."""
    parole = parole_evidenziate(testo)
    if not parole:
        raise ErroreImmagine(f"«{nome_campo}» è vuoto")
    # Gli a capo scritti nel campo restano: «Prima frase.\n**Seconda.**» va su due righe.
    semplice = "\n".join(" ".join(r.split()) for r in testo.replace("**", "").strip().split("\n"))
    # Il riquadro sporge di qualche pixel: si lascia margine alla misura.
    f, righe = adatta(draw, semplice, nome_font, sizes, max_w - 24, max_righe, nome_campo)
    spazio = larghezza(draw, " ", f)
    passo = int(f.size * interlinea)
    # Il riquadro va dall'altezza delle maiuscole al fondo delle discendenti: così
    # due righe evidenziate una sotto l'altra non si toccano.
    alto_lettere, basso_lettere = f.getbbox("H")[1], f.getbbox("g")[3]
    pad_x, pad_y = int(f.size * 0.12), int(f.size * 0.07)
    x0, y = xy
    k = 0
    for riga in righe:
        n = len(riga.split())
        pezzi, x = [], x0
        for parola in parole[k:k + n]:
            for testo_pezzo, evidenza in parola:
                w = larghezza(draw, testo_pezzo, f)
                pezzi.append((x, w, testo_pezzo, evidenza))
                x += w
            x += spazio
        k += n
        # Riquadri: un tratto continuo per ogni gruppo di pezzi evidenziati vicini.
        gruppi, aperto = [], None
        for px, pw, _, ev in pezzi:
            if ev and aperto and px - aperto[1] <= spazio + 1:
                aperto[1] = px + pw
            elif ev:
                aperto = [px, px + pw]
                gruppi.append(aperto)
            else:
                aperto = None
        for gx0, gx1 in (gruppi if riquadro else []):
            draw.rounded_rectangle(
                (gx0 - pad_x, y + alto_lettere - pad_y, gx1 + pad_x, y + basso_lettere + pad_y),
                radius=int(f.size * 0.14), fill=ARGILLA)
        acceso = CREMA if riquadro else (colore_evidenza or ARGILLA_SCURA)
        for px, _, testo_pezzo, ev in pezzi:
            draw.text((px, y), testo_pezzo, font=f, fill=acceso if ev else INCHIOSTRO)
        y += passo
    return y


# --- validazione --------------------------------------------------------------------

def _scena(blocco: dict, dove: str, obbligatoria: bool) -> None:
    scena = campo(blocco, "illustrazione", obbligatorio=obbligatoria)
    if len(scena) > ILLUSTRAZIONE_MAX:
        raise ErroreImmagine(f"«illustrazione» {dove} di {len(scena)} caratteri, il massimo è "
                             f"{ILLUSTRAZIONE_MAX}: descrivi la scena in poche righe")


def valida_carosello(dati) -> dict:
    if not isinstance(dati, dict):
        raise ErroreImmagine("`carosello:` deve essere un blocco di campi, non una riga sola")
    copertina = dati.get("copertina")
    if not isinstance(copertina, dict):
        raise ErroreImmagine("manca il blocco «copertina» con titolo e illustrazione")
    parole_evidenziate(campo(copertina, "titolo"))
    _scena(copertina, "della copertina", True)

    slide = dati.get("slide")
    if not isinstance(slide, list) or not SLIDE_MIN <= len(slide) <= SLIDE_MAX:
        raise ErroreImmagine(f"«slide» deve avere da {SLIDE_MIN} a {SLIDE_MAX} elementi")
    chiusura = campo(dati, "chiusura", obbligatorio=False)
    pagine = 1 + len(slide) + (1 if chiusura else 0)
    if pagine > PAGINE_MAX:
        raise ErroreImmagine(f"il carosello avrebbe {pagine} pagine, il massimo è {PAGINE_MAX}: "
                             "togli una slide o la chiusura")
    for i, s in enumerate(slide, 1):
        if not isinstance(s, dict):
            raise ErroreImmagine(f"la slide {i} deve avere titolo e contenuto")
        titoletto = campo(s, "titolo", obbligatorio=False)
        if len(testo_semplice(titoletto) if titoletto else "") > TITOLETTO_MAX:
            raise ErroreImmagine(f"il titolo della slide {i} supera {TITOLETTO_MAX} caratteri")
        parole_evidenziate(campo(s, "testo", obbligatorio=False))
        tipi = [t for t in ("frase", "numero", "voci") if s.get(t) not in (None, "")]
        if len(tipi) > 1:
            raise ErroreImmagine(f"la slide {i} ha {' e '.join(tipi)}: una slide, una cosa")
        if not tipi and not campo(s, "testo", obbligatorio=False):
            raise ErroreImmagine(f"la slide {i} non ha contenuto: serve testo, frase, numero o voci")
        if tipi and s.get("illustrazione"):
            raise ErroreImmagine(f"la slide {i} ha {tipi[0]} e illustrazione: l'illustrazione "
                                 "va solo sulle slide di testo")
        _scena(s, f"della slide {i}", False)
        if "numero" in tipi and not campo(s, "testo", obbligatorio=False):
            raise ErroreImmagine(f"la slide {i} ha il numero senza «testo» che lo spieghi")
        if "voci" in tipi:
            # Stesse regole del modello «confronto» dell'infografica.
            valida({"modello": "confronto", "titolo": "-", "alt": "-", "voci": s["voci"]})

    if chiusura:
        parole_evidenziate(chiusura)
    if "personaggio" in dati and not isinstance(dati["personaggio"], bool):
        raise ErroreImmagine("«personaggio» è true o false: true solo nei post sugli agenti")
    alt = campo(dati, "alt")
    if len(alt) > ALT_MAX:
        raise ErroreImmagine(f"«alt» di {len(alt)} caratteri, il massimo è {ALT_MAX}")
    return dati


# --- pezzi comuni -------------------------------------------------------------------

def freccia(draw, x_destra: int, y_centro: int, lunga: int = 56) -> None:
    """La freccia che invita a scorrere, disegnata: non dipende dai glifi del font."""
    draw.line((x_destra - lunga, y_centro, x_destra - 6, y_centro), fill=INCHIOSTRO, width=5)
    draw.polygon([(x_destra, y_centro), (x_destra - 18, y_centro - 13),
                  (x_destra - 18, y_centro + 13)], fill=INCHIOSTRO)


def piede(draw, pagina: int, totale: int, fonte: str = "") -> None:
    f = font(SERIF_TESTO, 28)
    if fonte:
        fonte = fonte.removeprefix("https://").removeprefix("http://").removeprefix("www.")
        testo = f"Fonte: {fonte}"
        if larghezza(draw, testo, f) > LARGHEZZA - 220:
            raise ErroreImmagine("«fonte» troppo lunga per il piede: metti solo il dominio")
        draw.text((MARGINE, PIEDE_Y), testo, font=f, fill=SECONDARIO)
    scorri = pagina < totale
    numero = f"{pagina}/{totale}"
    x = W - MARGINE - (80 if scorri else 0) - larghezza(draw, numero, f)
    draw.text((x, PIEDE_Y), numero, font=f, fill=SECONDARIO)
    if scorri:
        freccia(draw, W - MARGINE, PIEDE_Y + 17)


def riempi(img: Image.Image, foto: Image.Image, box) -> None:
    """Mette la foto nel riquadro tagliandola al centro, con gli angoli arrotondati e
    il contorno nero."""
    x0, y0, x1, y1 = (int(v) for v in box)
    adattata = ImageOps.fit(foto.convert("RGB"), (x1 - x0, y1 - y0), Image.LANCZOS)
    maschera = Image.new("L", adattata.size, 0)
    ImageDraw.Draw(maschera).rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1),
                                               radius=40, fill=255)
    img.paste(adattata, (x0, y0), maschera)
    ImageDraw.Draw(img).rounded_rectangle(box, radius=40, outline=INCHIOSTRO, width=TRATTO)


def metti_foto(img: Image.Image, percorso, box) -> bool:
    """Mette l'illustrazione se il file c'è. Restituisce False se manca."""
    if not percorso or not Path(percorso).is_file():
        return False
    with Image.open(percorso) as foto:
        riempi(img, foto, box)
    return True


def fumetto(draw, y: int, frase: str, y_max: int) -> int:
    """La frase da scrivere all'assistente dentro un fumetto. Restituisce la y sotto la coda."""
    pad = 52
    spazio = y_max - y - 70
    for size in range(46, 27, -2):
        try:
            f, righe = adatta(draw, f"“{frase}”", SERIF, [size], LARGHEZZA - 2 * pad - 40, 7, "frase")
        except ErroreImmagine:
            continue
        alto = int(f.size * 1.3) * len(righe) + 2 * pad
        if alto <= spazio:
            break
    else:
        raise ErroreImmagine("la «frase» non sta nella slide: accorciala o togli il testo sopra")
    bordo = (MARGINE, y, W - MARGINE - 40, y + alto)
    coda = [(MARGINE + 64, y + alto - 4), (MARGINE + 52, y + alto + 54), (MARGINE + 136, y + alto - 4)]
    draw.polygon(coda, fill=CREMA, outline=INCHIOSTRO, width=TRATTO)
    draw.rounded_rectangle(bordo, radius=36, fill=CREMA, outline=INCHIOSTRO, width=TRATTO)
    draw.rectangle((coda[0][0] + 3, y + alto - TRATTO - 1, coda[2][0] - 4, y + alto + 1), fill=CREMA)
    scrivi(draw, (MARGINE + pad, y + pad - 6), righe, f, INCHIOSTRO, 1.3)
    return y + alto + 54


def _titoletto(draw, s: dict, y: int, sizes=range(58, 39, -2)) -> int:
    """Il titoletto della slide: grassetto nero, le parole fra ** in terracotta."""
    titoletto = campo(s, "titolo", obbligatorio=False)
    if not titoletto:
        return y
    return scrivi_evidenziato(draw, (MARGINE, y), titoletto, VALORE, sizes, LARGHEZZA, 2,
                              "titolo della slide", 1.12, riquadro=False,
                              colore_evidenza=ARGILLA) + 22


def _testo(draw, s: dict, y: int, sizes, righe_max: int, interlinea: float = 1.28) -> int:
    return scrivi_evidenziato(draw, (MARGINE, y), campo(s, "testo"), SERIF, sizes, LARGHEZZA,
                              righe_max, "testo", interlinea, riquadro=False)


def _blocco(draw, s: dict, y: int, alto_max: int, grande: bool) -> int:
    """Titoletto e testo, dal corpo più grande che sta in alto_max pixel.
    Restituisce la y sotto il testo. Con draw=None misura soltanto."""
    prova = ImageDraw.Draw(Image.new("RGB", (W, H)))
    titoli = range(60, 41, -2) if grande else range(52, 37, -2)
    for alto_testo in (range(50, 29, -2) if grande else range(44, 27, -2)):
        sizes = range(alto_testo, 27, -2)
        try:
            fine = _testo(prova, s, _titoletto(prova, s, 0, titoli), sizes, 11)
        except ErroreImmagine:
            continue
        if fine <= alto_max:
            if draw is None:
                return fine
            return _testo(draw, s, _titoletto(draw, s, y, titoli), sizes, 11)
    raise ErroreImmagine("titolo e testo della slide non stanno nella pagina: accorciali")


def _solo_testo(s: dict) -> bool:
    return all(s.get(k) in (None, "", []) for k in ("numero", "voci", "frase"))


# --- le pagine ----------------------------------------------------------------------

def pagina_copertina(dati: dict, totale: int, foto=None) -> Image.Image:
    cop = dati["copertina"]
    img = Image.new("RGB", (W, H), SFONDO)
    draw = ImageDraw.Draw(img)

    def testata(d, y, sizes):
        y = scrivi_evidenziato(d, (MARGINE, y), campo(cop, "titolo"), TITOLO,
                               sizes, LARGHEZZA, 4, "titolo", 1.18)
        sottotitolo = campo(cop, "sottotitolo", obbligatorio=False)
        if sottotitolo:
            f_sot, righe = adatta(d, sottotitolo, SERIF, range(38, 27, -2), LARGHEZZA, 2,
                                  "sottotitolo")
            y = scrivi(d, (MARGINE, y + 10), righe, f_sot, INCHIOSTRO, 1.22)
        return y

    if foto and Path(foto).is_file():
        y = testata(draw, MARGINE - 8, range(92, 51, -4))
        box = (MARGINE, y + 36, W - MARGINE, FONDO)
        if box[3] - box[1] < 300:
            raise ErroreImmagine("titolo e sottotitolo lasciano poco posto all'illustrazione: "
                                 "accorciali")
        metti_foto(img, foto, box)
    else:
        # Senza illustrazione: il titolo più grande, un po' sopra il centro.
        prova = ImageDraw.Draw(Image.new("RGB", (W, H)))
        alto = testata(prova, 0, range(112, 63, -4))
        testata(draw, MARGINE + max(0, int((FONDO - MARGINE - alto) * 0.38)), range(112, 63, -4))
    piede(draw, 1, totale)
    return img


def pagina_slide(s: dict, pagina: int, totale: int, foto=None, fonte: str = "") -> Image.Image:
    img = Image.new("RGB", (W, H), SFONDO)
    draw = ImageDraw.Draw(img)
    fonte = campo(s, "fonte", obbligatorio=False) or fonte
    testo = campo(s, "testo", obbligatorio=False)
    y = MARGINE

    if _solo_testo(s):
        if foto and metti_foto(img, foto, (MARGINE, MARGINE, W - MARGINE, MARGINE + ALTO_FOTO)):
            # Come nei caroselli di notizie: l'illustrazione sopra, il testo sotto.
            y = MARGINE + ALTO_FOTO + 40
            _blocco(draw, s, y, FONDO - y, grande=False)
        else:
            # Senza illustrazione: titoletto e testo in un blocco solo, un po' sopra il
            # centro della pagina.
            alto = _blocco(None, s, 0, FONDO - MARGINE, grande=True)
            y += max(0, int((FONDO - MARGINE - alto) * 0.42))
            _blocco(draw, s, y, FONDO - MARGINE, grande=True)
    else:
        y = _titoletto(draw, s, y)
        if s.get("numero") not in (None, ""):
            corpo_numero(draw, {"numero": s["numero"], "didascalia": testo_semplice(testo)},
                         y, FONDO, cubi=False)
        elif s.get("voci"):
            if testo:
                y = _testo(draw, s, y, range(42, 29, -2), 3, 1.25) + 20
            corpo_confronto(draw, {"voci": s["voci"]}, y, FONDO)
        else:
            if testo:
                y = _testo(draw, s, y, range(42, 29, -2), 3, 1.25) + 32
            fumetto(draw, y, campo(s, "frase"), FONDO)
    piede(draw, pagina, totale, fonte)
    return img


def pagina_chiusura(dati: dict, totale: int) -> Image.Image:
    img = Image.new("RGB", (W, H), SFONDO)
    draw = ImageDraw.Draw(img)
    y = scrivi_evidenziato(draw, (MARGINE, MARGINE + 60), campo(dati, "chiusura"), TITOLO,
                           range(84, 51, -4), LARGHEZZA, 5, "chiusura", 1.2)
    f_salva = font(SERIF, 42)
    y_salva = FONDO - 52
    if y_salva - y < 120:
        raise ErroreImmagine("la «chiusura» è troppo lunga per l'ultima slide: accorciala")
    draw.line((MARGINE, y_salva - 34, W - MARGINE, y_salva - 34), fill=LINEA, width=2)
    draw.text((MARGINE, y_salva), SALVA, font=f_salva, fill=INCHIOSTRO)
    piede(draw, totale, totale, campo(dati, "fonte", obbligatorio=False))
    return img


def foto_pagina(illustrazioni, pagina: int):
    """Il file dell'illustrazione di una pagina. `illustrazioni` è la cartella del post
    (images/<data>/) oppure, per comodità, il file della sola copertina."""
    if not illustrazioni:
        return None
    illustrazioni = Path(illustrazioni)
    if illustrazioni.suffix:  # un file: vale solo per la copertina
        return illustrazioni if pagina == 1 else None
    return illustrazioni / nome_illustrazione(pagina)


def disegna_carosello(dati: dict, illustrazioni=None) -> list:
    """Restituisce le pagine del carosello, dalla copertina all'ultima slide."""
    dati = valida_carosello(dati)
    chiusura = campo(dati, "chiusura", obbligatorio=False)
    totale = 1 + len(dati["slide"]) + (1 if chiusura else 0)
    fonte_finale = "" if chiusura else campo(dati, "fonte", obbligatorio=False)
    pagine = [pagina_copertina(dati, totale, foto_pagina(illustrazioni, 1))]
    for i, s in enumerate(dati["slide"], 2):
        ultima = i == len(dati["slide"]) + 1
        pagine.append(pagina_slide(s, i, totale, foto_pagina(illustrazioni, i),
                                   fonte_finale if ultima else ""))
    if chiusura:
        pagine.append(pagina_chiusura(dati, totale))
    return pagine


# --- file ---------------------------------------------------------------------------

def cartella_post(post: Path) -> Path:
    """images/<data>/: anteprime, illustrazioni e prompt usati."""
    return IMAGES / post.stem


def nome_illustrazione(pagina: int) -> str:
    return "illustrazione.jpg" if pagina == 1 else f"illustrazione-{pagina:02d}.jpg"


def percorso_illustrazione(post: Path, pagina: int = 1) -> Path:
    return cartella_post(post) / nome_illustrazione(pagina)


def scene(dati: dict) -> dict:
    """Le scene da disegnare, per numero di pagina: la copertina e le slide di testo
    che hanno il campo `illustrazione`."""
    if not isinstance(dati, dict) or not isinstance(dati.get("copertina"), dict):
        return {}
    risultato = {}
    copertina = str(dati["copertina"].get("illustrazione") or "").strip()
    if copertina:
        risultato[1] = copertina
    for i, s in enumerate(dati.get("slide") or [], 2):
        if isinstance(s, dict) and str(s.get("illustrazione") or "").strip() and _solo_testo(s):
            risultato[i] = str(s["illustrazione"]).strip()
    return risultato


def percorso_pdf(post: Path) -> Path:
    return IMAGES / f"{post.stem}.pdf"


def salva_pdf(pagine: list, percorso: Path) -> None:
    percorso.parent.mkdir(parents=True, exist_ok=True)
    pagine[0].save(percorso, "PDF", save_all=True, append_images=pagine[1:],
                   resolution=144, quality=92)


def salva_anteprime(pagine: list, cartella: Path) -> list:
    """Le anteprime JPEG per la PR. Toglie quelle vecchie, se il carosello si è accorciato."""
    cartella.mkdir(parents=True, exist_ok=True)
    for vecchia in cartella.glob("slide-*.jpg"):
        vecchia.unlink()
    alto = round(H * ANTEPRIMA_W / W)
    percorsi = []
    for i, pagina in enumerate(pagine, 1):
        p = cartella / f"slide-{i:02d}.jpg"
        pagina.resize((ANTEPRIMA_W, alto), Image.LANCZOS).save(p, "JPEG", quality=84, optimize=True)
        percorsi.append(p)
    return percorsi


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("post", help="file del post, es. approved/2026-10-24.md")
    parser.add_argument("--pdf", help="dove salvare il PDF (default images/<data>.pdf)")
    parser.add_argument("--senza-anteprime", action="store_true",
                        help="scrive solo il PDF, non le anteprime JPEG")
    args = parser.parse_args(argv)

    post = Path(args.post)
    meta = parse_post_file(str(post))["meta"] or {}
    if "carosello" not in meta:
        print(f"{post}: nessun blocco carosello, niente da disegnare")
        return 0
    cartella = cartella_post(post)
    try:
        pagine = disegna_carosello(meta["carosello"], cartella)
    except ErroreImmagine as e:
        print(f"{post}\n  ! carosello: {e}")
        return 1
    pdf = Path(args.pdf) if args.pdf else percorso_pdf(post)
    salva_pdf(pagine, pdf)
    print(f"{post}\n  OK: {len(pagine)} pagine in {pdf}")
    mancano = [n for n in scene(meta["carosello"]) if not percorso_illustrazione(post, n).is_file()]
    if mancano:
        print(f"  ? pagine senza illustrazione: {', '.join(map(str, mancano))}. Escono con il "
              "solo testo; le illustrazioni le disegna scripts/illustrazione.py")
    if not args.senza_anteprime:
        anteprime = salva_anteprime(pagine, cartella)
        print(f"  OK: anteprime in {anteprime[0].parent}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
