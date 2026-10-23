#!/usr/bin/env python3
"""Disegna l'infografica di un post a partire dal blocco `immagine:` del frontmatter.

Uso:
    python scripts/render_image.py approved/2026-10-20.md
    python scripts/render_image.py approved/2026-10-20.md --out /tmp/prova.png

Scrive images/<data>.png (1080x1350, 4:5: il formato che occupa più spazio nel feed
da telefono). Esce con 0 se ha disegnato l'immagine o se il post non ne ha una,
con 1 se il blocco è sbagliato o il testo non ci sta: in quel caso stampa cosa
correggere, come readability.py.

Lo stile (dal 2026-10-19 pomeriggio): fondo avorio, titolo nero pesante,
sottotitolo con le grazie, un accento terracotta e piccoli cubi disegnati con il
contorno nero, come le illustrazioni piatte dei blog di AI. Niente loghi né
mascotte: l'immagine è di Marco, non di un marchio.

Tre modelli, scelti dal campo `modello`:
- numero:    un dato grande dentro un riquadro, con la didascalia sotto
- confronto: da 2 a 4 voci, ognuna con una pila di cubi proporzionale al valore
- frase:     la frase esatta da scrivere all'assistente, dentro un fumetto

I numeri seguono le regole di STYLE.md: presi dalla fonte o da un conto con le
ipotesi dichiarate nel post. Lo script non li verifica, li disegna.
"""

import argparse
import math
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from publish import parse_post_file  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
FONTS = REPO / "assets" / "fonts"
IMAGES = REPO / "images"

W, H = 1080, 1350
MARGINE = 80
LARGHEZZA = W - 2 * MARGINE

# Carta avorio, inchiostro quasi nero, un accento terracotta.
SFONDO = (244, 242, 236)
INCHIOSTRO = (20, 20, 19)
SECONDARIO = (94, 93, 89)
LINEA = (205, 202, 192)
OMBRA = (228, 225, 216)
CARTA = (234, 231, 222)
CREMA = (252, 251, 248)
ARGILLA = (217, 119, 87)
ARGILLA_SCURA = (178, 88, 60)
ARGILLA_CHIARA = (251, 232, 222)
KRAFT = (212, 178, 140)
KRAFT_SCURO = (176, 141, 103)
KRAFT_CHIARO = (246, 239, 228)
TRATTO = 3

MODELLI = ("numero", "confronto", "frase")
ALT_MAX = 300   # LinkedIn ne accetta 4.086, ne consiglia meno di 120
CUBI_MAX = 24   # la pila più alta del confronto
COS30 = math.cos(math.radians(30))

TITOLO = "InterDisplay-ExtraBold"
VALORE = "InterDisplay-Bold"
ETICHETTA = "Inter-SemiBold"
SERIF = "SourceSerif4Subhead-Regular"
SERIF_TESTO = "SourceSerif4-Regular"


class ErroreImmagine(ValueError):
    """Blocco `immagine:` incompleto o testo che non entra nello spazio."""


def font(nome: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(FONTS / f"{nome}.ttf"), size)


def larghezza(draw: ImageDraw.ImageDraw, testo: str, f) -> int:
    return int(draw.textlength(testo, font=f))


def a_capo(draw, testo: str, f, max_w: int) -> list:
    """Spezza il testo in righe che stanno in max_w pixel, senza tagliare parole."""
    righe = []
    for paragrafo in str(testo).split("\n"):
        corrente = ""
        for parola in paragrafo.split():
            prova = f"{corrente} {parola}".strip()
            if larghezza(draw, prova, f) <= max_w:
                corrente = prova
                continue
            if corrente:
                righe.append(corrente)
            if larghezza(draw, parola, f) > max_w:
                raise ErroreImmagine(f"la parola «{parola}» è troppo lunga per una riga")
            corrente = parola
        righe.append(corrente)
    return righe


