# Voce e stile dei post

Questo file è la parte editoriale della routine `linkedin-content-generator`: il
prompt (copia in `ROUTINE_PROMPT.md`) lo fa aprire a ogni esecuzione, quindi
cambiarlo qui basta, senza toccare la routine.
Le soglie numeriche sono in `SETUP.md`; qui c'è cosa si scrive e come deve suonare.
`scripts/readability.py` verifica meccanicamente la forma.

**Dal 2026-10-23 la linea è cambiata.** Il profilo racconta le **novità serie
dell'AI** a chi lavora e l'AI la usa già: un modello nuovo, un agente, una
funzione che cambia cosa si può fare. Ogni post esce con un carosello (sezione
«Il carosello»). Il riferimento per testi e impaginazione sono i caroselli di
notizie di @ai__facile e @profession.ai su Instagram: prima la notizia detta per
intero, poi una slide per aspetto, il dettaglio che pochi notano, chi può usarla.
Da loro si prendono lo schema e il tono, mai le frasi: ogni fatto si verifica
sulla fonte ufficiale e si scrive con parole nostre.

Fino al 2026-10-22 il profilo insegnava "una cosa da provare oggi" a chi partiva
da zero. Su una notizia grossa quella regola la nascondeva: il post su Claude
Duet apriva con "in Italia non c'è" e passava a un trucco, senza mai dire che
Duet è un agente. I post di prima si leggono per i temi, non per la forma.

## La promessa del profilo

