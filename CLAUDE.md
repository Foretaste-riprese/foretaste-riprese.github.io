# Guida alle riprese (Foretaste): contesto per Claude

Leggi tutto prima di cambiare qualcosa. Il proprietario scrive in **italiano**: rispondi in italiano, con frasi semplici, e spiega cosa deve fare lui passo per passo (spesso lavora dall'iPhone).

## Cos'è

Una web app per i clienti di un'agenzia immobiliare: dal telefono il cliente segue la guida, riprende la casa passo dopo passo (stanze, corridoio, scale) con l'app Fotocamera e sceglie il video nella guida, che lo manda da solo nel Google Drive del proprietario. Lo stile è di lusso (riferimento Son Daven): prato al vento come sfondo, titoli in Bodoni Moda (simile a Vogue), vetro "liquid glass", animazione "posa" (come una tazzina appoggiata), musica Gymnopédie n. 1 e piccoli suoni (colpi di legno morbidi, "ba" sui punti, "tchk" ai tocchi). In cima a ogni schermata c'è la scritta FORETASTE.

## Dove sta tutto

| Cosa | Dove |
|---|---|
| La guida, per i clienti | https://foretaste-riprese.github.io (link con casa: `/?casa=Via+Roma+12+Bologna`) |
| Questo repository | `Foretaste-riprese/foretaste-riprese.github.io`, **pubblico**. GitHub Pages pubblica il ramo **`prova-fotocamera`**, cartella `/` (non `main`) |
| Il disegno della guida (canvas Claude Design) | https://claude.ai/artifact/7NN2ZMwx3rmTpH1Hf3JdYf, una tavola sola `project/Main.dc.html` |
| La guida "grande" originale, 16 tavole (canvas) | https://claude.ai/artifact/FPq2VEwApcULY1hsFdqhjY, copia dei file in `design/generatore/canvas/project/` |
| Il questionario dopo la prova | https://foretaste-riprese.github.io/questionario/ (con `?casa=…&nome=…`). Pagina a mano in `questionario/index.html`: stessi colori, Bodoni Moda, prato, vetro `.gl`, animazione «posa», musica e suoni copiati dalla guida (stesso interruttore `guida-suoni-v2`). Domande in `PARTS`. Manda tutta la riga all'azione `questionario` dello script, foglio «Questionario della prova» |
| Video e feedback | Google Drive del proprietario, cartella **"Riprese proprietà dei miei clienti"**: una sottocartella per immobile, il foglio "Feedback della guida" e (dopo l'aggiornamento dello script) "Problemi della guida" |
| Lo script Google che riceve | Apps Script "Guida alle riprese" nell'account del proprietario. Indirizzo in `config.js`. Il codice di riferimento è `apps-script/Code.gs` |
| Vecchie prove su claude.ai (superate) | Pagina con archivio https://claude.ai/artifact/7hXVnd46fSKdnPfjr1Xtq7, versione "solo guida" https://claude.ai/artifact/YKkEQfjzLL8cesCqrhwMMW |

## Come è fatta

- `design/generatore/scripts/build_proto.py` è la **fonte del disegno**: genera `Main.dc.html` (schermate, pianta animata, schizzi a matita, suoni, testi dei passi in `stepsOf`, punti in `proto_data.json`). Usa `build_screens.py`, che prende CSS, vetro e logica dei suoni da `canvas/project/Stanza.dc.html`.
- `design/Main.dc.html` è il disegno generato: lo stesso file pubblicato nel canvas.
- `tools/build.py` trasforma il disegno in `index.html`, con il motore in `src/shell.html` (fa girare il formato del canvas come pagina normale), `src/fit.js` (tutto schermo) e `src/app.js` (Registra con la Fotocamera, invio a Drive, memoria dopo la ricarica, aggiornamento automatico, segnalazioni). Scrive anche `version.json`.
- Le pagine aperte dai clienti si **aggiornano da sole** quando cambia `version.json`, nel primo momento tranquillo, restando sullo stesso passo.

### Cambiare il disegno e pubblicare

```bash
cd design/generatore/canvas/project
python3 ../../scripts/build_proto.py ../../..     # scrive design/Main.dc.html
cd ../../../..
python3 tools/build.py                            # scrive index.html e version.json
git add -A && git commit && git push origin prova-fotocamera
```

Poi, se serve, ripubblica il canvas con lo strumento Artifact: `url` del canvas, `root` = una cartella con `project/Main.dc.html`, e solo quel file in `files`. Il canvas va aggiornato **insieme** alla guida: il proprietario ci guarda e chiede modifiche anche lì. Per cambiare solo il comportamento (invio, testi del pannello Registra, aggiornamento) basta `src/app.js` e poi `tools/build.py`.

## Cose da sapere (ci siamo già cascati)

- **Cache di GitHub Pages**: un telefono tiene la pagina fino a 10 minuti. Per una prova: Ctrl+Maiusc+R, oppure aggiungi `&v=N` al link. `config.js` è caricato con l'impronta del contenuto, quindi un cambio di indirizzo dello script arriva subito.
- **Script Google**: ogni modifica va incollata dal proprietario e poi **ogni deployment** va portato alla nuova versione (Gestisci deployment → matita → Versione). In `ORIGINS` deve esserci l'indirizzo della guida, altrimenti i video non partono (il feedback sì). L'ID cartella va scritto senza `?hl=it`.
- **iPhone**: il volume della musica non si può cambiare (la dissolvenza non arriva mai a zero) e l'audio si sospende dopo la Fotocamera: `app.js` ferma subito la musica e la riaccende al primo tocco. **Non** usare `navigator.audioSession.type = 'ambient'`: con il silenzioso la guida diventa muta.
- **iPhone, scelta del video**: il menu (Libreria foto / Registra video / Scegli file, in Chrome anche Google Drive) lo decide iOS; il sito non può togliere voci. Dopo la scelta, iOS converte il video: qualche secondo di attesa, e probabilmente anche meno qualità (arriva H.264 invece di HEVC). Non risolto, rimandato dal proprietario. La prova è in `prova-video/`.
- **Fotocamera nel browser**: l'iPhone dà al sito la grandangolare 0,5× in 4K a 30 fps (vedi `prova-fotocamera/`). È la strada per registrare dentro la guida, se un giorno servirà.
- Da questa sessione cloud non si raggiungono `*.github.io` né i server Google: le prove dal vivo le fa il proprietario sull'iPhone. In locale si prova con Playwright e un finto Drive.
- GitHub: niente GraphQL. Per creare repository o attivare Pages deve agire il proprietario.

## Regole del proprietario

- **Higgsfield** (generazione video e immagini): "per le spese di crediti, dovrai sempre avere il mio consenso esplicito di procedere con la generazione". Il connettore è in sola lettura; si preparano prompt e impostazioni, poi genera lui.
- Gli piace vedere le cose subito: pubblica, poi dì in poche righe cosa è cambiato e cosa deve fare lui.

## In sospeso

0. **Questionario**: lo script del proprietario deve avere l'azione `questionario` (incollare tutto `apps-script/Code.gs`, rimettere l'ID cartella, portare i deployment alla nuova versione). Finché non lo fa, la pagina tiene le risposte sul telefono e riprova.

1. **Segnalazioni automatiche**: la guida le manda già. Lo script nell'account del proprietario però non ha ancora l'azione `report`. Deve incollare tutto `apps-script/Code.gs` (rimettendo il suo ID cartella alla riga 11) e portare i deployment alla nuova versione. Finché non lo fa, le segnalazioni vengono ignorate senza danni.
2. **Feedback in tempo reale a Claude**: idea proposta, non fatta. Lo script pubblica ogni feedback come commento in un repository **privato** `foretaste-feedback` (token GitHub nelle Proprietà dello script, mai nel codice), la sessione si iscrive alle notifiche e manda al proprietario un messaggio con le opzioni.
3. **Dominio proprio** (es. `riprese.foretaste.it`): rimandato per costi. Richiede un record CNAME, un Custom domain su Pages e il nuovo indirizzo in `ORIGINS`.
4. **Scala (centinaia di migliaia di immobili)**: il proprietario usa un CRM e contatta via WhatsApp. Piano: un link per immobile generato dal CRM, invio con WhatsApp Business Platform, archivio video vero (Cloudflare R2 o S3) al posto di Drive, stato che torna nel CRM. Non iniziato; servono nome del CRM, volumi e conservazione dei video.
5. La guida "grande" a 16 tavole (canvas FPq2…) andrà allineata al prototipo, che è più avanti.
