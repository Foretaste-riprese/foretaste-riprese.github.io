---
name: editing
description: Modifica i frame di riferimento dei video Foretaste (foto di case, stanze, esterni) per renderli cinematici, immersivi ed emotivi, sempre con lo stesso look. Usala quando il proprietario scrive /editing, manda un gruppo di foto da "editare", chiede di dare il look cinematico ai frame, o manda nuovi esempi per aggiornare il look.
---

# /editing: frame cinematici con il look Foretaste

Il proprietario manda un gruppo di foto (i frame di riferimento da cui nasce il video) e scrive `/editing`. Tu le modifichi tutte con le **regole del look** qui sotto, sempre uguali, così il video sembra girato da una sola troupe con una sola pellicola.

Rispondi in **italiano**, con frasi semplici. Spesso lavora dall'iPhone: mostragli i risultati, non i numeri.

## Stato della skill

> ⚠️ **Il look non è ancora definito.** `look.json` contiene valori neutri e la sezione "Regole del look" è vuota. Le compiliamo dopo il reverse engineering delle foto di esempio del proprietario (vedi "Creare o aggiornare il look"). Finché è così, a `/editing` rispondi: «Prima mi servono le foto di esempio per costruire il look» e segui quella procedura.

## Regole del look

_(Da compilare dopo l'analisi degli esempi. Una riga per componente, con il valore e il perché. Esempio di forma: «Ombre: verso il blu-verde (190°), mai nere piene: il nero più scuro è al 4%. Perché: dà profondità senza perdere i dettagli dei mobili.»)_

1. **Inquadratura e formato:**
2. **Esposizione e luminosità generale:**
3. **Contrasto e curva** (nero, bianco, come arrivano le luci):
4. **Bilanciamento del bianco** (caldo/freddo, tinta):
5. **Colore delle ombre / toni medi / luci:**
6. **Colori singoli** (verdi, cielo, legno, pelle, muri bianchi):
7. **Saturazione:**
8. **Luce** (direzione, morbidezza, finestre, lampade, alone, bagliore):
9. **Atmosfera** (foschia, profondità, ora del giorno):
10. **Pellicola** (grana, nitidezza, vignettatura, bande nere):
11. **Emozione** (cosa deve provare chi guarda):
12. **Cose da non fare mai:**

## Procedura per `/editing` (gruppo di foto da modificare)

1. **Trova le foto.** Cerca i file allegati su disco (`find / -xdev -mmin -120 \( -iname "*.jp*g" -o -iname "*.png" -o -iname "*.heic" -o -iname "*.webp" \) -not -path "*/.git/*" 2>/dev/null`), oppure in `editing/in/` nel repository. Se le vedi solo in chat ma non esistono su disco, chiedigli di caricarle nel repository, cartella `editing/in/<nome-gruppo>/` (dall'iPhone: sito GitHub → Add file → Upload files, sul ramo di lavoro), poi `git pull`. Copia tutto in una cartella nuova: `editing/<AAAA-MM-GG>-<nome>/originali/`.
2. **Guarda ogni foto** (strumento Read) e annota per ognuna: tipo di scena (interno giorno, interno sera, esterno, dettaglio), da dove arriva la luce, problemi (storta, sottoesposta, finestre bruciate, colori sporchi, oggetti che disturbano).
3. **Misura** il gruppo: `python3 .claude/skills/editing/scripts/analizza.py esempi <cartella>`. Serve per capire quanto ogni foto è lontana dal look e per rendere il gruppo **coerente** (stessa luminosità media, stesso nero, stesso colore delle ombre).
4. **Applica il look**: `python3 .claude/skills/editing/scripts/applica.py <originali> <cartella>/editing --confronto`. Se una foto ha bisogno di una correzione in più (es. molto più scura delle altre), crea un look derivato solo per lei (copia di `look.json` con `base.esposizione` diverso, salvato come `<cartella>/look-<foto>.json`) e annotalo. Non cambiare `look.json` per una foto sola.
5. **Controlla** ogni `_prima-dopo.jpg` con Read. Domande: rispetta tutte le regole? Il gruppo sembra girato nella stessa giornata con la stessa pellicola? Ci sono luci bruciate, pelle o legno di colori strani, grana troppo forte? Se qualcosa non va, correggi e rifai.
6. **Ritocchi che il colore non può fare** (cambiare il cielo, accendere una lampada, aggiungere luce dalla finestra, togliere oggetti, raddrizzare con riempimento dei bordi): prepara per ogni foto il **prompt per Higgsfield** (modello di modifica immagine) con le regole del look dentro, in inglese, più le impostazioni consigliate. **Non generare mai**: il proprietario deve dare il consenso esplicito per ogni spesa di crediti, e il connettore è in sola lettura. Usa `models_list` / `models_get` solo per scegliere il modello e i parametri giusti.
7. **Consegna**: mandagli i `_prima-dopo.jpg` con SendUserFile e i file finali `_editing.jpg`. In poche righe: cosa hai fatto, le eccezioni foto per foto, gli eventuali prompt Higgsfield da lanciare. Chiedi se salvare il gruppo nel repository (commit e push sul ramo di lavoro).

## Creare o aggiornare il look (reverse engineering degli esempi)

Quando il proprietario manda foto di esempio «come le voglio»:

1. **Meglio le coppie prima/dopo** (stessa foto, originale e modificata, stesso nome file in due cartelle). Altrimenti vanno bene anche foto "finite".
2. Misura:
   - coppie: `python3 scripts/analizza.py coppie <cartella-prima> <cartella-dopo> --json analisi.json --scrivi-curve look.json` (impara anche le curve colore medie e le salva in `curve.tabelle`);
   - solo esempi: `python3 scripts/analizza.py esempi <cartella> --json analisi.json`.
3. **Guarda ogni esempio** e smontalo componente per componente, con la lista della sezione "Regole del look": formato e composizione, esposizione, nero e bianco, curva, bilanciamento del bianco, colore di ombre/medi/luci, colori singoli, saturazione, luce, atmosfera, grana, nitidezza, vignetta, emozione. I numeri di `analizza.py` confermano o smentiscono quello che vedi: usali entrambi. Conta solo ciò che si ripete in **quasi tutti** gli esempi: quella è la regola. Ciò che cambia da foto a foto è un'eccezione e va scritta come tale.
4. Mostra al proprietario l'analisi (una tavola con gli esempi e, accanto, le regole trovate) e decidete insieme quali tenere.
5. Traduci le regole in `look.json` (voci spiegate sotto). Prova sugli originali degli esempi e confronta il tuo risultato con il loro "dopo": correggi finché sono quasi uguali.
6. Scrivi le regole definitive nella sezione "Regole del look" (valore + perché), togli l'avviso in "Stato della skill" e fai commit e push.

## Le voci di `look.json`

Ogni voce ha un valore neutro che non cambia nulla. L'ordine di applicazione è quello della lista.

| Voce | Cosa fa | Neutro |
|---|---|---|
| `ritaglio.formato` | taglia al formato (2.39 cinema, 1.85, 1.78 = 16:9, 0.5625 = 9:16) | `null` |
| `ritaglio.centro_verticale` | dove tagliare in altezza (0 alto, 1 basso) | `0.5` |
| `base.esposizione` | stop di luce (+1 = doppio) | `0` |
| `base.temperatura` / `tinta` | + caldo / - freddo; + magenta / - verde (-100..100) | `0` |
| `curve.generale`, `r`, `g`, `b` | curva per punti `[[x,y],...]` da 0 a 1 (es. nero sollevato: `[0,0.04]`) | `null` |
| `curve.tabelle` | curve imparate dalle coppie (256 valori per canale) | `null` |
| `toni.ombre/medi/luci` | colore (`tinta_gradi`: 0 rosso, 30 arancio, 60 giallo, 120 verde, 190 teal, 230 blu) e `forza` (0.02 leggero, 0.08 forte) | `forza 0` |
| `base.saturazione` | moltiplica la saturazione | `1.0` |
| `base.vividezza` | alza i colori spenti più di quelli già forti | `0` |
| `colori.<fascia>` | per rossi, arancioni, gialli, verdi, azzurri, blu, viola: `tinta` (gradi), `saturazione` e `luminosita` (-1..1) | `0` |
| `base.compressione_luci_da` | da quale luminosità le luci vengono "frenate" come in pellicola (0.75 = morbido) | `1.0` |
| `luce.halation` | alone rossastro attorno alle luci forti: `forza`, `soglia`, `raggio` (frazione della diagonale), `colore` | `forza 0` |
| `luce.bloom` | bagliore morbido delle luci | `forza 0` |
| `vignetta` | bordi più scuri: `forza`, `inizio`, `morbidezza`, `rotondita` | `forza 0` |
| `grana` | grana da pellicola, più visibile nei toni medi: `forza` (0.015 fine, 0.04 forte), `dimensione`, `colore` | `forza 0` |
| `bande.formato` | bande nere invece del taglio | `null` |

## Strumenti

- `scripts/applica.py`: applica il look (solo Pillow e numpy, già installati). `--look` per un look diverso, `--confronto` per le tavole prima/dopo.
- `scripts/analizza.py`: misura luminosità, nero e bianco, contrasto, colore di ombre/medi/luci, saturazione per colore, vignetta, grana, formato e bande nere. Con le coppie misura anche le variazioni e impara le curve.
- `scripts/comune.py`: funzioni condivise (colore, curve, sfocatura).

## Regole del proprietario

- **Higgsfield**: «per le spese di crediti, dovrai sempre avere il mio consenso esplicito di procedere con la generazione». Prepari prompt e impostazioni, genera lui.
- Gli piace vedere subito: prima mostra i prima/dopo, poi spiega in poche righe.