def bilancia(draw, testo: str, f, max_w: int) -> list:
    """Stesso numero di righe, ma lunghe il più possibile uguali: evita l'ultima
    riga con una parola sola («Cosa compri con 1 / dollaro»)."""
    righe = a_capo(draw, testo, f, max_w)
    if len(righe) < 2:
        return righe
    basso, alto = max_w // 2, max_w
    while basso < alto:
        medio = (basso + alto) // 2
        try:
            prova = a_capo(draw, testo, f, medio)
        except ErroreImmagine:
            prova = None
        if prova is not None and len(prova) == len(righe):
            alto = medio
        else:
            basso = medio + 1
    return a_capo(draw, testo, f, alto)


def adatta(draw, testo: str, nome_font: str, sizes, max_w: int, max_righe: int, campo: str):
    """Prova le dimensioni dalla più grande e tiene la prima in cui il testo sta."""
    sizes = list(sizes)
    for n, size in enumerate(sizes):
        f = font(nome_font, size)
        try:
            righe = bilancia(draw, testo, f, max_w)
        except ErroreImmagine:
            continue
        if len(righe) > max_righe:
            continue
        # Una parola corta da sola sull'ultima riga («rispiegare chi / sei») si
        # legge male: meglio scendere di corpo, finché ci sono corpi da provare.
        orfana = (len(righe) > 1 and " " not in righe[-1]
                  and larghezza(draw, righe[-1], f) < max_w * 0.35)
        if orfana and n < len(sizes) - 1:
            continue
        return f, righe
    raise ErroreImmagine(
        f"«{campo}» non sta in {max_righe} righe nemmeno al corpo più piccolo: accorcialo"
    )


def scrivi(draw, xy, righe, f, colore, interlinea=1.12, centro=False) -> int:
    """Disegna le righe dall'alto e restituisce la y sotto l'ultima."""
    x, y = xy
    passo = int(f.size * interlinea)
    for riga in righe:
        rx = x - larghezza(draw, riga, f) // 2 if centro else x
        draw.text((rx, y), riga, font=f, fill=colore)
        y += passo
    return y


def spaziato(draw, xy, testo: str, f, colore, spazio: int = 4) -> int:
    """Testo maiuscolo con un po' d'aria fra le lettere. Restituisce la x finale."""
    x, y = xy
    for ch in testo:
        draw.text((x, y), ch, font=f, fill=colore)
        x += larghezza(draw, ch, f) + spazio
    return x


def campo(dati: dict, nome: str, obbligatorio: bool = True) -> str:
    valore = dati.get(nome)
    if valore is None or str(valore).strip() == "":
        if obbligatorio:
            raise ErroreImmagine(f"manca il campo «{nome}»")
        return ""
    return str(valore).strip()


def valida(dati) -> dict:
    if not isinstance(dati, dict):
        raise ErroreImmagine("`immagine:` deve essere un blocco di campi, non una riga sola")
    modello = campo(dati, "modello")
    if modello not in MODELLI:
        raise ErroreImmagine(f"modello «{modello}» sconosciuto: usa {', '.join(MODELLI)}")
    campo(dati, "titolo")
    alt = campo(dati, "alt")
    if len(alt) > ALT_MAX:
        raise ErroreImmagine(f"«alt» di {len(alt)} caratteri, il massimo è {ALT_MAX}")
    if modello == "numero":
        campo(dati, "numero")
        campo(dati, "didascalia")
    elif modello == "frase":
        campo(dati, "frase")
    else:
        voci = dati.get("voci")
        if not isinstance(voci, list) or not 2 <= len(voci) <= 4:
            raise ErroreImmagine("«voci» deve avere da 2 a 4 elementi")
        for i, voce in enumerate(voci, 1):
            if not isinstance(voce, dict):
                raise ErroreImmagine(f"la voce {i} deve avere nome, valore e testo")
            campo(voce, "nome")
            campo(voce, "testo")
            try:
                if float(voce.get("valore")) <= 0:
                    raise ValueError
            except (TypeError, ValueError):
                raise ErroreImmagine(f"la voce {i} ha «valore» non numerico o non positivo") from None
        if sum(1 for v in voci if v.get("evidenza")) > 1:
            raise ErroreImmagine("al massimo una voce con «evidenza: true»")
    return dati


