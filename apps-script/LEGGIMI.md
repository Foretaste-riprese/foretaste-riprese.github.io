# Lo script che riceve i video nel tuo Google Drive

La guida manda ogni video direttamente nel tuo Drive. Questo script, che gira con il tuo account Google, apre il "passaggio" per ogni video e salva i feedback in un foglio. Si installa una volta sola, in circa 5 minuti, dal computer.

## 1. La cartella

1. Su Google Drive crea una cartella, per esempio **Riprese clienti**.
2. Aprila e copia l'ultima parte dell'indirizzo: in `https://drive.google.com/drive/folders/1AbC…xyz` è `1AbC…xyz`. È l'**ID della cartella**.

La cartella resta privata: non va condivisa con nessuno.

## 2. Lo script

1. Vai su https://script.google.com e tocca **Nuovo progetto**. Chiamalo **Guida alle riprese**.
2. Cancella tutto quello che c'è in `Codice.gs` e incolla il contenuto di [`Code.gs`](Code.gs).
3. Nella riga `const FOLDER_ID = 'INCOLLA_QUI_L_ID_DELLA_CARTELLA';` metti l'ID della cartella, tra gli apici.
4. Tocca **Impostazioni progetto** (l'ingranaggio a sinistra) e spunta **Mostra il file manifest "appsscript.json" nell'editor**. Torna all'editor, apri `appsscript.json` e sostituisci tutto con il contenuto di [`appsscript.json`](appsscript.json).
5. Salva (icona del dischetto).

## 3. La pubblicazione

1. In alto a destra tocca **Esegui il deployment → Nuovo deployment**.
2. Tipo: **App web**.
   - Esegui come: **Me**
   - Chi ha accesso: **Chiunque**
3. Tocca **Esegui il deployment** e autorizza l'accesso con il tuo account. Google avvisa che l'app non è verificata: tocca **Avanzate → Vai a Guida alle riprese (non sicuro)**. È normale per uno script tuo.
4. Copia l'**URL dell'app web** (finisce con `/exec`) e mandalo a Claude, oppure incollalo in `config.js` nella riga `scriptUrl: ''`.

Per controllare che funzioni, apri quell'indirizzo nel browser: deve comparire `{"ok":true,"guida":"pronta"}`.

## Cosa arriva nel Drive

- Una sottocartella per ogni immobile, con il nome scritto nel link della guida (`?casa=Via Roma 12`) o dal cliente.
- Le **foto** di ogni passo, in 4K, con il nome del passo, per esempio `Ambiente Rettangolare · passo 03 di 10 · Punto 1 · foto 07.jpg` (dove il telefono non può fare le foto, un video con lo stesso nome).
- Il foglio **Feedback della guida**, con data, immobile, stelle e commento.
- Il foglio **Questionario della prova**, con le risposte al questionario dopo la prova: una riga per persona, una colonna per domanda. La riga si aggiorna da sola mentre la persona risponde; quando ha finito, lo Stato diventa «Completato».
- Le risposte date a voce nel questionario, come file audio nella cartella dell'immobile (es. `Questionario · Mario Rossi · domanda 05 · voce 1.m4a`); nel foglio, al posto della risposta, c'è il link per ascoltarle.

## Se cambi lo script

Dopo una modifica: **Esegui il deployment → Gestisci deployment → Modifica (matita) → Versione: nuova versione → Esegui il deployment**. L'indirizzo `/exec` resta lo stesso.

## Da sapere

Chi conosce l'indirizzo dello script può mandare video nella cartella: è scritto nel codice della guida, quindi non è segreto. Lo script accetta solo foto, video e audio, ma se un giorno ricevi file che non c'entrano, crea un nuovo deployment (l'indirizzo cambia) e aggiorna `config.js`.
