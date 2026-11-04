# Guida alle riprese (Foretaste): contesto per Claude

Leggi tutto prima di cambiare qualcosa. Il proprietario scrive in **italiano**: rispondi in italiano, con frasi semplici, e spiega cosa deve fare lui passo per passo (spesso lavora dall'iPhone).

## Cos'è

Una web app per i clienti di un'agenzia immobiliare: dal telefono il cliente segue la guida e riprende la casa passo dopo passo (stanze, corridoio, scale) con la **fotocamera dentro la guida** (lente 0,5×, 4K): tasto rosso, gira, stop, e la guida passa da sola al punto dopo con la fotocamera ancora accesa. Ogni video va da solo nel Google Drive del proprietario. Dove la fotocamera nel browser non si può usare (permesso negato, browser senza MediaRecorder) la guida torna al vecchio modo: app Fotocamera e scelta del video dalla galleria. Lo stile è di lusso (riferimento Son Daven): prato al vento come sfondo, titoli in Bodoni Moda (simile a Vogue), vetro "liquid glass", animazione "posa" (come una tazzina appoggiata), musica Gymnopédie n. 1 e piccoli suoni (colpi di legno morbidi, "ba" sui punti, "tchk" ai tocchi). In cima a ogni schermata c'è la scritta FORETASTE.

## Dove sta tutto

| Cosa | Dove |
|---|---|
| La guida, per i clienti | https://foretaste-riprese.github.io (link con casa: `/?casa=Via+Roma+12+Bologna`) |
| Questo repository | `Foretaste-riprese/foretaste-riprese.github.io`, **pubblico**. GitHub Pages pubblica il ramo **`prova-fotocamera`**, cartella `/` (non `main`) |
| Il disegno della guida (canvas Claude Design) | https://claude.ai/artifact/7NN2ZMwx3rmTpH1Hf3JdYf, una tavola sola `project/Main.dc.html` |
| La guida "grande" originale, 16 tavole (canvas) | https://claude.ai/artifact/FPq2VEwApcULY1hsFdqhjY, copia dei file in `design/generatore/canvas/project/` |
| Il questionario dopo la prova | https://foretaste-riprese.github.io/questionario/ (con `?casa=…&nome=…`). Pagina a mano in `questionario/index.html`: stessi colori, Bodoni Moda, prato, vetro `.gl`, animazione «posa», musica e suoni copiati dalla guida (stesso interruttore `guida-suoni-v2`). Domande in `PARTS`. Manda tutta la riga all'azione `questionario` dello script, foglio «Questionario della prova». Voce: «Detta la risposta» (SpeechRecognition, testo) dove funziona, cioè Safari su iPhone e Chrome altrove; negli altri browser (Chrome e browser delle app su iPhone) «Rispondi a voce» registra con MediaRecorder, salva nell'IndexedDB e carica l'audio con l'azione `start` nella cartella dell'immobile; nel foglio va il link |
| Video e feedback | Google Drive del proprietario, cartella **"Riprese proprietà dei miei clienti"**: una sottocartella per immobile, il foglio "Feedback della guida" e (dopo l'aggiornamento dello script) "Problemi della guida" |
| Lo script Google che riceve | Apps Script "Guida alle riprese" nell'account del proprietario. Indirizzo in `config.js`. Il codice di riferimento è `apps-script/Code.gs` |
| Vecchie prove su claude.ai (superate) | Pagina con archivio https://claude.ai/artifact/7hXVnd46fSKdnPfjr1Xtq7, versione "solo guida" https://claude.ai/artifact/YKkEQfjzLL8cesCqrhwMMW |

## Come è fatta

- `design/generatore/scripts/build_proto.py` è la **fonte del disegno**: genera `Main.dc.html` (schermate, pianta animata, schizzi a matita, suoni, testi dei passi in `stepsOf`, punti in `proto_data.json`). Usa `build_screens.py`, che prende CSS, vetro e logica dei suoni da `canvas/project/Stanza.dc.html`.
- `design/Main.dc.html` è il disegno generato: lo stesso file pubblicato nel canvas.
- `tools/build.py` trasforma il disegno in `index.html`, con il motore in `src/shell.html` (fa girare il formato del canvas come pagina normale), `src/fit.js` (tutto schermo) e `src/app.js` (fotocamera nella guida, ripiego sull'app Fotocamera, invio a Drive, memoria dopo la ricarica, aggiornamento automatico, segnalazioni). Scrive anche `version.json`.
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
- **Fotocamera nella guida** (dal 4/11, per togliere lentezza, attese e andirivieni con l'app Fotocamera): schermata `rec` del disegno, con due stati. «Pronto» (`ready: true`): fotocamera accesa, pianta piccola e testo del passo in alto, tasto rosso, «Pianta» (torna alla schermata del passo), «Salta» (solo punti), «Rifai «…»» subito dopo una ripresa. «In registrazione»: cerchio o frecce del passo, tempo vero, stop. Stop → il video entra nella coda d'invio (prima nell'IndexedDB, poi riletto da lì per non tenerlo in memoria) e compare il passo dopo, «pronto». Riprese sotto 1,5 s non valgono («Troppo breve»). In `app.js`: `getUserMedia` (lente scelta per nome `/ultra/`, ricordata in `guida-lente`; su Android zoom minimo), `MediaRecorder` mp4 H.264 a **30 Mbit/s** (`BITRATE`), **senza audio** (il proprietario: l'audio non serve, contano i frame; un leggero tremolio va bene). La fotocamera è accesa solo sulla schermata `rec`; se esci dalla pagina a metà ripresa, la ripresa si butta e il passo resta da rifare. Il permesso si chiede sulla schermata «La fotocamera, qui dentro» (`allowCamera`). Gli avvisi d'esempio del canvas (Più piano, Tieni dritto…) e la livella sono spenti nella guida vera (`PROPS.avviso = 'Nessuno'`): non ci sono ancora i sensori.
- **Meno tempo per stanza** (5/11): dalla forma della stanza (o da Corridoio) si va **dritti alla fotocamera** «pronta» sul passo 1, senza la schermata della pianta grande (resta con «Pianta»); dopo l'ultimo passo si va **dritti a «Cosa riprendi adesso?»** (`space` con `fatto`), senza «Spazio finito». La fotocamera si accende già sulla schermata del passo se il permesso c'è (`CAM.granted`), così Registra registra subito.
- **Segui la freccia, nello spazio** (solo nei giri, non nelle camminate; 5/11 su richiesta del proprietario): al centro un cerchio fisso; una linea tratteggiata parte da dove punta il telefono all'inizio della ripresa e copre tutto il giro (6 px per grado, `AIM_K`, circa il campo della lente 0,5×); una freccia la percorre a 15°/s dopo 0,6 s (`AIM_WAIT`). Con i **sensori di movimento** (`devicemotion`: giroscopio proiettato sulla gravità, gradi sommati in `MOT.yaw`) linea e freccia scorrono al contrario di quanto giri: chi gira al passo giusto tiene la freccia nel cerchio. Si muovono solo con `transform` in `aimLoop` (una volta per fotogramma), **mai** con `setState` o variabili sul `body`: sull'iPhone l'immagine della fotocamera si bloccava quando la pagina si ridisegnava di continuo. Il tempo scorre scrivendo direttamente in `.rec-clock`. La ripresa **si ferma da sola solo quando sono in fondo tutte e due**, telefono (giro completo, meno 4°) e freccia (`MOT.arrowMs`): chi va più lento non viene tagliato, chi va più veloce aspetta la freccia (due note, poi il passo dopo). Il permesso «Movimento» l'iPhone lo chiede su «Consenti» o al primo tasto rosso (serve un tocco). Senza sensori: la linea scorre con la freccia (mostra il ritmo) e alla fine un suono con «Fatto. Tocca stop». Le camminate si fermano a mano. Nel canvas un'animazione CSS mostra l'idea; nella guida è spenta (classe `aim-live`).
- **Voce**: `speechSynthesis` in italiano legge il passo quando è «pronto» («Vai al punto 3. Tocca il tasto rosso e gira…»), «Segui la freccia» quando parte, «Spazio finito» alla fine. Sempre accesa (non segue il tasto della musica).
- **Da verificare sull'iPhone vero** (in locale si prova solo con la fotocamera finta di Chromium): che il video arrivi dritto (verticale), la stabilizzazione (probabilmente il browser non la attiva come l'app Fotocamera), la qualità a 30 Mbit/s, Chrome per iPhone.
- **Dove era il cliente** si salva in `localStorage` (`guida-stato:<casa>`, valido 7 giorni), non più solo in `sessionStorage`: se il telefono chiude Chrome, riaprendo il link la guida torna allo stesso passo (una schermata di registrazione torna come schermata del passo).
- **iPhone, scelta del video** (solo nel ripiego con l'app Fotocamera): il menu (Libreria foto / Registra video / Scegli file, in Chrome anche Google Drive) lo decide iOS; il sito non può togliere voci. Dopo la scelta, iOS converte il video: qualche secondo di attesa, e probabilmente anche meno qualità. La prova è in `prova-video/`. `prova-fotocamera/` è la prova che ha mostrato che l'iPhone dà al sito la grandangolare 0,5× in 4K a 30 fps.
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
