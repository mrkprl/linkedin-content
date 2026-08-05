# Setup e configurazione — linkedin-content

Stato verificato il 2026-08-05.

## Architettura

```
Routine cloud Claude (lun-ven 8:00 IT) → genera bozza → pending/
Tu approvi → sposti il file in approved/ → push
GitHub Actions → pubblica su LinkedIn → sposta in published/
```

## Componenti

### 1. Generazione contenuti — routine cloud Claude
- **Routine**: `linkedin-content-generator` (`trig_01E1UaHdMXwNi3Z3QydKjoHg`)
- **Schedule**: `0 6 * * 1-5` UTC = 8:00 italiane (7:00 con ora legale) lun-ven
- **Modello**: `claude-sonnet-5`
- **Gestione**: https://claude.ai/code/routines
- La policy editoriale (whitelist fonti Tier 1/2, community solo come segnale,
  contestualizzazione Italia/EU, fonte citata nel post) vive nel prompt della routine.

### 2. Pubblicazione — GitHub Actions
- Workflow: `.github/workflows/publish-to-linkedin.yml` — trigger su push di `approved/**.md`
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

- **LinkedIn-Version scade**: le versioni API LinkedIn valgono ~12 mesi. Se il
  workflow fallisce con `426 NONEXISTENT_VERSION`, aggiorna `LINKEDIN_VERSION`
  in `scripts/publish.py` a un `YYYYMM` recente. Verificato attivo: `202607`.
- **Token 60 giorni**: LinkedIn non dà refresh token alle app standard.
  Il rinnovo è manuale (procedura sopra).
- **Rilevamento file approvati**: il workflow diffa `github.event.before..HEAD`
  con `--no-renames`, quindi sia `git mv` da `pending/` sia file nuovi in
  `approved/` vengono rilevati, anche in push multi-commit.
- **Smoke test versione API senza pubblicare**: `POST /rest/posts` con body `{}` —
  `422` = versione ok (fallisce solo la validazione campi), `426` = versione scaduta.
- **Person ID**: è il `sub` di `GET https://api.linkedin.com/v2/userinfo` (richiede
  scope `openid profile`). Non serve la console voyager.
