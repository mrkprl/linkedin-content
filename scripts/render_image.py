#!/usr/bin/env python3
"""Disegna l'infografica di un post a partire dal blocco `immagine:` del frontmatter.

Uso:
    python scripts/render_image.py approved/2026-10-20.md
    python scripts/render_image.py approved/2026-10-20.md --out /tmp/prova.png

Scrive images/<data>.png (1080x1350, 4:5: il formato che occupa più spazio nel feed
da telefono). Esce con 0 se ha disegnato l'immagine o se il post non ne ha una,
con 1 se il blocco è sbagliato o il testo non ci sta: in quel caso stampa cosa
correggere, come readability.py.

Tre modelli, scelti dal campo `modello`:
- numero:    un dato grande al centro (es. "2 ore") con la didascalia sotto
- confronto: da 2 a 4 voci con una barra proporzionale al valore, una in evidenza
- frase:     la frase esatta da scrivere all'assistente, dentro un fumetto

I numeri seguono le regole di STYLE.md: presi dalla fonte o da un conto con le
ipotesi dichiarate nel post. Lo script non li verifica, li disegna.
"""

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent))
from publish import parse_post_file  # noqa: E402

REPO = Path(__file__).resolve().parent.parent
FONTS = REPO / "assets" / "fonts"
IMAGES = REPO / "images"

W, H = 1080, 1350
MARGINE = 88
LARGHEZZA = W - 2 * MARGINE

# Bianco su nero, un solo colore d'accento: quello che conta si riconosce subito.
SFONDO = (11, 11, 12)
TESTO = (245, 245, 247)
GRIGIO = (161, 161, 166)
GRIGIO_SCURO = (58, 58, 60)
SUPERFICIE = (28, 28, 30)
ACCENTO = (41, 151, 255)

AUTORE = "Marco Parolin"
MODELLI = ("numero", "confronto", "frase")
ALT_MAX = 300  # LinkedIn ne accetta 4.086, ne consiglia meno di 120


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
    for size in sizes:
        f = font(nome_font, size)
        try:
            righe = bilancia(draw, testo, f, max_w)
        except ErroreImmagine:
            continue
        if len(righe) <= max_righe:
            return f, righe
    raise ErroreImmagine(
        f"«{campo}» non sta in {max_righe} righe nemmeno al corpo più piccolo: accorcialo"
    )


def scrivi(draw, xy, righe, f, colore, interlinea=1.12) -> int:
    """Disegna le righe dall'alto e restituisce la y sotto l'ultima."""
    x, y = xy
    passo = int(f.size * interlinea)
    for riga in righe:
        draw.text((x, y), riga, font=f, fill=colore)
        y += passo
    return y


def spaziato(draw, xy, testo: str, f, colore, spazio: int = 4) -> None:
    """Testo in maiuscolo con un po' di aria fra le lettere, per l'etichetta."""
    x, y = xy
    for ch in testo:
        draw.text((x, y), ch, font=f, fill=colore)
        x += larghezza(draw, ch, f) + spazio


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
                if float(voce.get("valore")) < 0:
                    raise ValueError
            except (TypeError, ValueError):
                raise ErroreImmagine(f"la voce {i} ha «valore» non numerico o negativo") from None
        if sum(1 for v in voci if v.get("evidenza")) > 1:
            raise ErroreImmagine("al massimo una voce con «evidenza: true»")
    return dati


# --- modelli ---------------------------------------------------------------------