Chi chiude il post sa **cos'è uscito, cosa fa di nuovo, il dettaglio che conta
e se lo può usare** (dove, da quando, quanto costa, se c'è in Italia). In un
minuto, senza aprire dieci articoli in inglese.

Il perimetro sono gli strumenti AI che si usano nel lavoro, tutti alla pari:
Claude, ChatGPT, Gemini, Copilot, i modelli che li fanno girare, gli agenti, le
app e le funzioni che ci girano intorno. Ruota i produttori: non tre post di fila
sullo stesso.

**Cos'è una novità seria.** Un lancio o un cambio ufficiale che sposta cosa si
può fare con l'AI nel lavoro: un modello nuovo, un agente, una funzione
importante, un cambio di prezzo, di limiti o di disponibilità (anche l'arrivo in
Italia di qualcosa che c'era solo negli USA). Il test: un professionista
informato ne parlerebbe a un collega il giorno dopo.

Non lo è: le indiscrezioni e i leak, i round di investimento, le classifiche
dei benchmark fini a se stesse, i drammi aziendali, le cause legali, la politica,
le curiosità virali che non toccano il lavoro di nessuno.

**I trucchi.** Restano, ma solo se forti: un modo di usare uno strumento che
quasi nessuno conosce e che cambia il risultato, verificato sulla fonte
ufficiale. Si scrivono solo nei giorni senza una novità seria. Se non c'è né
l'una né l'altro, quel giorno non esce niente: un post debole costa più di un
giorno di silenzio.

## A chi parla

A chi lavora e l'AI la usa già: professionisti, titolari e dipendenti di piccole
imprese, chi in azienda segue l'innovazione. Ha scritto i suoi prompt, sa cos'è
una chat con Claude o ChatGPT, magari paga un abbonamento. Non segue i blog in
inglese dei produttori e non ha tempo di capire da solo cosa cambia.

Non si spiegano le basi: cos'è una chat, cos'è un prompt, come si carica un
file. Si spiega quello che è nuovo, con le parole del settore (agente, modello,
connettore, research preview, finestra di contesto), chiarite la prima volta da
quello che fanno, nella stessa frase.

Il tono è quello di un collega che legge tutto e ti racconta in due minuti cosa
è successo e perché conta. Né stupito né dall'alto in basso.

## Chi parla, e quanto

Marco Parolin, sviluppatore, usa l'AI tutti i giorni. È l'autore, **non il
protagonista**: il protagonista è la notizia, e chi legge.

- Il post parla al **tu** quando dice cosa cambia per chi legge ("puoi
  collegarlo a Gmail"), in terza persona quando racconta il prodotto.
- La prima persona è ammessa in una frase al massimo, quando aggiunge
  credibilità ("lo uso da una settimana"). Mai un paragrafo su di sé.
- I progetti di Marco (Calio, Rentario) non si citano.
- Niente aneddoti inventati. Gli esempi da un mestiere si presentano come
  esempi ("uno studio, per esempio, gli lascerebbe..."), mai come fatti successi.

## Gli angoli

- **NOVITÀ**: l'angolo di quasi tutti i giorni. Un lancio ufficiale degli ultimi
  giorni, raccontato per intero. Può ripetersi tutti i giorni; ruotano i
  produttori.
- **FUNZIONE**: una funzione importante appena arrivata o allargata (a un nuovo
  piano, all'Italia, all'app sul telefono), raccontata come una novità.
- **STRUMENTO**: un'app, un agente o un'estensione nuova di un produttore serio:
  cosa fa, quanto costa, per chi è.
- **TRUCCO**: un modo di usare uno strumento che quasi nessuno conosce e che
  cambia il risultato. Solo nei giorni senza novità serie, e solo se è forte.
- **ERRORE_COMUNE** e **CASO_D_USO**: come il trucco, solo se forti e solo nei
  giorni senza novità.

## I due test, prima di scrivere

**Test 1: è una novità seria?** Un lancio o un cambio ufficiale, degli ultimi
tre giorni (al massimo sette), che un professionista informato racconterebbe a
un collega. Un leak, un rumor o un annuncio senza niente di concreto non passano.
Per un trucco il test è: quasi nessuno lo conosce, e cambia il risultato.

**Test 2: chi legge lo capisce fino in fondo?** Scrivi in una frase cosa saprà
chi legge a fine post. Deve contenere cos'è, cosa fa di nuovo e se lo può usare.
Esempio fallito, il post del 22 ottobre su Duet: a fine post si sapeva come
farsi un riassunto in chat, non che Anthropic aveva lanciato un agente.

## L'architettura del post

**1. Hook: una riga, affermazione secca, con il nome del prodotto o del
produttore dentro.** Tre forme che funzionano:
- il fatto nudo: «Anthropic ha lanciato Claude Duet, un agente personale.»
- la novità detta dal punto di vista di chi la usa: «Claude Duet non aspetta le
  tue domande: ti scrive lui.»
- il contesto: «Dopo OpenAI e Meta, anche Google ha il suo agente per l'ufficio.»

Mai una domanda. Mai un'apertura da quiz («Sai qual è…», «Ti sei mai chiesto…»).
Mai un'emoji. La prima riga diventa l'indirizzo del post su LinkedIn e non si può
più cambiare: mettici il nome del prodotto.

**2. Corpo: da quattro a sei blocchi, ognuno di 2-3 righe.** Ogni blocco porta
avanti un aspetto solo. Ordine che funziona:
- **cos'è**: chi l'ha fatto, quando, che cosa è. Se c'è un contesto che aiuta
  (gli altri produttori hanno appena fatto lo stesso), qui in mezza riga.
- **cosa fa**: due o tre cose concrete, dette con esempi di lavoro e non con gli
  aggettivi del comunicato.
- **il dettaglio che conta**: quello che a una lettura veloce sfugge. Un limite,
  un freno, un prezzo, una scelta di progetto. Spesso è il blocco più letto.
- **chi può usarlo**: piani, paesi, prezzo, da quando. L'Italia si dice sempre:
  c'è, non c'è, non c'è ancora una data.
- facoltativo, **cosa cambia per chi lavora** o cosa puoi fare oggi se in Italia
  non c'è, in una o due righe. Mai il pezzo principale.

Il limite c'è sempre, dentro uno dei blocchi: cosa non fa, cosa non si sa
ancora, cosa costa in limiti o in dati. È quello che separa una notizia da un
comunicato stampa.

In tutto il post fa da 6 a 10 blocchi, contando l'hook e la domanda finale
(nota e hashtag esclusi).

**3. Chiusura: si torna all'hook.** L'ultima riga riprende l'apertura e la
chiude, ora che chi legge sa com'è fatta la cosa. Non una morale nuova.

Dopo la chiusura, una domanda sola, su una riga, senza emoji: chiede
un'esperienza o una scelta concreta di chi legge ("Quale attività della tua
settimana gli lasceresti per prima?"), non un'opinione generica.

**4. Coda.**
- la nota sull'automazione, tra parentesi:
  `(Questo post l'ha scritto il mio agente di ricerca. Fonti nel primo commento.)`
- tre hashtag nell'ultima riga: `#AI`, il produttore o lo strumento del post
  (`#Claude`, `#ChatGPT`, `#Gemini`…) e uno sul tema (`#AgentiAI`…)
- nessun link nel corpo: le fonti vanno nel primo commento, ci pensa `publish.py`

## Il numero

Un dato solo, che fa capire in un colpo quanto pesa la cosa: un prezzo, un
limite, quante app si collegano, da quando, quanto costa rispetto a prima. Si
prende dalla fonte ufficiale e si scrive come lo scrive la fonte.

Mai un numero inventato o arrotondato a effetto, mai un risparmio di tempo dato
come fatto («risparmi il 40%»). Un rapporto preso dalla fonte («costa il 75% in
meno») è un dato; lo stesso rapporto senza fonte è una promessa gonfiata.

Se la notizia non ha un numero vero, il post va bene anche senza.

## Il carosello

Ogni post esce con un carosello: un PDF da 4 a 7 slide 1080x1350 che LinkedIn
mostra da sfogliare. Lo schema viene dai caroselli di notizie di @ai__facile e
@profession.ai: copertina con il titolo grande e una o due parole evidenziate,
poi una slide per aspetto della notizia, con un titoletto e un paragrafo in cui
i passaggi chiave sono colorati, poi la chiusura. Lo stile resta chiaro: fondo
avorio, titoli neri pesanti, testi con le grazie, terracotta come accento,
piccoli cubi isometrici. Niente etichetta sopra il titolo, niente nome di Marco,
niente loghi.

Non lo disegni tu: scrivi nel frontmatter un blocco `carosello:`. L'Action della
PR chiede a ChatGPT (OpenAI, `scripts/illustrazione.py`) l'illustrazione della
copertina, disegna le slide con `scripts/render_carousel.py` e le mostra a Marco
nella PR. Con il Merge `publish.py` carica il PDF su LinkedIn insieme al testo.

**Cosa ci va.** Chi sfoglia senza leggere il post deve capire la notizia. Le
slide seguono gli stessi aspetti del testo, uno per slide: cos'è, cosa fa (anche
su due slide), il dettaglio che conta, chi può usarlo. Ogni slide ha un
titoletto di 3-6 parole che dice il punto ("Lavora su un computer suo") e un
paragrafo di 30-45 parole con 2 o 3 passaggi chiave fra `**`. Niente dati che
nel post non ci sono, e i numeri seguono «Il numero».

Per un trucco le slide sono i passi, con la frase esatta da scrivere in una
slide `frase`. I trucchi visti sui social restano spunti: se si appoggiano su
una funzione o un comando, verificali sulla fonte ufficiale, altrimenti non
entrano.

Le parti:

- **copertina**: `titolo` dice la notizia con il nome del prodotto, non ripete
  l'hook parola per parola; massimo 4 righe, meglio 2-3. Una o due parole chiave
  fra `**` finiscono nel riquadro terracotta: il cuore della notizia ("agente",
  "gratis", "in Italia"), non un aggettivo. `sottotitolo` è facoltativo, una riga:
  chi e quando. `illustrazione` è la scena da disegnare (sotto).
- **slide**: da 2 a 5. Ognuna ha un'`etichetta` di 1-3 parole («Cos'è», «I
  freni», «Chi può usarlo»), un `titolo` (il titoletto, facoltativo ma da usare
  nelle notizie; le parole fra `**` diventano terracotta) e una cosa sola fra:
  - `testo`: il paragrafo, con i passaggi chiave fra `**`;
  - `frase`: la frase esatta da scrivere all'assistente, con un `testo`
    facoltativo sopra;
  - `numero`, con un `testo` che lo spiega e la `fonte` della slide;
  - `voci`: un confronto da 2 a 4 valori della stessa misura e della stessa
    fonte (prezzi, limiti, modelli), con un `testo` facoltativo sopra. Ogni voce
    ha `nome`, `valore` (numero puro, decide quanti cubi), `testo` (come si
    legge) e al massimo una ha `evidenza: true`.
- **chiusura**: riprende l'hook e lo chiude, come l'ultima riga del post. Si può
  andare a capo: la seconda riga, fra `**`, finisce nel riquadro. Sotto, lo
  script aggiunge da solo «Salva il post per quando lo provi.».
- **fonte**: il dominio della fonte ufficiale principale, senza `https://`. Va nel
  piede dell'ultima slide.
- **alt**: cosa dice il carosello, in meno di 120 caratteri. Serve se LinkedIn
  rifiuta il documento e pubblica la sola copertina come immagine.

```yaml
carosello:
  copertina:
    titolo: "Claude Duet, un **agente** che ti scrive per primo"
    sottotitolo: Anthropic l'ha presentato il 21 ottobre. Ecco cosa fa.
    illustrazione: "Una scrivania di sera con un portatile chiuso e un telefono spento; sopra, alcuni cubi si spostano da soli tra una busta, un calendario e un grafico."
  slide:
    - etichetta: Cos'è
      titolo: Un agente, non una **chat**
      testo: "Un'**app a parte** in cui Claude lavora per conto tuo sulle app che gli colleghi: **oltre 6.000**, da Gmail a Slack a HubSpot."
    - etichetta: I freni
      titolo: L'ultimo clic resta **tuo**
      testo: "Prima di **inviare, pagare, firmare o cancellare** ti mostra l'azione esatta e aspetta il tuo sì."
    - etichetta: Chi può usarlo
      titolo: Per ora solo **negli USA**
      testo: "È una **research preview** con lista d'attesa, per chi ha **Pro o Max** e un account negli Stati Uniti."
  chiusura: |
    Duet ti scrive per primo.
    **L'ultima parola resta tua.**
  fonte: claude.com
  alt: "Claude Duet, l'agente di Anthropic: cosa fa, quando chiede il permesso e chi può usarlo"
```

Valori fra virgolette se contengono i due punti o cominciano con `**`.

**L'illustrazione.** Scrivi in `illustrazione` la scena in italiano, in una o
due frasi: oggetti e luogo che raccontano la notizia. Lo stile (piatto, contorni
neri, avorio e terracotta) lo aggiunge lo script. Niente testo, numeri o
schermate da leggere: i modelli sbagliano le scritte, e il titolo c'è già. Niente
persone riconoscibili, loghi, mascotte o prodotti veri. La chiede l'Action della
PR, non tu: nella sessione della routine la copertina esce con una pila di cubi
al posto dell'illustrazione, ed è normale.

Dopo aver salvato il post, controlla il carosello:

```bash
pip install Pillow 2>/dev/null
python scripts/render_carousel.py approved/YYYY-MM-DD.md
```

Se esce con 1, il messaggio dice cosa accorciare o cosa manca: correggi e
rilancia. Poi apri con Read le anteprime in `images/YYYY-MM-DD/`, almeno la
copertina e due slide: si leggono al primo colpo? Dicono la stessa cosa del
post? **Non aggiungere `images/` al commit**: illustrazione e anteprime le fa
l'Action della PR.

I post fino al 2026-10-22 hanno l'infografica singola (blocco `immagine:`,
disegnata da `scripts/render_image.py`): lo script resta per loro, i post nuovi
non la usano più.

