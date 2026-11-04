# guida-riprese

La guida alle riprese: la web app con cui i clienti filmano la propria casa dal telefono, passo dopo passo, per il video dell'immobile. I video arrivano da soli nel tuo Google Drive.

**La guida:** https://foretaste-riprese.github.io/

Per ogni cliente, aggiungi l'indirizzo dell'immobile al link, così i suoi video finiscono nella sua cartella:
`https://foretaste-riprese.github.io/?casa=Via+Roma+12+Bologna` (i + al posto degli spazi tengono intero il link su WhatsApp). Senza `?casa=` la guida chiede l'indirizzo al cliente.

**Il questionario dopo la prova:** https://foretaste-riprese.github.io/questionario/

Stesso link per tutti; con `?casa=` (e, se vuoi, `&nome=Mario+Rossi`) le risposte portano già l'alloggio e il nome:
`https://foretaste-riprese.github.io/questionario/?casa=Via+Roma+12+Bologna&nome=Mario+Rossi`. Senza `nome` la pagina lo chiede.
Le risposte arrivano nel foglio **Questionario della prova**, nella cartella dei video: una riga per persona, una colonna per domanda, aggiornata mentre la persona va avanti (Stato «In corso», poi «Completato»).

## Come funziona

1. Il cliente apre il link dal telefono e segue la guida: setup, scelta dello spazio, un passo alla volta con la pianta.
2. Ogni passo lo gira con la fotocamera dentro la guida (4K, lente 0,5×): tasto rosso, gira o cammina, stop. La guida passa subito al punto dopo con la fotocamera ancora accesa, senza uscire da Chrome. Se il telefono non permette la fotocamera nel browser, la guida torna al vecchio modo: app Fotocamera e **Scegli il video**.
3. La guida manda il video a pezzi direttamente nel tuo Drive mentre lui passa al passo successivo; se cade la connessione riprende da sola. Se il telefono chiude la pagina, riaprendo il link la guida riparte dallo stesso passo.

## Cosa c'è

- `index.html`: la guida, costruita da `tools/build.py`. Non va modificata a mano.
- `design/Main.dc.html`: la guida disegnata nel canvas di Claude (schermate, testi, animazioni), generata da `design/generatore/` (vedi `CLAUDE.md`).
- `src/`: il motore che fa girare il disegno come pagina (`shell.html`), l'adattamento allo schermo (`fit.js`) e l'invio dei video (`app.js`).
- `config.js`: l'indirizzo dello script Google che riceve i video.
- `apps-script/`: lo script da installare nel tuo account Google, con le istruzioni in [`apps-script/LEGGIMI.md`](apps-script/LEGGIMI.md).
- `media/`: prato, musica e mappe per l'effetto vetro.
- `questionario/`: il questionario dopo la prova, una pagina sola con lo stesso disegno, la stessa musica e gli stessi suoni della guida. Si modifica a mano (domande in `PARTS`, in cima allo script).
- `prova-fotocamera/`: pagina di prova della fotocamera nel browser.

## Aggiornare la guida

Dopo aver cambiato `design/Main.dc.html` o `src/`:

```bash
python3 tools/build.py
```

Il comando rifà `index.html` e `version.json`. Una volta pubblicato, chi ha la guida aperta riceve la versione nuova da solo: la guida controlla `version.json` ogni pochi minuti e quando il cliente ci torna, e si ricarica nel primo momento tranquillo (nessun pannello aperto, nessun video in viaggio), restando sullo stesso passo.
