# LinkedIn Content: Claude per chi parte da zero

Post LinkedIn scritti da una routine Claude per il profilo di Marco Parolin. Ogni
post lascia a chi legge una cosa da provare oggi con Claude: un trucco, una
funzione, un errore da evitare, un caso d'uso da un mestiere non informatico.

## Flusso

```
routine (lun-mer-ven) → scripts/scout.py raccoglie gli spunti → scrive approved/DATA.md
→ push del branch post/DATA → la PR si apre da sola
→ Marco dal telefono: Merge = pubblica su LinkedIn · Close = scarta
```

## File da conoscere

- `IDEE.md`: dove incollare gli spunti (reel, video, trucchi). La routine li usa per primi.
- `fonti.yaml`: le fonti che la routine scansiona.
- `STYLE.md`: linea editoriale, voce, angoli, divieti.
- `ROUTINE_PROMPT.md`: copia del prompt della routine.
- `SETUP.md`: architettura, rete, soglie di forma, token LinkedIn, problemi noti.
