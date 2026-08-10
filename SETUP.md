# Setup e configurazione — linkedin-content

Stato verificato il 2026-08-07.

## Architettura

```
Routine cloud Claude (lun-ven 8:00 IT) → genera il post in approved/ sul branch post/YYYY-MM-DD
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
- **Schedule**: `0 6 * * 1-5` UTC = 8:00 italiane (7:00 con ora legale) lun-ven
- **Modello**: `claude-sonnet-5`
- **Gestione**: https://claude.ai/code/routines
- La policy editoriale vive nel prompt della routine: whitelist fonti Tier 1/2
  (community solo come segnale), contestualizzazione Italia/EU, fonte citata nel post,
  stile senza segni tipici da AI (niente trattini lunghi né frecce), tono simpatico
  e sfidante accessibile ai non addetti, voce in prima persona di Marco (senza
  aneddoti inventati), specificità progressiva (divulgativo sotto i 20 post
  pubblicati, poi via via più tecnico), formato confronto opzionale tra due
  notizie quando il materiale lo permette, emoji con misura (2-3 per post),
  firma fissa "P.S. ... con il supporto del mio amico Claudio Code 🙂".

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
