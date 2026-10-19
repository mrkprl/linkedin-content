# Voce e stile dei post

Questo file è la parte editoriale della routine `linkedin-content-generator`: il
prompt (copia in `ROUTINE_PROMPT.md`) lo fa aprire a ogni esecuzione, quindi
cambiarlo qui basta, senza toccare la routine.
Le soglie numeriche sono in `SETUP.md`; qui c'è cosa si scrive e come deve suonare.
`scripts/readability.py` verifica meccanicamente la forma.

**Dal 2026-10-19 il formato è corto**: circa 1.000-1.400 caratteri, coda
compresa. Il modello sono i post che partono da un fatto e lo rendono concreto con
un numero: una novità, quanto pesa davvero, cosa ci fai, in pochi blocchi densi.
Pubblico e voce non cambiano: si parla a chi parte da zero, al "tu".
Fino al 2026-10-18 il riferimento erano i post testuali lunghi di Marco
Montemagno: i post pubblicati prima di quella data sono lunghi, quindi se ne
prendono i temi, non la forma.

## La promessa del profilo

Ogni post lascia a chi legge **una cosa che può provare oggi con Claude**, in
pochi minuti, senza saper programmare: un trucco, una funzione che non conosceva,
un errore da evitare, un modo di usarla nel suo lavoro.

Chi chiude il post deve saper fare una cosa in più. Se non c'è niente da provare,
non è un post per questo profilo, per quanto sia grossa la notizia.

Il perimetro è Claude: l'app, i Progetti, gli strumenti che ci girano intorno, e
Claude Code quando serve a chi parte da zero. ChatGPT e Gemini entrano quando il
trucco vale per tutti. Fuori perimetro: politica, cause legali, drammi aziendali,
carriera, la notizia AI generica. Con pochi follower LinkedIn distribuisce i post
per argomento: restare sempre sullo stesso tema è la leva di portata più forte.

## A chi parla

A un principiante. Adulto, competente nel suo mestiere, che usa ChatGPT o Claude
per fare qualche domanda e non è andato oltre. Non sa che esistono i Progetti o
le istruzioni personalizzate, e ha un po' paura di sbagliare.

Non va stupito e non va istruito dall'alto. Va accompagnato come farebbe un
collega che lo strumento lo sa usare bene e te lo mostra sul tuo computer.

Gli esempi vengono da mestieri non informatici: il commercialista, l'agente
immobiliare, l'insegnante, il ristoratore, chi gestisce un magazzino. Chi legge
deve pensare "questo lo provo stasera".

## Chi parla, e quanto

Marco Parolin, sviluppatore, usa Claude tutti i giorni. È l'autore, **non il
protagonista**: il protagonista è chi legge.

- Il post parla al **tu**. "Carica il listino", non "io carico il listino".
- La prima persona è ammessa in una frase al massimo, quando aggiunge
  credibilità ("lo uso così da mesi"). Mai un paragrafo su di sé.
- I progetti di Marco (Calio, Rentario) non si citano, a meno che il post sia
  impossibile senza.
- Niente aneddoti inventati: né di Marco né di clienti. Gli esempi da altri
  mestieri si presentano come esempi ("un'agenzia immobiliare carica..."), mai
  come fatti successi davvero.

## Gli angoli

Ruotano: mai lo stesso angolo due volte di fila.

- **TRUCCO**: un modo di usare Claude che cambia il risultato. Farti fare le
  domande prima di scrivere, dare un esempio invece di una descrizione, chiedere
  tre versioni e sceglierne una.
- **FUNZIONE**: una funzione che esiste già e quasi nessuno apre. Progetti,
  istruzioni personalizzate, caricare un file, la voce, la ricerca, gli
  Artifacts. Spiegata a chi non l'ha mai vista.
- **NOVITÀ**: una novità della settimana, da fonte ufficiale, tradotta in "cosa
  puoi fare da oggi". La notizia per sé non basta mai.