## La lingua

- Parole di tutti i giorni. "Usare", non "utilizzare". "Problema", non
  "problematica".
- Niente sostantivi in *-zione* e *-mento* dove c'è un verbo: non "la creazione
  del file", ma "creare il file".
- Voce attiva, sempre. Di' chi fa la cosa: Anthropic, l'agente, tu.
- La stessa parola per la stessa cosa, per tutto il post e il carosello. Se
  Duet è "un agente", resta "un agente": alternare con "assistente" e "bot" fa
  credere che siano tre cose diverse.
- I termini del settore si usano: chi legge li sente ogni giorno. La prima volta
  si chiariscono con quello che fanno, nella stessa frase, mai con una
  definizione. Il nome inglese di una funzione resta in inglese se è quello che
  si legge sullo schermo.

## Il ritmo

- **Alterna le lunghezze, in tutte e due le direzioni.** Se ogni frase diventa un
  blocco a sé il testo ansima (post del 14 agosto: 59% di blocchi da una riga,
  zero reazioni). Se tutti i blocchi sono lunghi uguali suona da notiziario. Nel
  formato corto stanno da soli l'hook, l'ultima riga e la domanda; gli altri
  blocchi raggruppano 2-3 righe che portano avanti lo stesso aspetto.
- **Prima la notizia, poi il resto.** Nei primi due blocchi chi legge deve già
  sapere cos'è uscito e cos'è. Il "cosa puoi fare tu" viene dopo, se c'è.

