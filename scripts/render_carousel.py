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

Lo stile è quello dell'infografica (render_image.py): fondo avorio, titoli neri
pesanti, testi con le grazie, terracotta come accento, cubi isometrici. In più:
- le parole fra **due asterischi** nel titolo della copertina e nella chiusura
  finiscono in un riquadro terracotta;
- la copertina ha l'illustrazione disegnata da OpenAI (scripts/illustrazione.py).
  Se manca, al suo posto c'è una pila di cubi.

Struttura del carosello:
- copertina: titolo con le parole evidenziate, sottotitolo facoltativo, illustrazione
- da 2 a 5 slide, una per passo o per trucco: un'etichetta e un contenuto fra
  testo, frase (la frase esatta da scrivere), numero e voci (un confronto)
- chiusura: la frase che riprende l'hook e l'invito a salvare il post
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageOps

sys.path.insert(0, str(Path(__file__).parent))
from publish import parse_post_file  # noqa: E402
from render_image import (  # noqa: E402
    ALT_MAX, ARGILLA, CARTA, COLORI_EVIDENZA, CREMA, ETICHETTA, H, IMAGES, INCHIOSTRO,
    LARGHEZZA, LINEA, MARGINE, SECONDARIO, SERIF, SERIF_TESTO, SFONDO, TITOLO, TRATTO,
    W, ErroreImmagine, adatta, campo, corpo_confronto, corpo_numero, dimensioni_pila,
    disegna_pila, font, larghezza, motivo, scrivi, spaziato, valida,
)

SLIDE_MIN, SLIDE_MAX = 2, 5
ETICHETTA_MAX = 40
ILLUSTRAZIONE_MAX = 500
SALVA = "Salva il post per quando lo provi."
ANTEPRIMA_W = 720
PIEDE_Y = H - MARGINE - 26          # riga del piede: fonte a sinistra, pagina a destra
FONDO = PIEDE_Y - 64                # sotto questa y non si disegna il contenuto


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
                       max_righe: int, nome_campo: str, interlinea: float = 1.1) -> int:
    """Come scrivi(), ma le parole fra ** finiscono in un riquadro terracotta con il
    testo chiaro. Due parole evidenziate vicine sulla stessa riga condividono il
    riquadro. Restituisce la y sotto l'ultima riga."""
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
        for gx0, gx1 in gruppi:
            draw.rounded_rectangle(
                (gx0 - pad_x, y + alto_lettere - pad_y, gx1 + pad_x, y + basso_lettere + pad_y),
                radius=int(f.size * 0.14), fill=ARGILLA)
        for px, _, testo_pezzo, ev in pezzi:
            draw.text((px, y), testo_pezzo, font=f, fill=CREMA if ev else INCHIOSTRO)
        y += passo
    return y


# --- validazione --------------------------------------------------------------------

def valida_carosello(dati) -> dict:
    if not isinstance(dati, dict):
        raise ErroreImmagine("`carosello:` deve essere un blocco di campi, non una riga sola")
    copertina = dati.get("copertina")
    if not isinstance(copertina, dict):
        raise ErroreImmagine("manca il blocco «copertina» con titolo e illustrazione")
    parole_evidenziate(campo(copertina, "titolo"))
    scena = campo(copertina, "illustrazione")
    if len(scena) > ILLUSTRAZIONE_MAX:
        raise ErroreImmagine(f"«illustrazione» di {len(scena)} caratteri, il massimo è "
                             f"{ILLUSTRAZIONE_MAX}: descrivi la scena in poche righe")

    slide = dati.get("slide")
    if not isinstance(slide, list) or not SLIDE_MIN <= len(slide) <= SLIDE_MAX:
        raise ErroreImmagine(f"«slide» deve avere da {SLIDE_MIN} a {SLIDE_MAX} elementi")
    for i, s in enumerate(slide, 1):
        if not isinstance(s, dict):
            raise ErroreImmagine(f"la slide {i} deve avere etichetta e contenuto")
        etichetta = campo(s, "etichetta")
        if len(etichetta) > ETICHETTA_MAX:
            raise ErroreImmagine(f"l'etichetta della slide {i} supera {ETICHETTA_MAX} caratteri")
        tipi = [t for t in ("frase", "numero", "voci") if s.get(t) not in (None, "")]
        if len(tipi) > 1:
            raise ErroreImmagine(f"la slide {i} ha {' e '.join(tipi)}: una slide, una cosa")
        if not tipi and not campo(s, "testo", obbligatorio=False):
            raise ErroreImmagine(f"la slide {i} non ha contenuto: serve testo, frase, numero o voci")
        if "numero" in tipi and not campo(s, "testo", obbligatorio=False):
            raise ErroreImmagine(f"la slide {i} ha il numero senza «testo» che lo spieghi")
        if "voci" in tipi:
            # Stesse regole del modello «confronto» dell'infografica.
            valida({"modello": "confronto", "titolo": "-", "alt": "-", "voci": s["voci"]})

    parole_evidenziate(campo(dati, "chiusura"))
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


