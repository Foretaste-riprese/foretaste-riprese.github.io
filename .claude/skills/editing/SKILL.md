---
name: editing
description: Sistema le foto di alloggi e stanze per annunci, sito e social (Airbnb, Booking, Instagram). Raddrizza l'orizzonte, corregge le verticali storte del grandangolo, toglie le dominanti di colore, regola esposizione, ombre e luci, ritaglia e riesporta. Per togliere oggetti o generare parti nuove prepara invece un prompt per Higgsfield. Usala quando l'utente scrive /editing o chiede di sistemare, ritoccare o migliorare una foto di un ambiente.
argument-hint: "[foto] [cosa vuoi ottenere, es. 'per Airbnb', 'togli il disordine']"
---

# /editing — sistemare le foto degli alloggi

Rispondi all'utente in italiano, con frasi semplici: non è un fotografo e non conosce i termini tecnici.

## 1. Capire cosa serve

- Le foto possono arrivare come allegati in chat (cerca il percorso del file salvato) o come file nel repository. Se non c'è nessuna foto, chiedila.
- Se l'utente non dice cosa vuole, non chiedere: guarda la foto e applica la **sistemata standard** (punto 2). Alla fine elenca in una riga cosa hai cambiato.
- Separa subito le due famiglie di interventi:
  - **Sistemata** (si fa qui, con lo script): raddrizzare, verticali, colori, esposizione, ritaglio, formato.
  - **Ritocco generativo** (non si fa qui): togliere oggetti, persone, cavi, disordine, macchie; cambiare il cielo; aggiungere luce dalla finestra; arredare. Per questi vai al punto 4. Non provare a cancellare oggetti con il codice: il risultato è sempre visibilmente finto.

## 2. Sistemata standard

Guarda la foto (Read sul file) e decidi i parametri, poi lancia lo script:

```bash
python3 .claude/skills/editing/scripts/edit_photo.py INPUT OUTPUT [opzioni] --preview ANTEPRIMA.jpg
```

Scrivi output e anteprime nella cartella scratchpad, mai sopra l'originale.

| Problema che vedi | Opzione | Valori tipici |
|---|---|---|
| Orizzonte o pavimento storto | `--rotate` | da -3 a 3 gradi (positivo = antiorario) |
| Pareti e stipiti che convergono verso l'alto (telefono inclinato in su) | `--keystone` positivo | 0.03 – 0.12 |
| Pareti che si aprono verso l'alto (telefono inclinato in giù) | `--keystone` negativo | -0.03 – -0.12 |
| Foto troppo gialla/arancione (lampadine) o troppo blu | `--wb` | 0.5 – 0.9 |
| Dopo il bilanciamento risulta fredda | `--warmth` | 0.02 – 0.05 |
| Scura o slavata | `--exposure auto` (oppure stop, es. `0.3`) | |
| Ombre chiuse / finestre bruciate | `--shadows`, `--highlights` | 0.2 – 0.6 |
| Colori spenti o troppo accesi | `--saturation` | 0.9 – 1.15 |
| Oggetti tagliati ai bordi, piatti, mani, pezzi di mobili in primo piano | `--crop l,t,r,b` (frazioni) | es. `0,0,0.92,1` |
| Formato per la destinazione | `--aspect` e `--max-side` | vedi sotto |

Formati consigliati:
- **Airbnb / Booking**: `--aspect 3:2 --max-side 2400` (orizzontale, almeno 1024 px di lato corto).
- **Sito web**: `--aspect 3:2` o `16:9`, `--max-side 2400`.
- **Instagram post**: `--aspect 4:5 --max-side 1350`. **Storie / Reel**: `--aspect 9:16 --max-side 1920`.

Poi **guarda l'anteprima** (prima a sinistra, dopo a destra) e controlla:
- le verticali (spigoli delle pareti, porte, finestre) sono verticali? Se no, ritocca `--keystone` e `--rotate` a piccoli passi e rilancia;
- i bianchi (pareti, lenzuola) sono bianchi ma la stanza resta accogliente, non grigia o azzurrina?
- niente di importante è stato tagliato via?

Massimo tre o quattro giri. Meglio una correzione leggera e credibile che una spinta.

## 3. Consegna

- Mostra il risultato con l'anteprima prima/dopo (SendUserFile) e manda il file finale come allegato.
- Elenca in breve cosa hai cambiato e con quale formato è esportato.
- Più foto della stessa casa: usa gli stessi `--wb`, `--warmth`, `--saturation` per tutte, così la serie è coerente; regola a parte solo rotazione, prospettiva e ritaglio.

## 4. Ritocco generativo: prompt per Higgsfield

Per togliere o aggiungere elementi scrivi un prompt da usare in Higgsfield con **Nano Banana Pro** (modifica di immagine, la foto come riferimento, stesse proporzioni dell'originale). Se servono anche raddrizzatura e colori, fai prima la sistemata e dai all'utente quel file come riferimento.

Schema del prompt (in inglese, rende meglio):

```text
Edit this photo of a [bedroom / living room / ...]. Keep exactly the same room, furniture, layout, camera angle, perspective and lighting.
Only change this: [remove the plate and glass on the bedside table / remove the cables under the desk / remove the clothes on the chair ...].
Fill the removed areas naturally with what would be behind them. Do not add new objects. Photorealistic, real-estate photography, true colours.
```

Regole:
- Una modifica precisa per prompt funziona meglio di tante insieme.
- Non far mai aggiungere o cambiare arredi, viste o finiture che la casa non ha: le foto dell'annuncio devono restare fedeli alla realtà.
- Se la foto mostra persone, documenti, nomi o foto di famiglia, suggerisci di toglierli.
