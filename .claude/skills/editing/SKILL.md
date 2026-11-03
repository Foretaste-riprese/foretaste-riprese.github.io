---
name: editing
description: Modifica i frame di riferimento dei video Foretaste (foto di case, stanze, esterni) per renderli cinematici, immersivi ed emotivi, sempre con lo stesso look. Usala quando il proprietario scrive /editing, manda un gruppo di foto da "editare", chiede di dare il look cinematico ai frame, o manda nuovi esempi per aggiornare il look.
---

# /editing: frame cinematici con il look Foretaste

Il proprietario manda un gruppo di foto (i frame di riferimento da cui nasce il video) e scrive `/editing`. Tu le modifichi tutte con le **regole del look** qui sotto, sempre uguali, così il video sembra girato da una sola troupe con una sola pellicola.

Rispondi in **italiano**, con frasi semplici. Spesso lavora dall'iPhone: mostragli i risultati, non i numeri.

## Stato della skill

> **Look v1 ("Luce dorata"), bozza.** Ricavato da 16 esempi (2026-11-03): 14 frame di video di interni di lusso (stile The Local Project) e 2 foto Instagram (castello nella nebbia, bosco d'autunno). Sono tutte foto "finite", senza originali. Il look è stato tarato rendendole piatte come uno scatto di telefono e poi ricolorandole (tavola in `editing/esempi/2026-11-03/prova-look-v1.jpg`). Da confermare sui primi frame veri dei clienti (iPhone, grandangolo 0,5×). Gli esempi sono screenshot compressi: grana e nitidezza misurate lì non sono affidabili.

## Regole del look ("Luce dorata")

**L'idea in una riga:** una casa silenziosa nel tardo pomeriggio. Luce di sole bassa e calda che entra di lato, ombre profonde e calde, tutto in una sola famiglia di colori (crema, sabbia, terracotta, noce, bordeaux). Lusso calmo, niente effetti.

**Attenzione:** metà di questo look nasce dalla **luce al momento della ripresa** (macchie di sole, ombre di piante e tende sui muri). Il colore da solo non la crea. Se il frame ha luce piatta o di mezzogiorno, il colore porta circa a metà strada; il resto va fatto con il ritocco luce su Higgsfield (vedi "Prompt Higgsfield").

1. **Inquadratura e formato.** 16:9 orizzontale per il video (tutti i frame di riferimento), 3:4 o 4:5 per i post. Nessuna banda nera. Composizioni ricorrenti:
   - prospettiva centrale con linee che portano dentro: corridoio, strada, sentiero (esempi 1, 2, 7, 11);
   - cornice nella cornice: porta, colonna o muro in primo piano che chiude un lato (3, 6, 10, 11);
   - un elemento in primo piano sfocato (fiori, vaso, foglie) per dare profondità (5, 10, 12);
   - dettagli stretti di materiali e oggetti: quadro, marmo, legno (9, 14, 16);
   - persone solo parziali: di spalle, piedi, un braccio, mai il volto (13, 14).
   Verticali dritte (è architettura), orizzonte dritto. Si può tagliare per stringere, mai deformare.
2. **Esposizione.** Due registri, da scegliere per scena e da non mescolare nella stessa sequenza:
   - *luce dorata* (stanze chiare col sole): mediana 0,40–0,56;
   - *penombra* (legno scuro, corridoi, sera): mediana 0,15–0,21, con i bianchi tenuti a 0,5–0,8.
   Mai tutto illuminato in modo uniforme: almeno un terzo del frame in ombra.
3. **Contrasto e curva.** Curva morbida: il contrasto lo fa la luce, non la curva (p75−p25 tra 0,10 e 0,36). **Bianco mai pieno**: il punto più chiaro sta tra 0,85 e 0,97, i pixel bruciati sono meno dello 0,2%. Le luci arrivano al bianco piano, come in pellicola. Nero profondo ma caldo (0,00–0,06), non grigio sollevato.
4. **Bilanciamento del bianco.** Caldo ambra. I bianchi sono crema o pesca, mai bianco ottico (blu/rosso nelle luci 0,65–0,90).
5. **Ombre, toni medi, luci.** Ombre marrone caldo, mai blu (blu/rosso nelle ombre 0,15–0,30). Toni medi sabbia. Luci pesca/oro, più calde dei toni medi. **Niente teal & orange.** Tavolozza quasi monocromatica: in 12 esempi su 14 di interni ombre, medi e luci stanno tutti tra 20° e 40° (arancio). L'unico freddo ammesso è la luce delle finestre e dell'esterno: pallida, poco satura, piccola nel frame.
6. **Colori singoli.** Verdi spenti e spostati verso l'oliva (piante sì, ma mai verde acceso). Cielo e blu quasi grigi. Rossi verso terracotta e bordeaux. Legno rosso-bruno, non verdognolo. Muri bianchi color crema.
7. **Saturazione.** Moderata (croma media 0,10–0,29): colori ricchi ma terrosi, nessun colore acceso o "pop". Gli esterni sono ancora più spenti (0,03–0,15).
8. **Luce.** È la protagonista. Sole basso (golden hour) radente e laterale dalle finestre. Ombre nette proiettate sui muri e sui pavimenti (piante, tende, infissi). Alternanza di zone di luce e d'ombra. Lampade spente o calde. Mai luce piatta dall'alto, flash o neon freddi.
9. **Atmosfera.** Esterni con nebbia o foschia, raggi di luce tra gli alberi (1, 2, 12). Interni con aria ferma, un leggero bagliore su tende e finestre. Silenzio: niente disordine, nessuna persona riconoscibile.
10. **Pellicola.** Pulito: grana appena percepibile, nitidezza morbida, niente effetto "HDR" o dettagli spinti. Vignetta lieve. Leggero bagliore sulle luci forti.
11. **Emozione.** Calma, intimità, lusso silenzioso. Il tempo rallentato del tardo pomeriggio: chi guarda deve sentire il calore del sole sul muro.
12. **Da non fare mai.** Bianchi bruciati. Teal & orange. Saturazione alta. HDR. Luce fredda o mista (neon + sole). Verticali storte. Grandangolo 0,5× deformato lasciato così. Testi o loghi grandi sopra la foto (i titoli, se servono, sono piccoli, serif, bianchi e centrati, come "THE LOCAL PROJECT").

### Come le regole diventano `look.json`

| Regola | Voce |
|---|---|
| bianco mai pieno, luci morbide | `curve.generale` finisce a 0,955; `compressione_luci_da` 0,75 |
| nero caldo, non sollevato | `curve.generale` parte da 0,012 |
| caldo ambra, bianchi crema | `temperatura` 40, `tinta` 6, curva blu che finisce a 0,90 |
| ombre marroni, luci pesca | `toni.ombre` 22° (0,05), `medi` 27° (0,04), `luci` 32° (0,085) |
| verdi oliva, blu spenti, legno rosso-bruno | `colori.verdi` −20°/−0,4, `gialli` −14°, `azzurri`/`blu` −0,55 |
| terroso | `saturazione` 0,92 |
| bagliore, vignetta, grana | `bloom` 0,08, `halation` 0,03, `vignetta` 0,18, `grana` 0,006 |

Per il registro *penombra* usa un look derivato con `base.esposizione` tra −0,6 e −1,0 e `curve.generale` che finisce a 0,80.

## Prompt Higgsfield (ritocco luce e scena)

Si usano solo per ciò che il colore non può fare. Il modello di modifica immagine si sceglie con `models_list`. **Non generare mai: genera il proprietario, dopo il suo consenso esplicito.** Base in inglese, da adattare alla stanza:

```
Relight this interior photo as late-afternoon golden hour: low warm sun entering
from the [left/right] window, raking across the room, casting crisp shadows of
[plants / sheer curtains / window frames] on the [wall / floor]. Keep the room,
furniture, materials and camera angle exactly the same. Warm amber highlights,
deep warm brown shadows, creamy whites never clipped, muted earthy palette,
desaturated olive greens, soft film-like roll-off, quiet luxury architectural
photography, no people, no added objects, no HDR look.
```

Varianti: «remove [object], keep everything else identical»; «straighten verticals and fill the edges naturally»; esterni: «soft morning mist, diffused light, muted autumn palette».

## Procedura per `/editing` (gruppo di foto da modificare)

1. **Trova le foto.** Cerca i file allegati su disco (`find / -xdev -mmin -120 \( -iname "*.jp*g" -o -iname "*.png" -o -iname "*.heic" -o -iname "*.webp" \) -not -path "*/.git/*" 2>/dev/null`), oppure in `editing/in/` nel repository. Se le vedi solo in chat ma non esistono su disco, chiedigli di caricarle nel repository, cartella `editing/in/<nome-gruppo>/` (dall'iPhone: sito GitHub → Add file → Upload files, sul ramo di lavoro), poi `git pull`. Copia tutto in una cartella nuova: `editing/<AAAA-MM-GG>-<nome>/originali/`.
2. **Guarda ogni foto** (strumento Read) e annota per ognuna: tipo di scena (interno giorno, interno sera, esterno, dettaglio), da dove arriva la luce, problemi (storta, sottoesposta, finestre bruciate, colori sporchi, oggetti che disturbano).
3. **Misura** il gruppo: `python3 .claude/skills/editing/scripts/analizza.py esempi <cartella>`. Serve per capire quanto ogni foto è lontana dal look e per rendere il gruppo **coerente** (stessa luminosità media, stesso nero, stesso colore delle ombre).
4. **Scegli il registro** per ogni foto (*luce dorata* o *penombra*, regola 2) e tieni lo stesso registro nelle foto della stessa stanza. **Applica il look**: `python3 .claude/skills/editing/scripts/applica.py <originali> <cartella>/editing --confronto`. Se una foto ha bisogno di una correzione in più (es. molto più scura delle altre), crea un look derivato solo per lei (copia di `look.json` con `base.esposizione` diverso, salvato come `<cartella>/look-<foto>.json`) e annotalo. Non cambiare `look.json` per una foto sola.
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