# --- cubi isometrici --------------------------------------------------------------

def proietta(ox, oy, s, x, y, z):
    return (ox + (x - y) * s * COS30, oy + (x + y) * s * 0.5 - z * s)


def cubo(draw, ox, oy, s, i, j, k, colori) -> None:
    """Un cubo con lo spigolo posteriore in basso in (i, j, k). Si vedono tre facce:
    sopra, destra (verso +i) e sinistra (verso +j)."""
    sopra, sinistra, destra = colori
    p = lambda x, y, z: proietta(ox, oy, s, x, y, z)  # noqa: E731
    facce = [
        ([p(i, j, k + 1), p(i + 1, j, k + 1), p(i + 1, j + 1, k + 1), p(i, j + 1, k + 1)], sopra),
        ([p(i + 1, j, k), p(i + 1, j + 1, k), p(i + 1, j + 1, k + 1), p(i + 1, j, k + 1)], destra),
        ([p(i, j + 1, k), p(i + 1, j + 1, k), p(i + 1, j + 1, k + 1), p(i, j + 1, k + 1)], sinistra),
    ]
    for poligono, colore in facce:
        draw.polygon(poligono, fill=colore, outline=INCHIOSTRO, width=TRATTO)


def pila(n: int):
    """Posizioni di n cubi impilati come scatole: strati da 3x2 riempiti dal basso,
    e nello strato in cima prima la fila dietro, così la pila sale a gradini."""
    larg, prof = (n, 1) if n <= 3 else (3, 2)
    pos = []
    for idx in range(n):
        strato, resto = divmod(idx, larg * prof)
        j, i = divmod(resto, larg)
        pos.append((i, j, strato))
    return pos, larg, prof


def dimensioni_pila(n: int, s: float):
    _, larg, prof = pila(n)
    strati = math.ceil(n / (larg * prof))
    return (larg + prof) * s * COS30, strati * s + (larg + prof) * s * 0.5


def disegna_pila(draw, cx: float, base_y: float, s: float, n: int, colori) -> None:
    """Disegna la pila centrata in cx, appoggiata alla linea base_y, con l'ombra."""
    pos, larg, prof = pila(n)
    w_pila, _ = dimensioni_pila(n, s)
    draw.ellipse((cx - w_pila * 0.62, base_y - s * 0.32, cx + w_pila * 0.62, base_y + s * 0.32),
                 fill=OMBRA)
    ox = cx - (larg - prof) / 2 * s * COS30
    oy = base_y - (larg + prof) * s * 0.5
    for i, j, k in sorted(pos, key=lambda t: (t[0] + t[1] + t[2], t[2])):
        cubo(draw, ox, oy, s, i, j, k, colori)


COLORI_EVIDENZA = (ARGILLA_CHIARA, ARGILLA, ARGILLA_SCURA)
COLORI_NORMALI = (KRAFT_CHIARO, KRAFT, KRAFT_SCURO)


def motivo(draw, x_destra: float, base_y: float, s: float) -> None:
    """Quattro cubi in mucchio: il segno che lega le immagini fra loro."""
    pos = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)]
    # Occupa 4s in altezza: da base_y - 4s (spigolo in cima) a base_y.
    ox = x_destra - 2 * s * COS30
    oy = base_y - 2 * s
    for i, j, k in sorted(pos, key=lambda t: (t[0] + t[1] + t[2], t[2])):
        cubo(draw, ox, oy, s, i, j, k, COLORI_EVIDENZA if (i, j, k) == (0, 0, 1)
             else COLORI_NORMALI)


# --- modelli ----------------------------------------------------------------------