def corpo_numero(draw, dati, y0: int, y1: int) -> None:
    f_num, righe_num = adatta(draw, campo(dati, "numero"), "InterDisplay-ExtraBold",
                              range(300, 119, -12), LARGHEZZA, 1, "numero")
    f_did, righe_did = adatta(draw, campo(dati, "didascalia"), "Inter-Medium",
                              range(44, 31, -2), LARGHEZZA, 3, "didascalia")
    alto_num = int(f_num.size * 1.0)
    alto_did = int(f_did.size * 1.25) * len(righe_did)
    y = y0 + max(0, (y1 - y0 - alto_num - 36 - alto_did) // 2)
    # Il bordo superiore del glifo sta sotto la y di disegno: lo si compensa.
    sopra = f_num.getbbox(righe_num[0])[1]
    draw.text((MARGINE, y - sopra), righe_num[0], font=f_num, fill=ACCENTO)
    scrivi(draw, (MARGINE, y + alto_num + 36), righe_did, f_did, TESTO, 1.25)


def corpo_confronto(draw, dati, y0: int, y1: int) -> None:
    voci = dati["voci"]
    massimo = max(float(v["valore"]) for v in voci) or 1.0
    f_nome = font("Inter-Medium", 38)
    f_val = font("InterDisplay-Bold", 56)
    passo = min(170, (y1 - y0) // len(voci))
    y = y0 + max(0, (y1 - y0 - passo * len(voci)) // 2)
    for voce in voci:
        evidenza = bool(voce.get("evidenza"))
        nome, testo = campo(voce, "nome"), campo(voce, "testo")
        w_val = larghezza(draw, testo, f_val)
        if larghezza(draw, nome, f_nome) + w_val + 32 > LARGHEZZA:
            raise ErroreImmagine(f"la voce «{nome}» con «{testo}» non sta su una riga: accorciala")
        draw.text((MARGINE, y + 14), nome, font=f_nome, fill=TESTO if evidenza else GRIGIO)
        draw.text((W - MARGINE - w_val, y), testo, font=f_val,
                  fill=ACCENTO if evidenza else TESTO)
        barra_y = y + 84
        draw.rounded_rectangle((MARGINE, barra_y, W - MARGINE, barra_y + 22),
                               radius=11, fill=SUPERFICIE)
        lungo = max(22, int(LARGHEZZA * float(voce["valore"]) / massimo))
        draw.rounded_rectangle((MARGINE, barra_y, MARGINE + lungo, barra_y + 22),
                               radius=11, fill=ACCENTO if evidenza else GRIGIO_SCURO)
        y += passo


def corpo_frase(draw, dati, y0: int, y1: int) -> None:
    interno = 56
    f_lab = font("Inter-SemiBold", 30)
    f_fr, righe = adatta(draw, f"“{campo(dati, 'frase')}”", "Inter-Medium",
                         range(52, 33, -2), LARGHEZZA - 2 * interno, 8, "frase")
    alto_testo = int(f_fr.size * 1.3) * len(righe)
    alto = alto_testo + 2 * interno
    y = y0 + max(0, (y1 - y0 - alto - 56) // 2)
    spaziato(draw, (MARGINE, y), "SCRIVI COSÌ", f_lab, GRIGIO)
    y += 56
    draw.rounded_rectangle((MARGINE, y, W - MARGINE, y + alto), radius=36,
                           fill=SUPERFICIE, outline=ACCENTO, width=3)
    scrivi(draw, (MARGINE + interno, y + interno - 4), righe, f_fr, TESTO, 1.3)


CORPI = {"numero": corpo_numero, "confronto": corpo_confronto, "frase": corpo_frase}


def disegna(dati: dict) -> Image.Image:
    dati = valida(dati)
    img = Image.new("RGB", (W, H), SFONDO)
    draw = ImageDraw.Draw(img)

    y = MARGINE
    etichetta = campo(dati, "etichetta", obbligatorio=False).upper()
    if etichetta:
        f_et = font("Inter-SemiBold", 28)
        if larghezza(draw, etichetta, f_et) + 4 * len(etichetta) > LARGHEZZA:
            raise ErroreImmagine("«etichetta» troppo lunga: bastano due o tre parole")
        spaziato(draw, (MARGINE, y), etichetta, f_et, ACCENTO)
        y += 72

    f_tit, righe_tit = adatta(draw, campo(dati, "titolo"), "InterDisplay-Bold",
                              range(96, 63, -4), LARGHEZZA, 3, "titolo")
    y = scrivi(draw, (MARGINE, y), righe_tit, f_tit, TESTO, 1.08)

    sottotitolo = campo(dati, "sottotitolo", obbligatorio=False)
    if sottotitolo:
        f_sot, righe_sot = adatta(draw, sottotitolo, "Inter-Regular",
                                  range(40, 29, -2), LARGHEZZA, 3, "sottotitolo")
        y = scrivi(draw, (MARGINE, y + 36), righe_sot, f_sot, GRIGIO, 1.25)

    # Piede: linea sottile, fonte a sinistra, nome a destra.
    piede_y = H - MARGINE - 30
    draw.line((MARGINE, piede_y - 32, W - MARGINE, piede_y - 32), fill=GRIGIO_SCURO, width=2)
    f_piede = font("Inter-Medium", 26)
    f_autore = font("Inter-SemiBold", 26)
    w_autore = larghezza(draw, AUTORE, f_autore)
    draw.text((W - MARGINE - w_autore, piede_y), AUTORE, font=f_autore, fill=TESTO)
    fonte = campo(dati, "fonte", obbligatorio=False)
    if fonte:
        fonte = fonte.removeprefix("https://").removeprefix("http://").removeprefix("www.")
        testo_fonte = f"Fonte: {fonte}"
        if larghezza(draw, testo_fonte, f_piede) > LARGHEZZA - w_autore - 40:
            raise ErroreImmagine("«fonte» troppo lunga per il piede: metti solo il dominio")
        draw.text((MARGINE, piede_y), testo_fonte, font=f_piede, fill=GRIGIO)

    CORPI[dati["modello"]](draw, dati, y + 64, piede_y - 80)
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
