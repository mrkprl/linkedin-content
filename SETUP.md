# Setup e configurazione — linkedin-content

Stato verificato il 2026-08-07.

## Architettura

```
Routine cloud Claude (lun-mer-ven 8:00 IT) → genera il post in approved/ sul branch post/YYYY-MM-DD
GitHub Action "Open Post PR" → apre la PR di approvazione (reviewer: mrkprl)
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
- **Schedule**: `0 6 * * 1,3,5` UTC = 8:00 italiane (7:00 con ora legale) lun-mer-ven
  (era lun-ven fino al 2026-08-14: cinque post a settimana obbligavano a commentare
  anche i giorni senza una notizia degna, e il generatore riempiva descrivendo prodotti)
- **Modello**: `claude-sonnet-5`
- **Gestione**: https://claude.ai/code/routines
- La policy editoriale vive nel prompt della routine: whitelist fonti Tier 1/2
  (community solo come segnale), contestualizzazione Italia/EU, voce in prima
  persona di Marco (senza aneddoti inventati).
- **La voce e l'architettura del testo stanno in `STYLE.md`**, che è la parte
  editoriale del prompt: se cambia lì, va ricopiata nel prompt della routine.
  Le regole di forma sono verificabili e la routine le auto-controlla con
  `scripts/readability.py` prima di aprire la PR (esce con 1 se qualcosa non
  passa). Esempio di riferimento in `examples/riscrittura-2026-08-10.md`.

### Parte editoriale del prompt della routine

Aggiornata il 2026-08-13 via API (`RemoteTrigger`, action `update`). Lo Step 4 del
prompt non elenca più le regole di stile: fa aprire `STYLE.md`, la tabella qui
sotto e un file di `examples/` a ogni esecuzione, così la fonte di verità resta
una sola e cambiarla non richiede di toccare il prompt.

Nel prompt restano la tesi del profilo (in apertura, perché decide cosa si
scrive e cosa si scarta), i cinque punti da cui dipende il resto (hook
affermativo, ragionamento invece che bollettino, blocchi di lunghezza diversa,
niente glosse/attenuatori/emoji, chiusura che riprende l'hook), lo Step 5 che
impone `scripts/readability.py` a 0 prima del push, e la distinzione fra
violazioni (`!`, bloccano) e avvisi (`?`, da leggere).

**Dal 2026-08-14 i temi non sono più categorie di notizie ma angolazioni sulla
tesi** (`DA_CERCARE_A_COSTRUIRE`, `UNO_VALE_UN_TEAM`, `LAVORO_RIPETITIVO`,
`COSA_SI_ROMPE`, `LO_STRUMENTO`), e la notizia non è più il punto di partenza
obbligatorio: si parte dall'angolo e si cerca semmai un fatto che lo sostenga.
Un post può reggersi sul solo ragionamento, purché i fatti che cita siano
verificati.

Per rileggere o modificare il prompt: https://claude.ai/code/routines/trig_01E1UaHdMXwNi3Z3QydKjoHg

## Policy di forma dei post (aggiornata il 2026-08-13)

Ogni numero qui sotto viene da una misura, non da un'opinione. Le fonti sono in
fondo alla sezione. `scripts/readability.py` implementa i controlli; le regole di
voce che i numeri non catturano stanno in `STYLE.md`.

| Regola | Valore | Perché |
|---|---|---|
| Lunghezza | 1.800-2.400 caratteri | Le impression mediane crescono con la lunghezza: 575 sotto i 400 caratteri, 1.106 tra 1.301 e 2.000, 1.400 tra 2.501 e 3.000. Accorciare costa portata. |
| Hook (prima riga) | max 60 caratteri, meglio sotto 40 | Hook sotto i 40 caratteri battono quelli oltre i 200 di circa il 25% di engagement rate. |
| Tipo di hook | affermazione, fatto o confessione, **mai domanda** | Su 309.614 post l'hook a domanda è ultimo dei cinque tipi (2,16% contro 2,60% dell'hook narrativo). Bloccate anche le aperture da quiz ("Sai qual è…", "Ti sei mai chiesto…"). |
| Paragrafi | almeno 20, da 1-3 righe, max 260 caratteri l'uno | Post con 20+ paragrafi: 1,13x reach. Con 0-5 paragrafi: 0,70x. È l'effetto di formattazione più forte e costa zero. Il limite per blocco evita il muro di testo sul telefono. |
| Frasi | mai oltre 25 parole, media 12-18 | Direttiva sulla semplificazione del linguaggio dei testi amministrativi (8/5/2002), regola 1; Cortelazzo-Pellegrino regola 12. |
| Gulpease | ≥ 60, target 70 | Sotto 60 il testo non è leggibile in autonomia da chi ha la licenza media. È l'indice tarato sull'italiano (Lucisano-Piemontese 1988), non Flesch. |
| Glosse didascaliche | **zero** | "cioè", "ovvero", "in altre parole": presuppongono un lettore che non capisce e fanno suonare il testo come un tema di scuola. Al loro posto va un esempio concreto. |
| Attenuatori | max 2 | "un po'", "forse", "onestamente": oltre due, il post non afferma più niente e la voce si sfalda. |
| Link nel corpo | **nessuno** | Sui profili personali un link costa −27% impression e −20% interazioni. Sulle pagine aziendali l'effetto è opposto (+51%): da qui gran parte della confusione in circolazione. |
| Fonti | nel primo commento, in automatico | Vedi `source_comment()` e `publish_comment()` in `publish.py`. |
| Hashtag | 3, ultima riga, mai in apertura | L'effetto sulla portata è vicino a zero, ma un hashtag in prima riga rovina lo slug dell'URL. |
| CTA | domanda che richiede esperienza personale | Le domande generiche ("Sei d'accordo?") sono engagement bait dichiarato e vengono ridotte. Una domanda specifica sposta l'engagement dai like ai commenti (+77% commenti), che pesano di più. |
| Blocchi da una riga sola | max 50%, meglio ~33% | Nei post riusciti due blocchi su tre raggruppano 2-3 righe. Sopra il 50% il testo ansima e si legge come un elenco puntato senza punti (post del 14-08: 59%, zero reazioni). |
| Spazio dedicato ai fatti | max un quarto del testo | Il resto è il ragionamento. Se la notizia occupa di più, il tema era debole. Mai descrivere un'interfaccia: è manuale utente. |
| Tesi | deve poter essere contestata | Un luogo comune ("non è quanto usi l'AI, è come la usi") non genera commenti. Se nessuno può dissentire, non c'è tesi: cambia tema, o quel giorno non si pubblica. |
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
(AI, coding, strumenti) è la leva di portata numero uno.

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
  - `LINKEDIN_ACCESS_TOKEN` — impostato 2026-08-05, **scade ~2026-10-05**
  - `LINKEDIN_PERSON_ID` — `IJ0yQ3PjVm` (il claim `sub` di `/v2/userinfo`, stabile)

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