def corpo_numero(draw, dati, y0: int, y1: int, cubi: bool = True) -> None:
    pad = 56
    draw.rounded_rectangle((MARGINE, y0, W - MARGINE, y1), radius=40,
                           fill=CARTA, outline=INCHIOSTRO, width=TRATTO)
    interno = LARGHEZZA - 2 * pad
    f_num, righe_num = adatta(draw, campo(dati, "numero"), TITOLO,
                              range(320, 99, -10), interno, 1, "numero")
    f_did, righe_did = adatta(draw, campo(dati, "didascalia"), SERIF,
                              range(44, 29, -2), interno, 3, "didascalia")
    passo_did = int(f_did.size * 1.25)
    alto_did = passo_did * len(righe_did)
    bbox = f_num.getbbox(righe_num[0])
    alto_num = bbox[3] - bbox[1]
    y_did = y1 - pad - alto_did
    y_num = y_did - 40 - alto_num
    draw.text((MARGINE + pad, y_num - bbox[1]), righe_num[0], font=f_num, fill=ARGILLA)
    scrivi(draw, (MARGINE + pad, y_did), righe_did, f_did, INCHIOSTRO, 1.25)
    # Il motivo dei cubi in alto a destra, se c'è posto sopra il numero. Il
    # carosello lo spegne: lì i cubi restano solo nei confronti.
    s = 54
    if cubi and y_num - (y0 + pad) > 4 * s + 24:
        motivo(draw, W - MARGINE - pad, y0 + pad + 4 * s, s)


def corpo_confronto(draw, dati, y0: int, y1: int) -> None:
    voci = dati["voci"]
    n = len(voci)
    massimo = max(float(v["valore"]) for v in voci)
    cubi = [max(1, round(CUBI_MAX * float(v["valore"]) / massimo)) for v in voci]
    colonna = LARGHEZZA / n

    # Riga dei numeri sotto le pile: nome con le grazie, valore in grassetto.
    f_nome = font(SERIF, 34)
    alto_righe = 34 + 14 + 84
    base_y = y1 - alto_righe - 56

    # Il lato del cubo è lo stesso per tutte le pile, così le quantità si confrontano.
    alto_max = base_y - y0 - 20
    s = 64.0
    while s > 14:
        w_p, h_p = dimensioni_pila(max(cubi), s)
        if w_p <= colonna * 0.82 and h_p + s * 0.32 <= alto_max:
            break
        s -= 2

    for idx, (voce, n_cubi) in enumerate(zip(voci, cubi)):
        evidenza = bool(voce.get("evidenza"))
        cx = MARGINE + colonna * (idx + 0.5)
        disegna_pila(draw, cx, base_y, s, n_cubi, COLORI_EVIDENZA if evidenza else COLORI_NORMALI)

        nome, testo = campo(voce, "nome"), campo(voce, "testo")
        max_w = int(colonna - 24)
        if larghezza(draw, nome, f_nome) > max_w:
            raise ErroreImmagine(f"il nome «{nome}» non sta nella colonna: accorcialo")
        y_righe = base_y + 56
        # Nome e valore centrati sotto la propria pila.
        draw.text((cx - larghezza(draw, nome, f_nome) / 2, y_righe), nome,
                  font=f_nome, fill=SECONDARIO)
        sizes = range(84, 39, -4) if evidenza else range(52, 31, -2)
        f_val = None
        for size in sizes:
            if larghezza(draw, testo, font(VALORE, size)) <= max_w:
                f_val = font(VALORE, size)
                break
        if f_val is None:
            raise ErroreImmagine(f"il valore «{testo}» non sta nella colonna: accorcialo")
        draw.text((cx - larghezza(draw, testo, f_val) / 2, y_righe + 34 + 14), testo, font=f_val,
                  fill=ARGILLA if evidenza else INCHIOSTRO)