def piede(draw, pagina: int, totale: int, fonte: str = "", scorri: bool = True) -> None:
    f = font(SERIF_TESTO, 28)
    if fonte:
        fonte = fonte.removeprefix("https://").removeprefix("http://").removeprefix("www.")
        testo = f"Fonte: {fonte}"
        if larghezza(draw, testo, f) > LARGHEZZA - 220:
            raise ErroreImmagine("«fonte» troppo lunga per il piede: metti solo il dominio")
        draw.text((MARGINE, PIEDE_Y), testo, font=f, fill=SECONDARIO)
    numero = f"{pagina}/{totale}"
    x = W - MARGINE - (80 if scorri else 0) - larghezza(draw, numero, f)
    draw.text((x, PIEDE_Y), numero, font=f, fill=SECONDARIO)
    if scorri:
        freccia(draw, W - MARGINE, PIEDE_Y + 17)


def riempi(img: Image.Image, foto: Image.Image, box) -> None:
    """Mette la foto nel riquadro tagliandola al centro, con gli angoli arrotondati."""
    x0, y0, x1, y1 = (int(v) for v in box)
    adattata = ImageOps.fit(foto.convert("RGB"), (x1 - x0, y1 - y0), Image.LANCZOS)
    maschera = Image.new("L", adattata.size, 0)
    ImageDraw.Draw(maschera).rounded_rectangle((0, 0, x1 - x0 - 1, y1 - y0 - 1),
                                               radius=40, fill=255)
    img.paste(adattata, (x0, y0), maschera)


def fumetto(draw, y: int, frase: str, y_max: int) -> int:
    """La frase da scrivere all'assistente dentro un fumetto. Restituisce la y sotto la coda."""
    pad = 52
    spazio = y_max - y - 70
    for size in range(52, 29, -2):
        try:
            f, righe = adatta(draw, f"“{frase}”", SERIF, [size], LARGHEZZA - 2 * pad - 40, 9, "frase")
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


# --- le tre pagine ------------------------------------------------------------------

def pagina_copertina(dati: dict, totale: int, illustrazione: Path = None) -> Image.Image:
    cop = dati["copertina"]
    img = Image.new("RGB", (W, H), SFONDO)
    draw = ImageDraw.Draw(img)
    y = scrivi_evidenziato(draw, (MARGINE, MARGINE - 8), campo(cop, "titolo"), TITOLO,
                           range(112, 63, -4), LARGHEZZA, 4, "titolo", 1.18)
    sottotitolo = campo(cop, "sottotitolo", obbligatorio=False)
    if sottotitolo:
        f_sot, righe = adatta(draw, sottotitolo, SERIF, range(44, 31, -2), LARGHEZZA, 2, "sottotitolo")
        y = scrivi(draw, (MARGINE, y + 10), righe, f_sot, INCHIOSTRO, 1.22)

    box = (MARGINE, y + 44, W - MARGINE, FONDO)
    if box[3] - box[1] < 360:
        raise ErroreImmagine("titolo e sottotitolo lasciano poco posto all'illustrazione: accorciali")
    if illustrazione and Path(illustrazione).exists():
        with Image.open(illustrazione) as foto:
            riempi(img, foto, box)
    else:
        # Senza illustrazione: una pila di cubi terracotta su carta, lo stesso segno
        # delle infografiche.
        draw.rounded_rectangle(box, radius=40, fill=CARTA)
        alto = box[3] - box[1]
        s = 70
        while s > 30 and dimensioni_pila(12, s)[1] > alto * 0.72:
            s -= 2
        disegna_pila(draw, (box[0] + box[2]) / 2, box[3] - alto * 0.16, s, 12, COLORI_EVIDENZA)
    draw.rounded_rectangle(box, radius=40, outline=INCHIOSTRO, width=TRATTO)
    piede(draw, 1, totale)
    return img


