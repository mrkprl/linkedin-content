# Voce e stile dei post

Questo file è la parte editoriale della routine `linkedin-content-generator`: il
prompt (copia in `ROUTINE_PROMPT.md`) lo fa aprire a ogni esecuzione, quindi
cambiarlo qui basta, senza toccare la routine.
Le soglie numeriche sono in `SETUP.md`; qui c'è cosa si scrive e come deve suonare.
`scripts/readability.py` verifica meccanicamente la forma.

Riferimento per l'architettura del testo: i post testuali lunghi di Marco
Montemagno (analizzati il 2026-08-13). Non si copiano i contenuti, si copia il
ritmo.

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

**2. Corpo: blocchi da una a tre righe.** Ordine che funziona:
- il problema, descritto in modo che chi legge ci si riconosca
- cosa fare: i passi concreti, con la frase esatta da scrivere quando c'è
- perché funziona, con un'analogia presa dalla vita di tutti i giorni
- un esempio da un mestiere non informatico
- il limite: quando non funziona o cosa controllare, in due righe

Il limite non è facoltativo. È quello che separa un consiglio da una televendita.

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

I passi numerati vanno bene se sono al massimo tre, e ognuno sta su una riga.

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
  zero reazioni). Se tutti i blocchi sono lunghi uguali suona da notiziario. Nei
  post riusciti due blocchi su tre raggruppano 2-3 righe che portano avanti lo
  stesso pensiero, e la riga isolata arriva ogni tanto.
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

**Le righe che annunciano.** «Un esempio.», «Come si fa, in tre passi.», «C'è una
strada più corta.», «Due cose da controllare.» Sono l'impalcatura del post rimasta
in vista: chi legge capisce che è un esempio quando lo legge. Si entra subito nel
contenuto («Un'agenzia immobiliare, per esempio, carica...»).

**Gli stilemi da modello linguistico.** Trattino lungo, freccia `→`, «non è solo
X ma Y», «in un mondo in cui», «la vera domanda è», «rappresenta una svolta».

## Esempi

- `examples/funzione-progetti.md`: **il modello di riferimento** per la linea
  attuale. Un post FUNZIONE: problema, tre passi, la frase da scrivere,
  l'analogia, l'esempio da un altro mestiere, il limite, la chiusura sull'hook.
  Se ne copia il ritmo e l'ordine delle parti, non le frasi: un post che
  riprende le sue formule riga per riga suona compilato.
- `examples/riscrittura-2026-08-10.md` e `examples/riscrittura-2026-08-13.md`:
  utili **solo per la forma** (hook, blocchi, ritmo). Sono scritti nella vecchia
  voce in prima persona: non imitarne il punto di vista.