def corpo_frase(draw, dati, y0: int, y1: int) -> None:
    pad = 52
    f_lab = font(ETICHETTA, 26)
    f_fr, righe = adatta(draw, f"“{campo(dati, 'frase')}”", SERIF,
                         range(50, 31, -2), LARGHEZZA - 2 * pad - 40, 7, "frase")
    passo = int(f_fr.size * 1.3)
    alto = passo * len(righe) + 2 * pad
    s = 40
    spazio_motivo = 4 * s + 20
    y = y0 + max(0, (y1 - y0 - alto - 56 - spazio_motivo) // 2)
    spaziato(draw, (MARGINE, y), "SCRIVI COSÌ", f_lab, SECONDARIO, 4)
    y += 56
    # Fumetto con la coda in basso a sinistra.
    bordo = (MARGINE, y, W - MARGINE - 40, y + alto)
    coda = [(MARGINE + 64, y + alto - 4), (MARGINE + 52, y + alto + 54), (MARGINE + 136, y + alto - 4)]
    draw.polygon(coda, fill=CREMA, outline=INCHIOSTRO, width=TRATTO)
    draw.rounded_rectangle(bordo, radius=36, fill=CREMA, outline=INCHIOSTRO, width=TRATTO)
    # Cancella il bordo del fumetto dove si attacca la coda.
    draw.rectangle((coda[0][0] + 3, y + alto - TRATTO - 1, coda[2][0] - 4, y + alto + 1), fill=CREMA)
    scrivi(draw, (MARGINE + pad, y + pad - 6), righe, f_fr, INCHIOSTRO, 1.3)
    motivo(draw, W - MARGINE, y + alto + spazio_motivo, s)


CORPI = {"numero": corpo_numero, "confronto": corpo_confronto, "frase": corpo_frase}


def disegna(dati: dict) -> Image.Image:
    dati = valida(dati)
    img = Image.new("RGB", (W, H), SFONDO)
    draw = ImageDraw.Draw(img)

    # Niente etichetta sopra e niente nome sotto (dal 2026-10-19): il titolo apre
    # l'immagine e il nome di Marco è già sopra il post. Un campo `etichetta`
    # rimasto in un post vecchio viene ignorato.
    y = MARGINE

    f_tit, righe_tit = adatta(draw, campo(dati, "titolo"), TITOLO,
                              range(124, 71, -4), LARGHEZZA, 3, "titolo")
    y = scrivi(draw, (MARGINE - 4, y), righe_tit, f_tit, INCHIOSTRO, 1.02)

    sottotitolo = campo(dati, "sottotitolo", obbligatorio=False)
    if sottotitolo:
        f_sot, righe_sot = adatta(draw, sottotitolo, SERIF,
                                  range(46, 31, -2), LARGHEZZA, 3, "sottotitolo")
        y = scrivi(draw, (MARGINE, y + 26), righe_sot, f_sot, INCHIOSTRO, 1.22)

    # Piede, solo se c'è una fonte: linea sottile e fonte con le grazie. Senza
    # fonte (un conto fatto nel post) il disegno scende fino al margine.
    fondo = H - MARGINE
    fonte = campo(dati, "fonte", obbligatorio=False)
    if fonte:
        piede_y = H - MARGINE - 22
        f_piede = font(SERIF_TESTO, 27)
        fonte = fonte.removeprefix("https://").removeprefix("http://").removeprefix("www.")
        testo_fonte = f"Fonte: {fonte}"
        if larghezza(draw, testo_fonte, f_piede) > LARGHEZZA:
            raise ErroreImmagine("«fonte» troppo lunga per il piede: metti solo il dominio")
        draw.line((MARGINE, piede_y - 30, W - MARGINE, piede_y - 30), fill=LINEA, width=2)
        draw.text((MARGINE, piede_y), testo_fonte, font=f_piede, fill=SECONDARIO)
        fondo = piede_y - 70

    CORPI[dati["modello"]](draw, dati, y + 56, fondo)
    return img


def percorso_immagine(post: Path) -> Path:
    return IMAGES / f"{post.stem}.png"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("post", help="file del post, es. approved/2026-10-20.md")
    parser.add_argument("--out", help="dove salvare il PNG (default images/<data>.png)")
    args = parser.parse_args(argv)

    post = Path(args.post)
    meta = parse_post_file(str(post))["meta"] or {}
    if "immagine" not in meta:
        print(f"{post}: nessun blocco immagine, niente da disegnare")
        return 0
    try:
        img = disegna(meta["immagine"])
    except ErroreImmagine as e:
        print(f"{post}\n  ! immagine: {e}")
        return 1
    out = Path(args.out) if args.out else percorso_immagine(post)
    out.parent.mkdir(parents=True, exist_ok=True)
    img.save(out, "PNG", optimize=True)
    print(f"{post}\n  OK: immagine salvata in {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