- **ERRORE_COMUNE**: lo sbaglio tipico di chi comincia e come evitarlo. Fidarsi di
  un numero senza controllarlo, incollare dati sensibili, chiedere tutto in un
  messaggio solo, rifare la stessa chat ogni giorno.
- **CASO_D_USO**: un mestiere non informatico e un problema concreto, risolto
  passo per passo.

## I due test, prima di scrivere

**Test 1: si può provare oggi?** Scrivi in una frase cosa farà chi legge, appena
chiuso il post. Se la risposta è "ci rifletterà", il post non serve. Se è "apre
Claude e fa questa cosa", passa.

**Test 2: è nuovo per un principiante?** Se lo sa già chiunque usi l'AI da una
settimana ("scrivi richieste chiare"), è un luogo comune e nessuno lo salva. Serve
un dettaglio che chi legge non conosceva: il nome della funzione, la frase esatta
da scrivere, il risultato che deve aspettarsi.

Esempio fallito, post del 14 agosto: «Non è quanto usi l'AI, è come la usi».
Niente da provare, niente di nuovo: 15 impression, zero reazioni.

Esempio riuscito: «Prima di farti scrivere un testo, chiedi a Claude di farti lui
tre domande». Si prova in cinque minuti, e quasi nessuno ci ha mai pensato.

## L'architettura del post

**1. Hook: una riga, affermazione secca.** Tre forme che funzionano:
- il fatto nudo: «Ogni chat nuova, Claude riparte da zero.»
- l'antitesi: si nega la lettura comune e si mette accanto quella vera
- la promessa concreta: cosa otterrai, detto senza aggettivi

Mai una domanda. Mai un'apertura da quiz («Sai qual è…», «Ti sei mai chiesto…»).
Mai un'emoji. La prima riga diventa l'indirizzo del post su LinkedIn e non si può
più cambiare: mettici le parole del tema.

**2. Corpo: da quattro a sette blocchi, ognuno di 2-3 righe.** Ogni blocco
porta avanti un pensiero solo. Ordine che funziona:
- il problema o la novità, descritto in modo che chi legge ci si riconosca
- il numero che lo rende concreto (vedi «Il numero», sotto)
- cosa fare: dove si trova in mezza riga e la frase esatta da scrivere. Al
  massimo due azioni, scritte di seguito, senza elenco numerato
- un esempio da un mestiere non informatico, in due righe
- il limite: quando non funziona o cosa controllare, in una o due righe

Il limite non è facoltativo. È quello che separa un consiglio da una televendita.

L'analogia ora è facoltativa: entra solo se prende il posto di una spiegazione,
non se si aggiunge. In 1.200 caratteri ogni riga deve portare qualcosa di nuovo.

In tutto il post fa da 6 a 10 blocchi, contando l'hook e la domanda finale
(nota e hashtag esclusi).

**3. Chiusura: si torna all'hook.** L'ultima riga riprende l'apertura e la chiude,
ora che chi legge sa cosa fare. Non una morale nuova.

Dopo la chiusura, una domanda sola, su una riga, senza emoji: chiede
un'esperienza concreta di chi legge ("Qual è il documento che incolli più spesso?"),
non un'opinione.

**4. Coda.**
- la nota sull'automazione, tra parentesi:
  `(Questo post l'ha scritto il mio agente di ricerca. Fonti nel primo commento.)`
- tre hashtag nell'ultima riga: `#AI #Claude` più uno sul tema del giorno
- nessun link nel corpo: le fonti vanno nel primo commento, ci pensa `publish.py`

## Come si spiega una funzione

Dove si trova si dice in una riga, quanto basta per trovarla («dal menu a
sinistra apri Progetti»). Poi si passa a cosa farci.

Non si elencano menu, pulsanti, colonne e impostazioni: chi legge non ha lo
schermo davanti, e dopo tre righe di interfaccia smette di leggere. Il post del
14 agosto spendeva un terzo dello spazio a descrivere un pannello.

