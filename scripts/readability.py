#!/usr/bin/env python3
"""Misura la leggibilità di un post e i segnali di scrittura artificiosa.

Le soglie vengono dalle fonti citate in SETUP.md. Gulpease è la formula tarata
sull'italiano (Lucisano e Piemontese, 1988): usa le lettere invece delle sillabe,
quindi si calcola senza sillabazione.
"""

import re

PAROLA = re.compile(r"[0-9A-Za-zÀ-ÖØ-öø-ÿ']+")
NON_ALFANUM = re.compile(r"[^0-9A-Za-zÀ-ÖØ-öø-ÿ]")
FINE_FRASE = re.compile(r"[.!?;:]+")
EMOJI = re.compile("[\U0001F000-\U0001FAFF☀-➿⬀-⯿️]")
HASHTAG_RE = re.compile(r"#\w+")

# Soglie: vedi SETUP.md per la fonte di ciascuna.
GULPEASE_MIN = 60          # sotto: non leggibile in autonomia con la licenza media
PAROLE_PER_FRASE_MAX = 25  # Direttiva 8/5/2002 regola 1; Cortelazzo regola 12
MEDIA_PAROLE_MAX = 18
HOOK_MAX_CHARS = 60        # la prima riga è anche lo slug dell'URL del post
HOOK_CONSIGLIATO = 40      # sotto i 40 caratteri l'engagement rate è ~25% più alto
# Formato corto dal 2026-10-19 (scelta di Marco, vedi SETUP.md): prima 1600-2600
# di tolleranza e almeno 20 paragrafi.
CARATTERI_MIN = 900        # target di scrittura 1000-1400 coda compresa, qui la banda di tolleranza
CARATTERI_MAX = 1500       # oltre i 3000 LinkedIn rifiuta il post
BLOCCHI_MIN = 6            # sotto: 0-5 paragrafi valgono 0,70x reach
BLOCCHI_MAX = 10           # sopra, in 1.200 caratteri, si torna a una frase per blocco
PARAGRAFO_MAX_CHARS = 260  # oltre, il blocco è un muro di testo sul telefono
# Il post corto regge su un dato concreto, se la fonte ne ha uno. "sei" è escluso
# perché in italiano è quasi sempre il verbo.
NUMERO = re.compile(
    r"\d|\b(?:due|tre|quattro|cinque|sette|otto|nove|dieci|undici|dodici|quindici|"
    r"venti|trenta|quaranta|cinquanta|cento|mille|milion[ei]|miliard[oi]|metà|"
    r"decimo|doppio|triplo)\b", re.I)
EMOJI_MAX = 1              # da 0 a 1 emoji: +22% reach. Oltre, l'effetto è piatto
HASHTAG_MAX = 3
ATTENUATORI_MAX = 2        # oltre, il testo non afferma più niente
RIGA_BREVE = 40            # una riga sotto i 40 caratteri è un colpo di ritmo
QUOTA_RIGHE_BREVI = 0.10   # sotto: tutti i blocchi sono lunghi uguali, suona da notiziario
                           # (0,15 fino al 2026-10-18: nel formato corto le righe brevi sono
                           # hook, chiusura e domanda, e spezzare il resto lo farebbe ansimare)
QUOTA_BLOCCHI_MONORIGA = 0.50  # sopra: una frase per blocco, cioè un elenco travestito da post
BLOCCO = re.compile(r"\n\s*\n")  # su LinkedIn il blocco è ciò che sta fra due righe vuote

