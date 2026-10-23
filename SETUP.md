# Setup e configurazione — linkedin-content

Stato verificato il 2026-08-07.

## Architettura

```
Routine cloud Claude (ogni giorno, 7:55 IT) → genera il post in approved/ sul branch post/YYYY-MM-DD
GitHub Action "Open Post PR" → illustrazione OpenAI + anteprime del carosello → PR di approvazione (reviewer: mrkprl)
Tu, da GitHub Mobile → Merge = pubblica · Close = scarta
GitHub Actions "Publish to LinkedIn" (solo main) → pubblica → sposta in published/
```

L'approvazione avviene dal telefono con l'app **GitHub Mobile**: la review request
sulla PR genera una notifica push, il testo completo del post è nel body della PR.
I post scartati o rimasti orfani finiscono in `archive/`. La cartella `pending/`
non è più usata dal flusso (rimane solo per compatibilità storica).

## Componenti

### 1. Generazione contenuti — routine cloud Claude
- **Routine**: `linkedin-content-generator` (`trig_01E1UaHdMXwNi3Z3QydKjoHg`)
- **Schedule**: `CRON_TZ=Europe/Rome 55 7 * * *` = 7:55 italiane tutto l'anno, ogni giorno
  (dal 2026-10-23; prima era `0 6 * * *` in UTC e con l'ora solare sarebbe slittato alle 7:00.
  Le 7:55 invece delle 8:00 perché le routine fissate allo scoccare dell'ora partono in ritardo)
  (era lun-ven fino al 2026-08-14: cinque post a settimana obbligavano a commentare
  anche i giorni senza una notizia degna, e il generatore riempiva descrivendo prodotti)
- **Modello**: `claude-opus-5-5` (dal 2026-10-12; si imposta nella routine, non nel repo)
- **Environment**: `LinkedInSearch`, con la rete Custom descritta in "Rete e fonti"
- **Gestione**: https://claude.ai/code/routines
- **Il prompt è copiato in `ROUTINE_PROMPT.md`**: se cambia lì, va reincollato
  nella routine (claude.ai/code → Routine → linkedin-content-generator → freccia
  accanto al nome → Modifica). La routine è stata creata via API: un agente non la
  può modificare con i suoi strumenti, solo da quella pagina. Dopo averlo
  incollato, controlla che gli a capo ci siano: il 2026-10-19 si erano persi e i
  comandi erano finiti tutti su una riga. La parte editoriale invece sta in `STYLE.md`, che il prompt fa
  aprire a ogni esecuzione: cambiarla non richiede di toccare la routine.
- Le regole di forma sono verificabili e la routine le auto-controlla con
  `scripts/readability.py` prima di pushare (esce con 1 se qualcosa non passa).
  Esempio di riferimento in `examples/novita-duet.md` (dal 2026-10-23).

### Linea editoriale (dal 2026-10-12)

Dal 2026-10-23 il profilo racconta le **novità serie dell'AI** a chi lavora e
l'AI la usa già (professionisti, piccole imprese), su tutti gli strumenti alla
pari: Claude, ChatGPT, Gemini, Copilot. Il riferimento per testi e impaginazione
sono i caroselli di notizie di @ai__facile e @profession.ai. Ogni giorno una
novità seria; un trucco solo nei giorni senza novità e solo se è forte; se non
c'è nessuno dei due, niente post. Niente riepilogo settimanale (scelta di Marco
del 2026-10-23).
Angoli: `NOVITÀ` (quasi sempre), `FUNZIONE`, `STRUMENTO`, e nei giorni senza
novità `TRUCCO`, `ERRORE_COMUNE`, `CASO_D_USO` (dettagli in `STYLE.md`). I test
prima di scrivere sono "è una novità seria?" e "chi legge lo capisce fino in
fondo?".