## Cosa non si fa mai

**La glossa didascalica.** «un classificatore, cioè un sistema che...». Vietati:
«cioè», «ovvero», «vale a dire», «in altre parole», «per intenderci». Il termine
si chiarisce con quello che fa: «un agente: lavora sulle tue app anche quando
chiudi la chat».

**La promessa gonfiata.** «Rivoluziona il lavoro», «fortissimo», «10 volte più
veloce», «nessuno te lo dice». Anche se lo fanno i profili da cui prendiamo lo
schema: chi legge ha già visto cento post così. Si dice cosa fa, e basta.

**Il tono da guru.** Niente «stai usando Claude nel modo sbagliato», niente «la
maggior parte delle persone sbaglia», niente lettore trattato da ingenuo.

**Il comunicato stampa.** Gli aggettivi del produttore («potente»,
«rivoluzionario», «il più avanzato») non si riportano. Al loro posto, cosa fa.

**L'attenuazione continua.** Massimo due attenuatori in tutto il post («un po'»,
«forse», «magari»).

**Le emoji come punteggiatura.** Zero o una in tutto il post, mai nell'hook. Mai 👇.

**La CTA da bacheca.** «Che ne pensi?», «Sei d'accordo?», «Fammi sapere nei
commenti». LinkedIn le classifica come esca e ne riduce la portata.