# Costrutti che fanno "suonare" il testo come generato da un modello.
STILEMI = [
    (re.compile(r"—"), "trattino lungo"),
    (re.compile(r"→"), "freccia"),
    (re.compile(r"\bnon (?:è |si tratta )?(?:solo|soltanto|più) (?:una |un |di )?\w+[,.]? ma\b", re.I),
     "costrutto 'non solo X ma Y'"),
    (re.compile(r"\bnon è (?:più )?(?:una )?questione di\b", re.I), "formula 'non è questione di'"),
    (re.compile(r"\bin un (?:mondo|'?epoca|era) in cui\b", re.I), "attacco 'in un mondo in cui'"),
    (re.compile(r"\bnell'era (?:dell|di)\w*\b", re.I), "attacco 'nell'era di'"),
    (re.compile(r"\bla vera domanda è\b", re.I), "formula 'la vera domanda è'"),
    (re.compile(r"\bnon è un caso che\b", re.I), "formula 'non è un caso che'"),
    (re.compile(r"\bed è qui che entra in gioco\b", re.I), "formula 'entra in gioco'"),
    (re.compile(r"\brappresenta un(?:a)? (?:vero|vera|svolta|punto)\b", re.I), "enfasi 'rappresenta una svolta'"),
    (re.compile(r"\bsi configura come\b|\bfunge da\b", re.I), "verbo gonfio al posto di 'è'"),
    (re.compile(r"\bnonostante (?:le difficoltà|tutto), \w+ continua\b", re.I), "chiusa formulaica"),
    # Dalla skill humanizer (.claude/skills/humanizer): i segnali più sicuri.
    (re.compile(r"\bnon si tratta (?:solo |soltanto )?di [^.!?\n]{1,60}[,;:.]\s*si tratta di\b", re.I),
     "contrasto 'non si tratta di X, si tratta di Y'"),
    (re.compile(r"\bè (?:importante|fondamentale|bene) (?:notare|sottolineare|ricordare)\b", re.I),
     "formula 'è importante notare'"),
    (re.compile(r"\b(?:in conclusione|in sintesi|per concludere)\b", re.I), "chiusa da tema 'in conclusione'"),
    (re.compile(r"\b(?:vediamo|scopriamo) insieme\b|\bimmergiamoci\b|\bfacciamo chiarezza\b|"
                r"\bandiamo con ordine\b|\becco cosa devi sapere\b", re.I), "rincorsa prima del punto"),
    (re.compile(r"\bspero (?:ti|vi) sia (?:stato )?utile\b|\bottima domanda\b", re.I), "residuo da chatbot"),
    (re.compile(r"\b(?:segna|segnano) una svolta\b|\bgioca(?:no)? un ruolo (?:chiave|cruciale|fondamentale)\b|"
                r"\bapre la strada a\b|\bgetta le basi\b|\bin continua evoluzione\b|\bgame[- ]?changer\b", re.I),
     "importanza gonfiata"),
]

# Parole che i modelli usano molto più delle persone (skill humanizer, §12):
# una sola non dice niente, due o più nello stesso post sì.
PAROLE_AI = re.compile(
    r"\b(?:fondamental[ei]|crucial[ei]|essenzial[ei]|potenzia\w*|sfrutta\w*|ottimizza\w*|"
    r"valorizza\w*|ecosistem[ai]|panoram[ai]|sinergi[ae]|approfondi\w*|innovativ[oaie]|"
    r"rivoluzionari\w*|testimonianz[ae]|a 360 gradi)\b", re.I)
GERUNDIO_APPESO = re.compile(
    r",\s*(?:sottolineando|evidenziando|garantendo|contribuendo|favorendo|rendendo possibile)\b", re.I)
ANTITESI = re.compile(r"\bnon è [^.!?\n]{1,40}[.;:,]\s*è\b", re.I)

# Aperture da quiz: l'hook a domanda è ultimo dei cinque tipi per engagement.
HOOK_FORMULE = re.compile(
    r"^\s*(?:sai (?:qual|che|come|cosa)|ti sei mai chiest|hai mai |cosa succede se|"
    r"e se ti dicessi|lo sapevi|immagina (?:di|che|per un))", re.I)

# La glossa didascalica è il tratto che fa suonare il testo come un tema di scuola:
# presuppone un lettore che non capisce. Al suo posto va un esempio concreto.
GLOSSE = re.compile(
    r"\b(?:cioè|ovvero|vale a dire|in altre parole|in parole povere|"
    r"per chi non lo sapesse|per intenderci|in pratica si tratta)\b", re.I)

# Attenuatori: uno o due danno il parlato, cinque tolgono ogni affermazione.
ATTENUATORI = re.compile(
    r"\b(?:un po'|un filo di|onestamente|sinceramente|in un certo senso|"
    r"diciamo che|forse|magari|abbastanza|piuttosto|più o meno|"
    r"in qualche modo|tutto sommato)\b", re.I)

# CTA generica: LinkedIn la classifica come engagement bait e ne riduce la portata.
CTA_GENERICA = re.compile(
    r"(?:sei d'accordo|che ne pensi|fammi sapere|dimmi la tua|scrivilo (?:qui )?nei commenti|"
    r"cosa ne pensate|👇)", re.I)


def gulpease(testo: str) -> float:
    """89 + (300*frasi - 10*lettere) / parole. Scala 0-100, 100 = più leggibile."""
    parole_lista = PAROLA.findall(testo)
    if not parole_lista:
        return 0.0
    lettere = sum(len(NON_ALFANUM.sub("", p)) for p in parole_lista)
    t = testo.strip()
    frasi = max(len(FINE_FRASE.findall(t)) + (0 if FINE_FRASE.search(t[-1:]) else 1), 1)
    return 89 + (300 * frasi - 10 * lettere) / len(parole_lista)