Dal 2026-10-12 al 2026-10-22 il profilo insegnava "una cosa da provare oggi" a
chi partiva da zero, con Claude al centro. Marco l'ha trovato troppo da
principianti, e sulle notizie grosse la regola le nascondeva (post su Claude
Duet del 22 ottobre: non diceva che era un agente).

Dal 2026-10-19 il formato è corto: 900-1.300 caratteri dal 2026-10-23 (prima 1.000-1.400), 6-10 blocchi, un numero
concreto (dalla fonte o da un conto con le ipotesi scritte). Pubblico e voce non
cambiano. Dettagli in `STYLE.md`, soglie qui sotto in "Policy di forma dei post".

Dal 2026-10-23 il post esce con un carosello PDF di al massimo 4 pagine al posto
dell'infografica singola, sul modello di @ai__facile e @profession.ai su
Instagram: copertina e slide con le illustrazioni di ChatGPT, titoletti e
passaggi chiave evidenziati. Il testo segue lo schema dei post di Datapizza su
LinkedIn, in tono colloquiale: fatto nudo, per chi è, dov'è la novità, i paletti
in un elenco breve, chi può usarlo, il contesto in chiusura. Dettagli in
"5. Carosello" e in `STYLE.md`.

Fino al 2026-10-09 la linea era un'altra: una tesi da difendere ("cercare contro
costruire") raccontata in prima persona a partire dai progetti di Marco. È stata
abbandonata perché troppo centrata su di lui; i 25 post scritti in quella voce
(PR #1 e #7-#30) sono stati chiusi senza pubblicarli.

### Rete e fonti

La routine trova gli spunti con `scripts/scout.py`, che legge `IDEE.md` (le idee
che Marco incolla dal telefono, con la precedenza) e poi le fonti in `fonti.yaml`
(feed RSS/Atom, Hacker News, pagine ufficiali). Per aggiungere una fonte basta una
voce in `fonti.yaml` **e** il suo dominio nella lista dell'environment.

L'environment cloud della routine deve avere **Network access: Custom**, con
"Also include default list of common package managers" spuntato e questi domini
in **Allowed domains** (impostato il 2026-10-12):

```
*.anthropic.com
*.claude.com
openai.com
*.openai.com
blog.google
deepmind.google
github.blog
simonwillison.net
www.theverge.com
arstechnica.com
techcrunch.com
venturebeat.com
www.reddit.com
old.reddit.com
hn.algolia.com
news.ycombinator.com
www.youtube.com
*.substack.com
rss.beehiiv.com
www.therundown.ai
www.theneurondaily.com
bensbites.com
www.bensbites.com
tldr.tech
```

Si cambia da claude.ai/code: icona a forma di nuvola sopra la casella dei
messaggi, ingranaggio sull'environment, campo **Network access**. Con il livello
**Trusted** di default le fonti non rispondono, e anche WebFetch passa da lì.
Meglio Custom che Full: la routine legge testo scritto da sconosciuti senza
nessuno che guardi, e una lista chiusa limita cosa può raggiungere.

`openai.com` (senza asterisco) è in lista dal 2026-10-23 per il feed di OpenAI News:
non è detto che `*.openai.com` copra anche il dominio nudo. Se `scout.py` lo
segnala come non raggiungibile, controlla che sia anche nell'environment.

Verificato il 2026-10-12:
- **Instagram non si legge**, nemmeno con Full: senza login non mostra i post, e
  lo scraping viola i termini d'uso. Gli spunti da lì passano da `IDEE.md`.
- **Reddit risponde vuoto agli user agent generici**: `scout.py` usa un nome
  descrittivo (`linux:linkedin-content-scout:v1.0 (by /u/mrkprl)`).
- **Bloccano i bot** l'help center di OpenAI (403), VentureBeat (429) e i feed di
  The Neuron (403): per ora non sono in `fonti.yaml`.

Per rileggere o modificare il prompt: https://claude.ai/code/routines/trig_01E1UaHdMXwNi3Z3QydKjoHg

## Policy di forma dei post (aggiornata il 2026-10-19)

Ogni numero qui sotto viene da una misura, non da un'opinione. Le fonti sono in
fondo alla sezione. `scripts/readability.py` implementa i controlli; le regole di
voce che i numeri non catturano stanno in `STYLE.md`.

| Regola | Valore | Perché |
|---|---|---|
| Lunghezza | 900-1.300 caratteri, coda compresa (lo script tollera 800-1.500) | **Scelta di Marco del 2026-10-19**, ritoccata il 2026-10-23 sul modello dei post di Datapizza (circa 850 caratteri), contro i dati: post corti e densi, sul modello di quelli che legge e vuole scrivere. Le impression mediane crescono con la lunghezza (575 sotto i 400 caratteri, 1.106 tra 1.301 e 2.000, 1.400 tra 2.501 e 3.000), quindi la scelta va verificata sulle impression dei prossimi post. Fino al 2026-10-18 la fascia era 1.800-2.400. |
| Hook (prima riga) | max 60 caratteri, meglio sotto 40 | Hook sotto i 40 caratteri battono quelli oltre i 200 di circa il 25% di engagement rate. |
| Tipo di hook | affermazione, fatto o confessione, **mai domanda** | Su 309.614 post l'hook a domanda è ultimo dei cinque tipi (2,16% contro 2,60% dell'hook narrativo). Bloccate anche le aperture da quiz ("Sai qual è…", "Ti sei mai chiesto…"). |
| Blocchi | 6-10, contando hook e domanda finale (nota e hashtag esclusi); righe max 260 caratteri | Post con 20+ paragrafi: 1,13x reach. Con 0-5 paragrafi: 0,70x. In 1.200 caratteri 20 paragrafi vorrebbero dire una frase per blocco, il difetto del post del 14-08: si sta sopra la fascia peggiore e si raggruppano 2-3 righe per blocco. Il limite per riga evita il muro di testo sul telefono. Fino al 2026-10-18 la soglia era almeno 20 paragrafi. |
| Frasi | mai oltre 25 parole, media 12-18 | Direttiva sulla semplificazione del linguaggio dei testi amministrativi (8/5/2002), regola 1; Cortelazzo-Pellegrino regola 12. |
| Gulpease | ≥ 60, target 70 | Sotto 60 il testo non è leggibile in autonomia da chi ha la licenza media. È l'indice tarato sull'italiano (Lucisano-Piemontese 1988), non Flesch. |
| Glosse didascaliche | **zero** | "cioè", "ovvero", "in altre parole": presuppongono un lettore che non capisce e fanno suonare il testo come un tema di scuola. Al loro posto va un esempio concreto. |
| Attenuatori | max 2 | "un po'", "forse", "onestamente": oltre due, il post non afferma più niente e la voce si sfalda. |
| Link nel corpo | **nessuno** | Sui profili personali un link costa −27% impression e −20% interazioni. Sulle pagine aziendali l'effetto è opposto (+51%): da qui gran parte della confusione in circolazione. |
| Fonti | nel primo commento, in automatico | Vedi `source_comment()` e `publish_comment()` in `publish.py`. |
| Hashtag | 3, ultima riga, mai in apertura | L'effetto sulla portata è vicino a zero, ma un hashtag in prima riga rovina lo slug dell'URL. |
| CTA | domanda che richiede esperienza personale | Le domande generiche ("Sei d'accordo?") sono engagement bait dichiarato e vengono ridotte. Una domanda specifica sposta l'engagement dai like ai commenti (+77% commenti), che pesano di più. |
| Blocchi da una riga sola | max 50%, meglio ~33% | Nei post riusciti due blocchi su tre raggruppano 2-3 righe. Sopra il 50% il testo ansima e si legge come un elenco puntato senza punti (post del 14-08: 59%, zero reazioni). |
| Ordine | prima la notizia: nei primi due blocchi cos'è, chi, quando | Dal 2026-10-23. Fino al 2026-10-22 la regola era l'opposta (la notizia al massimo un quarto del testo, il resto "cosa farne"), e sul post di Claude Duet ha nascosto la notizia. Dove si trova una funzione si dice comunque in una riga: elencare menu e pulsanti è manuale utente. |
| Utilità | una novità seria, che chi legge capisce fino in fondo (cos'è, cosa fa, se la può usare) | Un luogo comune o una notizia di contorno non lasciano niente: 15 impression, zero reazioni (post del 14-08). Se non c'è una novità seria né un trucco forte, quel giorno non si pubblica. |
| Emoji | 0-1, mai nell'hook | Da 0 a 1 emoji: +22% reach. Oltre, l'effetto è piatto, e in serie fanno registro adolescenziale. |
| Nota sull'automazione | tra parentesi, in coda, senza faccine | Sostituisce il vecchio "P.S. … il mio amico Claudio Code 🙂". |

**La prima riga diventa l'URL del post.** LinkedIn ricava lo slug di
`linkedin.com/posts/<slug>-activity-<id>` dalla prima riga, ed è immutabile dopo la
pubblicazione. È l'unica leva SEO deterministica disponibile: mettici le parole
chiave del tema, mai un hashtag.

**Cosa NON è SEO su LinkedIn.** La distribuzione non funziona per keyword matching:
il feed usa dual encoder LLM che confrontano per similarità coseno l'embedding del
post con quello del profilo di chi legge. Riempire il testo di parole chiave non
serve. Serve la **coerenza tematica**: con pochi follower il post viene distribuito
per argomento, non per rete sociale, quindi restare sempre sullo stesso perimetro
(gli assistenti AI e come usarli nel lavoro) è la leva di portata numero uno.

**Da fare a mano, fuori dal sistema** (non automatizzabile, alto ritorno):
1. Allineare headline, About e Skills del profilo al vocabolario dei post: il
   profilo entra nell'embedding che decide a chi mostrare il post.
2. Verificare che "Articoli e attività" sia su "Mostra" nelle impostazioni di
   visibilità del profilo pubblico: è la condizione per l'indicizzazione dei post.
3. Rispondere a ogni commento: +30% engagement misurato con regressione a effetti
   fissi su 72.000 post. Le risposte dell'autore contano anche verso la soglia dei
   10 commenti che LinkedIn indica come utile.

Fonti dei numeri: [AuthoredUp](https://authoredup.com/blog/linkedin-character-limit)
(372.126 post da profili personali, set 2025-feb 2026; hook su 309.614 post),
[Metricool](https://metricool.com/linkedin-trends/) (673.658 post, link e hashtag),
[Buffer](https://buffer.com/resources/linkedin-engagement-data/) (72.000 post,
effetti fissi), [LinkedIn Engineering sul nuovo feed](https://www.linkedin.com/blog/engineering/feed/engineering-the-next-generation-of-linkedins-feed)
e [LinkedIn Business Blog, 12/03/2026](https://www.linkedin.com/business/marketing/blog/content-marketing/how-to-leverage-linkedin-for-ai-visibility-in-2026)
(slug URL, soglia dei 10 commenti), [Direttiva 8/5/2002](https://www.funzionepubblica.gov.it)
e [Cortelazzo-Pellegrino, 30 regole](https://www.unifg.it/sites/default/files/2021-06/30_reg_txt_amm_chr_0.pdf)
(frasi e leggibilità), [Vena 2022, Italiano LinguaDue](https://riviste.unimi.it/index.php/promoitals/article/download/18298/16262/54964)
(formula e soglie Gulpease).

Attenzione: molte cifre che circolano sull'algoritmo LinkedIn 2026 (penalità
percentuali per contenuti AI, soglie di dwell time in secondi, "−60% per i link")
non sono tracciabili a nessuna fonte primaria, incluso un articolo di Forbes le cui
uniche fonti sono due blog SEO. Non inseguirle.

### 2. PR di approvazione — GitHub Actions
- Workflow: `.github/workflows/open-post-pr.yml` — trigger su push dei branch `post/**`
- Apre la PR verso main con il testo del post nel body, assegna e richiede la
  review a `mrkprl` (è la review request che fa scattare la notifica push su mobile)
- Richiede l'impostazione repo "Allow GitHub Actions to create and approve pull
  requests" (abilitata il 2026-08-07 via API); attivo anche il delete-branch-on-merge

### 3. Pubblicazione — GitHub Actions
- Workflow: `.github/workflows/publish-to-linkedin.yml` — trigger su push di `approved/**.md` **solo su main**
- Script: `scripts/publish.py` — LinkedIn REST API `/rest/posts`
- Secrets (repo → Settings → Secrets → Actions):
  - `LINKEDIN_ACCESS_TOKEN` — impostato 2026-10-12, **scade ~2026-12-11**
  - `LINKEDIN_PERSON_ID` — `IJ0yQ3PjVm` (il claim `sub` di `/v2/userinfo`, stabile)

### 4. Infografica (dal 2026-10-19 al 2026-10-22, solo per i post di quei giorni)
- Il generatore scrive nel frontmatter un blocco `immagine:` (campi e modelli in
  `STYLE.md`, sezione "L'immagine"). Non committa il PNG.
- `scripts/render_image.py` disegna `images/DATA.png`, 1080x1350, con Pillow e i
  font Inter e Source Serif 4 in `assets/fonts/` (entrambi SIL OFL, licenze
  accanto). Stile chiaro: avorio, inchiostro, terracotta, cubi isometrici; niente
  loghi né mascotte di marchi. Esce con 1 se un campo manca o un testo non ci sta.
- "Open Post PR" disegna l'immagine, la committa sul branch e la mostra in cima
  alla PR. Se il blocco è sbagliato la PR lo dice: con il Merge esce solo il testo.
- "Publish to LinkedIn" la ridisegna dal frontmatter (così vale anche una
  correzione fatta nella PR), la carica con la Images API e la allega al post con
  il testo alternativo. Se LinkedIn rifiuta il caricamento il post non parte e il
  workflow fallisce: si può rilanciare.
- Prova senza pubblicare: Actions → "Smoke test immagine" → Run workflow. Carica
  l'immagine dell'esempio senza creare nessun post.
- Test locali: `python scripts/test_image.py` (disegno, campi sbagliati, chiamate
  all'API simulate).

### 5. Carosello (dal 2026-10-23)
- Il generatore scrive nel frontmatter un blocco `carosello:` (campi in
  `STYLE.md`, sezione "Il carosello"): copertina, da 1 a 3 slide, chiusura
  facoltativa, al massimo 4 pagine. Non committa niente in `images/`.
- `scripts/illustrazione.py` chiede a OpenAI un'illustrazione per la copertina e
  una per ogni slide di testo con il campo `illustrazione` (Images API,
  `POST /v1/images/generations`, modello `gpt-image-2.5-flare`, 1536x1024,
  qualità `medium`, JPEG). Le salva in `images/DATA/illustrazione.jpg` (copertina)
  e `illustrazione-NN.jpg` (pagina NN), ognuna con accanto un `.txt` con il prompt
  usato: finché il prompt non cambia non la richiede, quindi un secondo push non
  paga le immagini due volte. Senza chiave o con un errore di OpenAI esce con 0 e
  quella pagina esce di solo testo.
- `scripts/render_carousel.py` disegna le pagine 1080x1350 con Pillow e gli
  stessi font e colori dell'infografica: scrive le anteprime JPEG a 720 px in
  `images/DATA/slide-NN.jpg` e il PDF in `images/DATA.pdf` (in `.gitignore`).
  Niente cubi decorativi (dal 2026-10-23): restano solo nelle slide `voci`, dove
  sono il grafico.
- "Open Post PR" chiede le illustrazioni, disegna le slide, committa
  illustrazioni e anteprime sul branch e le mostra una sotto l'altra nella PR. A
  ogni push successivo sullo stesso branch (per esempio una correzione fatta da
  Marco nella PR) rifà le anteprime e aggiorna il testo della PR; un'illustrazione
  si rifà solo se è cambiata la sua scena.
- "Publish to LinkedIn" ridisegna il PDF dal frontmatter con le illustrazioni già
  committate (non le rigenera: escono quelle viste nella PR), lo carica con la
  Documents API (`/rest/documents?action=initializeUpload`, poi PUT) e lo allega
  al post con il titolo della copertina. LinkedIn elabora i documenti in modo
  asincrono, quindi il post si riprova fino a 8 volte a 10 secondi. Se la
  Documents API risponde 401/403 esce la sola copertina come immagine, con l'alt;
  qualunque altro errore blocca il post e il workflow si può rilanciare.
- Prova senza pubblicare: Actions → "Smoke test carosello" → Run workflow.
  Carica il PDF dell'esempio senza creare nessun post.
- Test locali: `python scripts/test_carousel.py` (disegno, campi sbagliati,
  illustrazioni con OpenAI simulato, pubblicazione con LinkedIn simulato).

**Secret e variabili su GitHub** (repo → Settings → Secrets and variables → Actions):
- `OPENAI_API_KEY` (secret): chiave API di OpenAI da platform.openai.com. È
  fatturata a parte rispetto all'abbonamento ChatGPT: serve credito prepagato sul
  conto API. Per i modelli GPT Image OpenAI può chiedere la verifica
  dell'organizzazione (platform.openai.com → Settings → Organization).
- `OPENAI_IMAGE_MODEL` e `OPENAI_IMAGE_QUALITY` (variabili, facoltative): per
  cambiare modello o qualità senza toccare il codice, per esempio
  `gpt-image-2.5-sunburst` o `high`.

Costo, a ottobre 2026: secondo i listini che riportano i prezzi di OpenAI,
un'immagine 1536x1024 con gpt-image-2.5 va da circa mezzo centesimo (qualità
bassa) a circa 17 centesimi (massima). Con fino a 4 immagini al giorno, anche alla
qualità massima si sta sotto i 20 dollari al mese; alla qualità media usata qui
il costo è una frazione di quel massimo. Il prezzo ufficiale è su openai.com/api/pricing.

## Rinnovo token LinkedIn (ogni ~60 giorni!)

1. Vai su https://www.linkedin.com/developers/tools/oauth/token-generator
2. App: **Content Publisher** (Client ID `7732yy3ss7c76i`)
3. Scope: `openid`, `profile`, `w_member_social` (servono i prodotti
   "Share on LinkedIn" e "Sign In with LinkedIn using OpenID Connect" — già attivi)
4. Request access token → login/allow → copia il token
5. `gh secret set LINKEDIN_ACCESS_TOKEN --repo mrkprl/linkedin-content`

## Gotcha noti

- **Il commentary NON è testo semplice** (causa del post troncato il 2026-08-10):
  il campo usa il [formato little](https://learn.microsoft.com/en-us/linkedin/marketing/community-management/shares/little-text-format)
  e questi caratteri sono riservati: `| { } @ [ ] ( ) < > # \ * _ ~`.
  Vanno escapati con backslash **anche quando non servono a nessun elemento**,
  altrimenti LinkedIn tronca silenziosamente il post al primo carattere inatteso
  e risponde comunque `201`. Il post del 10 agosto conteneva `(dovresti)` ed è
  stato tagliato al carattere 281 su 1871. Se ne occupa `escape_little_text()` in
  `scripts/publish.py`, che preserva gli hashtag `#parola` (elemento valido).
  Il generatore può quindi scrivere liberamente: non serve evitare le parentesi.
- **Il 201 non garantisce nulla**: l'API accetta il post e restituisce l'ID anche
  quando il testo verrà troncato. Il workflow non può accorgersene dalla risposta,
  per questo `scripts/test_publish.py` valida il commentary **prima** di pubblicare.
- **LinkedIn-Version scade**: le versioni API LinkedIn valgono ~12 mesi. Se il
  workflow fallisce con `426 NONEXISTENT_VERSION`, aggiorna `LINKEDIN_VERSION`
  in `scripts/publish.py` a un `YYYYMM` recente. Verificato attivo: `202607`.
- **Token 60 giorni**: LinkedIn non dà refresh token alle app standard.
  Il rinnovo è manuale (procedura sopra).
- **Rilevamento file approvati**: il workflow diffa `github.event.before..HEAD`
  con `--no-renames`, quindi i file che arrivano in `approved/` col merge della PR
  vengono rilevati come aggiunti, anche in push multi-commit e con squash merge.
- **Filtro branch obbligatorio**: `publish-to-linkedin.yml` deve avere
  `branches: [main]` nel trigger, altrimenti pubblica appena il generatore pusha
  il branch `post/*`, prima dell'approvazione.
- **Notifiche mobile**: servono l'app GitHub Mobile con le notifiche push attive
  (Impostazioni profilo GitHub → Notifications → Mobile, incluse le review request).
- **Images API con il solo `w_member_social`**: `initializeUpload` e il PUT
  funzionano, ma la GET su `/rest/images/{urn}` per leggere lo stato
  dell'immagine è negata (lo scope è di sola scrittura). Per questo
  `publish_post()` non aspetta lo stato `AVAILABLE`: se il post con immagine viene
  rifiutato lo riprova fino a 3 volte a 5 secondi di distanza. Un rifiuto non
  crea il post, quindi riprovare non fa doppioni.
- **Mai `[skip ci]` nei commit dei branch `post/*`**: con lo squash merge i
  messaggi dei commit finiscono nel commit su main, e `[skip ci]` farebbe saltare
  la pubblicazione.
- **Smoke test versione API senza pubblicare**: `POST /rest/posts` con body `{}` —
  `422` = versione ok (fallisce solo la validazione campi), `426` = versione scaduta.
- **Person ID**: è il `sub` di `GET https://api.linkedin.com/v2/userinfo` (richiede
  scope `openid profile`). Non serve la console voyager.
- **Per i commenti serve `/v2/socialActions`, non `/rest/socialActions`**
  (verificato il 2026-08-10 con `scripts/smoke_comment.py`). L'endpoint versionato
  è riservato ai partner e con un'app standard risponde
  `403 ACCESS_DENIED: partnerApiSocialActions.CREATE`. Il `/v2` legacy funziona con
  lo scope `w_member_social` che il token ha già: nel token generator quello scope
  è descritto come "Create, modify, and delete posts, **comments**, and reactions".
  La documentazione Microsoft Learn descrive solo la variante `/rest`, quindi qui
  la doc è fuorviante. `publish_comment()` prova `/v2` e poi `/rest` come fallback.
  Se un giorno fallisce, il post resta comunque pubblicato (fallire dopo la
  pubblicazione sarebbe fuorviante) e il workflow lo segnala.
- **Verificare i permessi senza sporcare un post**: `smoke-comment.yml` da
  Actions → Run workflow, passando l'URN di un post. Crea un commento di prova e
  lo cancella subito.
- **Il testo del commento NON usa il formato little**: `message.text` è testo
  semplice, quindi lì non va applicato `escape_little_text()`. Le mention nei
  commenti usano `attributes` con indici start/length, un sistema del tutto diverso
  da quello del `commentary`.