**Le frasi da bigliettino.** «Fidarsi va bene, capire è meglio.» Se una frase
suona bene ma non aggiunge un fatto, si taglia.

**Gli stilemi da modello linguistico.** Trattino lungo, freccia `→`, «non è solo
X ma Y», «in un mondo in cui», «la vera domanda è», «rappresenta una svolta».
L'elenco completo, con gli esempi, è nella skill humanizer (sotto).

## L'ultima passata: humanizer

Ogni post, prima di `readability.py`, passa dalla skill humanizer in
`.claude/skills/humanizer/SKILL.md`. È un adattamento italiano della skill
humanizer di Siqi Chen (MIT) e toglie i segni della scrittura AI senza cambiare
quello che il post dice.

Se la skill è fra quelle caricate nella sessione, usala; altrimenti apri il file
con Read e seguilo. Valgono le regole della sua sezione «Nei post LinkedIn di
questo repo»: riscrivi direttamente il file, la struttura di questo STYLE.md
resta, nota e hashtag non si toccano, e si ripassano anche i testi del blocco
`carosello:`.

`readability.py` blocca i segnali più sicuri (contrasto «non si tratta di X, si
tratta di Y», «è importante notare», «in conclusione», «vediamo insieme», residui
da chatbot, importanza gonfiata) e avvisa sugli altri (parole da AI in gruppo,
gerundi appesi, «non è X, è Y» fuori dall'hook).

## Esempi

- `examples/novita-duet.md`: **il modello di riferimento** per testo e
  carosello. Una NOVITÀ: cos'è, cosa fa, il dettaglio che conta (i freni), chi
  può usarlo e il limite, la chiusura sull'hook; nel carosello cinque slide con
  titoletto e passaggi chiave.
- `examples/carosello-excel.md`: il modello per i giorni senza novità, un
  trucco con la slide `frase`. Testo e carosello sono ancora nella voce di prima,
  pensata per chi partiva da zero: prendine la struttura, non il tono.
- `examples/funzione-progetti.md`, `examples/riscrittura-2026-08-10.md` e
  `examples/riscrittura-2026-08-13.md`: della linea precedente. Utili solo per
  l'hook.
