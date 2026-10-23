# LinkedIn Content: le novità dell'AI per chi lavora

Post LinkedIn scritti da una routine Claude per il profilo di Marco Parolin. Ogni
giorno una novità seria dell'AI (un modello, un agente, una funzione che cambia
cosa si può fare con Claude, ChatGPT, Gemini o Copilot), raccontata a chi lavora
e l'AI la usa già: cos'è, cosa fa, il dettaglio che conta, chi può usarla. Ogni
post esce con un carosello sul modello di @ai__facile e @profession.ai, con
l'illustrazione della copertina disegnata da ChatGPT.

## Flusso

![Schema del flusso](docs/schema-flusso.png)

In breve: la routine (ogni giorno alle 7:55) scrive `approved/DATA.md` e fa push del
branch `post/DATA`. La Action "Open Post PR" chiede l'illustrazione a OpenAI,
disegna il carosello e apre la PR con le slide. Marco dal
telefono decide: Merge = pubblica su LinkedIn, Close = scarta. Lo schema è
un'immagine fissa: se il flusso cambia, va rifatta.

Dal 23 ottobre 2026 i post si preparano in anticipo in `programmati/`, uno per
giorno, e una Action li pubblica ogni mattina alle 8:30 (vedi `SETUP.md`, sezione
"6. Post programmati"). La routine giornaliera è in pausa.

## File da conoscere

- `programmati/`: i post pronti, uno per giorno (`AAAA-MM-GG.md`).
- `IDEE.md`: dove incollare gli spunti (reel, video, trucchi). La routine li usa per primi.
- `fonti.yaml`: le fonti che la routine scansiona.
- `STYLE.md`: linea editoriale, voce, angoli, divieti.
- `ROUTINE_PROMPT.md`: copia del prompt della routine.
- `SETUP.md`: architettura, rete, soglie di forma, token LinkedIn, problemi noti.
