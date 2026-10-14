# LinkedIn Content: il mondo AI per chi parte da zero

Post LinkedIn scritti da una routine Claude per il profilo di Marco Parolin:
gli strumenti AI che si usano, le ultime notizie dai produttori e le idee che
Marco lascia in `IDEE.md`. Ogni post lascia a chi legge una cosa concreta: un
trucco, una funzione, un errore da evitare, una notizia spiegata per quello che
cambia per lui.

## Flusso

```
routine (ogni giorno) → scripts/scout.py raccoglie gli spunti → scrive approved/DATA.md
→ push del branch post/DATA → la PR si apre da sola
→ Marco dal telefono: Merge = pubblica su LinkedIn · Close = scarta
```

## File da conoscere

- `IDEE.md`: dove incollare gli spunti (reel, video, trucchi). La routine li usa per primi e fa da sola la ricerca.
- `fonti.yaml`: le fonti che la routine scansiona.
- `STYLE.md`: linea editoriale, voce, angoli, divieti.
- `ROUTINE_PROMPT.md`: copia del prompt della routine.
- `SETUP.md`: architettura, rete, soglie di forma, token LinkedIn, problemi noti.