def analizza(testo: str) -> dict:
    righe = [r for r in testo.split("\n")]
    paragrafi = [r.strip() for r in righe if r.strip()]
    # La coda (nota fra parentesi, hashtag) è mono-riga per costruzione: contarla
    # gonfierebbe la frammentazione di ogni post ben scritto.
    blocchi = [b.strip() for b in BLOCCO.split(testo.strip()) if b.strip()
               and not b.strip().startswith(("#", "("))]
    frasi = [f.strip() for f in re.split(r"[.!?;:\n]+", testo) if f.strip()]
    per_frase = [len(PAROLA.findall(f)) for f in frasi] or [0]

    return {
        "caratteri": len(testo),
        "parole": len(PAROLA.findall(testo)),
        "gulpease": round(gulpease(testo), 1),
        "paragrafi": len(paragrafi),
        "paragrafi_lunghi": [p for p in paragrafi if len(p) > PARAGRAFO_MAX_CHARS],
        "righe_brevi": [p for p in paragrafi if len(p) < RIGA_BREVE],
        "blocchi": blocchi,
        "blocchi_monoriga": [b for b in blocchi if "\n" not in b],
        "media_parole_frase": round(sum(per_frase) / len(per_frase), 1),
        "frase_piu_lunga": max(per_frase),
        "frasi_lunghe": [f for f, n in zip(frasi, per_frase) if n > PAROLE_PER_FRASE_MAX],
        "hook": righe[0].strip() if righe else "",
        "stilemi": [nome for pattern, nome in STILEMI if pattern.search(testo)],
        "emoji": EMOJI.findall(testo),
        "hashtag": HASHTAG_RE.findall(testo),
        "glosse": GLOSSE.findall(testo),
        "attenuatori": ATTENUATORI.findall(testo),
    }


def problemi(testo: str) -> list:
    """Violazioni delle soglie. Lista vuota = il testo passa."""
    m = analizza(testo)
    out = []

    if m["gulpease"] < GULPEASE_MIN:
        out.append(f"Gulpease {m['gulpease']} sotto {GULPEASE_MIN}: "
                   f"non si legge in autonomia con la licenza media")
    if m["media_parole_frase"] > MEDIA_PAROLE_MAX:
        out.append(f"media di {m['media_parole_frase']} parole per frase, il massimo è {MEDIA_PAROLE_MAX}")
    for f in m["frasi_lunghe"]:
        out.append(f"frase da {len(PAROLA.findall(f))} parole (max {PAROLE_PER_FRASE_MAX}): «{f[:70]}...»")
    if not m["hook"]:
        out.append("prima riga vuota: è l'hook e diventa lo slug dell'URL")
    elif len(m["hook"]) > HOOK_MAX_CHARS:
        out.append(f"hook di {len(m['hook'])} caratteri, il massimo è {HOOK_MAX_CHARS}")
    if m["hook"].startswith("#"):
        out.append("l'hook inizia con un hashtag: genera uno slug URL generico")
    if "?" in m["hook"]:
        out.append("hook a domanda: è l'ultimo dei cinque tipi per engagement, "
                   "va riscritto come affermazione")
    if HOOK_FORMULE.match(m["hook"]):
        out.append(f"hook da quiz: «{m['hook'][:40]}...» — apri con un fatto, non con un indovinello")
    if not (CARATTERI_MIN <= m["caratteri"] <= CARATTERI_MAX):
        out.append(f"{m['caratteri']} caratteri, fuori dalla fascia {CARATTERI_MIN}-{CARATTERI_MAX}")
    if len(m["blocchi"]) < BLOCCHI_MIN:
        out.append(f"solo {len(m['blocchi'])} blocchi (hook e domanda compresi): "
                   f"ne servono almeno {BLOCCHI_MIN}, separati da riga vuota")
    elif len(m["blocchi"]) > BLOCCHI_MAX:
        out.append(f"{len(m['blocchi'])} blocchi, il massimo è {BLOCCHI_MAX}: raggruppa in "
                   f"un blocco le 2-3 righe che portano avanti lo stesso pensiero")
    for p in m["paragrafi_lunghi"]:
        out.append(f"paragrafo da {len(p)} caratteri (max {PARAGRAFO_MAX_CHARS}), "
                   f"spezzalo: «{p[:60]}...»")
    if len(m["emoji"]) > EMOJI_MAX:
        out.append(f"{len(m['emoji'])} emoji ({''.join(m['emoji'])}), il massimo è {EMOJI_MAX}")
    if len(m["hashtag"]) > HASHTAG_MAX:
        out.append(f"{len(m['hashtag'])} hashtag, il massimo è {HASHTAG_MAX}")
    for g in set(x.lower() for x in m["glosse"]):
        out.append(f"glossa didascalica «{g}»: spiega con un esempio concreto, non con una definizione")
    if "http://" in testo or "https://" in testo:
        out.append("link nel corpo del post: costa circa il 27% di impression, va nel commento")
    for s in m["stilemi"]:
        out.append(f"stilema da testo generato: {s}")
    return out