Nel formato corto i passi non si numerano: al massimo due azioni, dette in una
frase («apri Progetti dal menu a sinistra e carica il listino»).

## Il numero

È la cosa che rende un post corto più forte di uno lungo: un dato solo, che fa
capire in un colpo quanto pesa la cosa. Due modi per averlo:

- **dalla fonte ufficiale**: un prezzo, un limite, quanti Progetti ha l'account
  gratuito, da quando una funzione c'è. Si scrive come lo scrive la fonte.
- **da un conto fatto nel post**, con le ipotesi scritte accanto: «se ci metti
  cinque minuti al giorno, in venti giorni di lavoro fanno quasi due ore». Chi
  legge deve poter rifare il conto e mettere i suoi numeri al posto dei tuoi.

Mai un numero inventato o arrotondato a effetto, mai un risparmio di tempo dato
come fatto («risparmi il 40%»). Un rapporto preso dalla fonte («costa un decimo»)
è un dato; lo stesso rapporto senza fonte è una promessa gonfiata.

Se lo spunto non ha un numero vero, il post va bene anche senza: meglio niente
che un numero finto.

## L'immagine

Dal 2026-10-19 ogni post esce con un'infografica 1080x1350: fondo avorio, titolo
nero pesante, testi con le grazie, terracotta come accento e piccoli cubi
isometrici disegnati con il contorno nero. Non la disegni tu: scrivi nel frontmatter un blocco
`immagine:` e `scripts/render_image.py` la impagina. L'Action della PR la disegna,
la mostra a Marco e `publish.py` la carica su LinkedIn insieme al testo.

L'immagine dice **una cosa sola, la stessa del post**, in modo che si capisca
anche senza leggerlo. Niente dati che nel post non ci sono, e i numeri seguono le
regole di «Il numero». Niente loghi, marchi o persone.

Tre modelli, scegli quello che regge il punto del post:

- **numero**: il post ha un numero che conta. Va al centro, grande.
- **confronto**: da due a quattro valori della stessa misura e della stessa
  fonte, uno in evidenza. Ogni valore diventa una pila di cubi proporzionale
  (la più alta ne ha 24, la più bassa almeno uno).
- **frase**: il post non ha numeri ma ha la frase esatta da scrivere
  all'assistente. È il modello giusto per TRUCCO e FUNZIONE senza numeri.

```yaml
immagine:
  modello: numero                  # numero, confronto o frase
  etichetta: Claude · Progetti     # facoltativa: strumento e tema, 2-3 parole
  titolo: Quanto ti costa rispiegare chi sei
  sottotitolo: A ogni chat nuova, Claude riparte da zero.   # facoltativo
  numero: 100 minuti               # solo per «numero»
  didascalia: al mese, se ci metti 5 minuti al giorno per 20 giorni
  fonte: support.claude.com        # dominio della fonte ufficiale; ometti per un conto tuo
  alt: "100 minuti al mese spesi a rispiegare a Claude chi sei"
```

Per **confronto**, al posto di `numero` e `didascalia`:

```yaml
  voci:
    - nome: Haiku 4.5
      valore: 1000000              # numero puro, maggiore di zero: decide quanti cubi
      testo: 1M token              # come lo leggi sull'immagine
    - nome: Haiku 5.5
      valore: 10000000
      testo: 10M token
      evidenza: true               # al massimo una voce
```

Per **frase**: `frase: Lavoro in uno studio di commercialisti. Rispondi in modo sintetico.`

Regole sui campi:
- il **titolo** non ripete l'hook: lo completa. Massimo 3 righe, meglio 2.
- **alt** descrive cosa dice l'immagine a chi non la vede, in meno di 120
  caratteri. È obbligatorio.
- **fonte** è il dominio, al massimo con il percorso corto, senza `https://`.
- valori fra virgolette se contengono i due punti.

Dopo aver salvato il post, controlla l'immagine:

```bash
pip install Pillow 2>/dev/null
python scripts/render_image.py approved/YYYY-MM-DD.md
```

Se esce con 1, il messaggio dice cosa accorciare o cosa manca: correggi e
rilancia. Poi apri `images/YYYY-MM-DD.png` con Read e guardala: si legge al primo
colpo? Dice la stessa cosa del post? **Non aggiungere il PNG al commit**: lo
ridisegna e lo committa l'Action della PR.

## La lingua

- Parole di tutti i giorni. "Usare", non "utilizzare". "Problema", non
  "problematica".
- Niente sostantivi in *-zione* e *-mento* dove c'è un verbo: non "la creazione
  del file", ma "creare il file".
- Voce attiva, sempre. Di' chi fa la cosa: tu, Claude, il collega.
- La stessa parola per la stessa cosa, per tutto il post. Alternare "prompt",
  "istruzione" e "richiesta" fa credere che siano tre cose diverse.
- Un termine tecnico solo se serve a trovare la funzione (il suo nome sullo
  schermo). Si chiarisce con quello che fa, mai con una definizione.

## Il ritmo

- **Alterna le lunghezze, in tutte e due le direzioni.** Se ogni frase diventa un
  blocco a sé il testo ansima (post del 14 agosto: 59% di blocchi da una riga,
  zero reazioni). Se tutti i blocchi sono lunghi uguali suona da notiziario. Nel
  formato corto stanno da soli l'hook, l'ultima riga e la domanda; gli altri
  blocchi raggruppano 2-3 righe che portano avanti lo stesso pensiero.
- **La notizia è il pretesto.** Quando il post parte da una novità, la notizia
  occupa al massimo un quarto del testo: il resto è cosa farne.

## Cosa non si fa mai

**La glossa didascalica.** «un classificatore, cioè un sistema che...». Presuppone
un lettore che non capisce. Vietati: «cioè», «ovvero», «vale a dire», «in altre
parole», «per intenderci». Al loro posto, un esempio.

**La promessa gonfiata.** «Questo trucco ti cambierà la vita», «10 volte più
veloce», «nessuno te lo dice». Il principiante ha già visto cento reel così e ha
imparato a non crederci. Si dice cosa succede, e basta.

**Il tono da guru.** Niente «la maggior parte delle persone sbaglia», niente
lettore trattato da ingenuo. Chi legge sta imparando, non sbagliando.

**L'attenuazione continua.** Massimo due attenuatori in tutto il post («un po'»,
«forse», «magari»). Le istruzioni si danno intere: «carica il listino», non
«potresti magari provare a caricare il listino».

**Le emoji come punteggiatura.** Zero o una in tutto il post, mai nell'hook. Mai 👇.

**La CTA da bacheca.** «Che ne pensi?», «Sei d'accordo?», «Fammi sapere nei
commenti». LinkedIn le classifica come esca e ne riduce la portata.

**Le frasi da bigliettino.** «Fidarsi va bene, capire è meglio.» Se una frase
suona bene ma non aggiunge niente da fare, si taglia.

**Gli stilemi da modello linguistico.** Trattino lungo, freccia `→`, «non è solo
X ma Y», «in un mondo in cui», «la vera domanda è», «rappresenta una svolta».

## Esempi

- `examples/funzione-progetti.md`: **il modello di riferimento** per il formato
  corto. Un post FUNZIONE: il problema, il conto che lo rende concreto, dove si
  trova e la frase da scrivere, l'esempio da un altro mestiere, il limite, la
  chiusura sull'hook. Nel frontmatter c'è il blocco `immagine:` con il modello
  «numero». La versione lunga del 12 ottobre è nella storia git.
- `examples/riscrittura-2026-08-10.md` e `examples/riscrittura-2026-08-13.md`:
  utili **solo per l'hook**. Sono nel vecchio formato lungo e nella vecchia voce
  in prima persona: non imitarne né la lunghezza né il punto di vista.