def pagina_slide(s: dict, pagina: int, totale: int) -> Image.Image:
    img = Image.new("RGB", (W, H), SFONDO)
    draw = ImageDraw.Draw(img)
    fonte = campo(s, "fonte", obbligatorio=False)

    y = MARGINE + 4
    f_lab = font(ETICHETTA, 30)
    # Il numero del passo in terracotta, poi l'etichetta: si capisce dove sei.
    x = spaziato(draw, (MARGINE, y), f"{pagina - 1:02d}", f_lab, ARGILLA, 3)
    draw.line((x + 14, y + 17, x + 54, y + 17), fill=ARGILLA, width=3)
    spaziato(draw, (x + 70, y), campo(s, "etichetta").upper(), f_lab, ARGILLA, 3)
    y += 30 + 64

    testo = campo(s, "testo", obbligatorio=False)
    if s.get("numero") not in (None, ""):
        corpo_numero(draw, {"numero": s["numero"], "didascalia": testo}, y, FONDO)
    elif s.get("voci"):
        if testo:
            f, righe = adatta(draw, testo, SERIF, range(48, 33, -2), LARGHEZZA, 3, "testo")
            y = scrivi(draw, (MARGINE, y), righe, f, INCHIOSTRO, 1.25) + 24
        corpo_confronto(draw, {"voci": s["voci"]}, y, FONDO)
    elif s.get("frase"):
        if testo:
            f, righe = adatta(draw, testo, SERIF, range(48, 33, -2), LARGHEZZA, 4, "testo")
            y = scrivi(draw, (MARGINE, y), righe, f, INCHIOSTRO, 1.25) + 40
        y_fine = fumetto(draw, y, campo(s, "frase"), FONDO)
        if FONDO - y_fine > 4 * 40 + 20:
            motivo(draw, W - MARGINE, FONDO, 40)
    else:
        f, righe = adatta(draw, testo, SERIF, range(64, 37, -2), LARGHEZZA, 11, "testo")
        y_fine = scrivi(draw, (MARGINE, y), righe, f, INCHIOSTRO, 1.28)
        if FONDO - y_fine > 4 * 54 + 40:
            motivo(draw, W - MARGINE, FONDO, 54)
    piede(draw, pagina, totale, fonte)
    return img


def pagina_chiusura(dati: dict, totale: int) -> Image.Image:
    img = Image.new("RGB", (W, H), SFONDO)
    draw = ImageDraw.Draw(img)
    y = scrivi_evidenziato(draw, (MARGINE, MARGINE + 60), campo(dati, "chiusura"), TITOLO,
                           range(96, 55, -4), LARGHEZZA, 6, "chiusura", 1.2)
    f_salva = font(SERIF, 42)
    y_salva = FONDO - 52
    if y_salva - y < 4 * 64 + 60:
        raise ErroreImmagine("la «chiusura» è troppo lunga per l'ultima slide: accorciala")
    motivo(draw, MARGINE + 4 * 64 * 0.87, y_salva - 70, 64)
    draw.line((MARGINE, y_salva - 34, W - MARGINE, y_salva - 34), fill=LINEA, width=2)
    draw.text((MARGINE, y_salva), SALVA, font=f_salva, fill=INCHIOSTRO)
    piede(draw, totale, totale, campo(dati, "fonte", obbligatorio=False), scorri=False)
    return img


def disegna_carosello(dati: dict, illustrazione: Path = None) -> list:
    """Restituisce le pagine del carosello, dalla copertina alla chiusura."""
    dati = valida_carosello(dati)
    totale = len(dati["slide"]) + 2
    pagine = [pagina_copertina(dati, totale, illustrazione)]
    pagine += [pagina_slide(s, i, totale) for i, s in enumerate(dati["slide"], 2)]
    pagine.append(pagina_chiusura(dati, totale))
    return pagine


# --- file ---------------------------------------------------------------------------

def cartella_post(post: Path) -> Path:
    """images/<data>/: anteprime, illustrazione e prompt usato."""
    return IMAGES / post.stem


def percorso_illustrazione(post: Path) -> Path:
    return cartella_post(post) / "illustrazione.jpg"


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
    illustrazione = percorso_illustrazione(post)
    try:
        pagine = disegna_carosello(meta["carosello"], illustrazione)
    except ErroreImmagine as e:
        print(f"{post}\n  ! carosello: {e}")
        return 1
    pdf = Path(args.pdf) if args.pdf else percorso_pdf(post)
    salva_pdf(pagine, pdf)
    print(f"{post}\n  OK: {len(pagine)} pagine in {pdf}")
    if not illustrazione.exists():
        print("  ? copertina senza illustrazione: al suo posto ci sono i cubi "
              "(la disegna scripts/illustrazione.py)")
    if not args.senza_anteprime:
        anteprime = salva_anteprime(pagine, cartella_post(post))
        print(f"  OK: anteprime in {anteprime[0].parent}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