def avvisi(testo: str) -> list:
    """Segnali di voce debole. Non bloccano, ma se compaiono il post suona finto."""
    m = analizza(testo)
    out = []

    if 0 < len(m["hook"]) <= HOOK_MAX_CHARS and len(m["hook"]) > HOOK_CONSIGLIATO:
        out.append(f"hook di {len(m['hook'])} caratteri: sotto {HOOK_CONSIGLIATO} rende di più")
    if len(m["attenuatori"]) > ATTENUATORI_MAX:
        out.append(f"{len(m['attenuatori'])} attenuatori ({', '.join(m['attenuatori'][:5])}): "
                   f"il testo non afferma più niente")
    if m["blocchi"] and len(m["blocchi_monoriga"]) / len(m["blocchi"]) > QUOTA_BLOCCHI_MONORIGA:
        quota = round(100 * len(m["blocchi_monoriga"]) / len(m["blocchi"]))
        out.append(f"testo frammentato: {quota}% dei blocchi è di una riga sola "
                   f"(nei post riusciti sta intorno al 33%). Raggruppa le frasi che "
                   f"portano avanti lo stesso pensiero: la riga isolata pesa solo se è rara")
    if m["paragrafi"] and len(m["righe_brevi"]) / m["paragrafi"] < QUOTA_RIGHE_BREVI:
        out.append(f"ritmo piatto: solo {len(m['righe_brevi'])} blocchi su {m['paragrafi']} "
                   f"sotto i {RIGA_BREVE} caratteri. Senza righe corte il post è un notiziario")
    if not NUMERO.search(testo):
        out.append("nessun numero: se la fonte ne ha uno (prezzo, limite, data) o se un conto "
                   "con le ipotesi dichiarate rende concreto il punto, usalo. Mai inventarlo: "
                   "senza un numero vero il post va bene così")
    if CTA_GENERICA.search(testo):
        out.append("chiusura da engagement bait: la domanda deve chiedere un'esperienza specifica")
    parole_ai = PAROLE_AI.findall(testo)
    if len(parole_ai) >= 2:
        out.append(f"parole da testo generato ({', '.join(parole_ai[:5])}): "
                   f"riscrivi con parole di tutti i giorni (skill humanizer, §12)")
    if GERUNDIO_APPESO.search(testo):
        out.append("gerundio appeso a un fatto (', garantendo...', ', sottolineando...'): "
                   "tieni il fatto e togli il gerundio (skill humanizer, §15)")
    antitesi = ANTITESI.findall(testo)
    if len(antitesi) > 1 or (antitesi and antitesi[0] not in testo.split("\n")[0]):
        out.append("contrasto 'non è X, è Y' fuori dall'hook: di' la cosa direttamente, "
                   "tienilo solo se corregge un'idea che chi legge ha davvero (skill humanizer, §1)")
    if re.search(r"^\s*P\.?S\.?[ :]", testo, re.M):
        out.append("firma con P.S.: la nota sull'automazione va tra parentesi, asciutta")
    return out


def main():
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from publish import parse_post_file

    uscita = 0
    for percorso in sys.argv[1:]:
        testo = parse_post_file(percorso)["text"]
        m = analizza(testo)
        print(f"\n{percorso}")
        print(f"  {m['caratteri']} caratteri · {m['parole']} parole · {m['paragrafi']} paragrafi")
        print(f"  Gulpease {m['gulpease']} · {m['media_parole_frase']} parole/frase "
              f"· frase più lunga {m['frase_piu_lunga']}")
        print(f"  {len(m['emoji'])} emoji · {len(m['hashtag'])} hashtag")
        print(f"  hook ({len(m['hook'])} car.): {m['hook'][:80]}")
        errori = problemi(testo)
        for p in errori:
            print(f"  ! {p}")
        for a in avvisi(testo):
            print(f"  ? {a}")
        if not errori:
            print("  OK: nessuna violazione")
        uscita |= bool(errori)
    return uscita


if __name__ == "__main__":
    # exit 1 se almeno un post viola una soglia: così la routine se ne accorge
    # senza dover leggere l'output. Nel workflow della PR il report è informativo
    # (`|| true`), qui l'uscita serve al generatore per riscrivere prima di pushare.
    raise SystemExit(main())
