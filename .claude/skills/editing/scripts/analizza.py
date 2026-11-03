#!/usr/bin/env python3
"""Misura il look di foto di riferimento (reverse engineering) per /editing.

Uso:
  python3 analizza.py esempi <foto-o-cartella>             # foto "finite": misura il look
  python3 analizza.py coppia <prima.jpg> <dopo.jpg>        # stessa foto prima/dopo: ricava le correzioni
  python3 analizza.py coppie <cartella-prima> <cartella-dopo> [--scrivi-curve look.json]

Stampa un riassunto leggibile e un JSON con i numeri. Le misure sono il punto
di partenza: vanno sempre confermate guardando le foto.
"""
import argparse
import json
from pathlib import Path
import numpy as np
from PIL import Image
import comune as C


def riduci(img, lato=1200):
    h, w = img.shape[:2]
    s = lato / max(h, w)
    if s >= 1:
        return img
    im = Image.fromarray((img * 255).astype(np.uint8)).resize((int(w * s), int(h * s)), Image.LANCZOS)
    return np.asarray(im, np.float32) / 255


def nome_tinta(g):
    nomi = [(15, "rosso"), (45, "arancio"), (70, "giallo"), (160, "verde"), (200, "ciano/teal"),
            (250, "blu"), (290, "viola"), (335, "magenta"), (360, "rosso")]
    for lim, n in nomi:
        if g < lim:
            return n
    return "rosso"


def colore_zona(img, maschera):
    if maschera.sum() < 50:
        return None
    m = img[maschera].mean(0)
    dev = m - m.mean()
    h, s, _ = C.rgb_a_hsv(m[None, None, :] / max(m.max(), 1e-6))
    return {"rgb_medio": [round(float(x), 3) for x in m],
            "sbilanciamento": [round(float(x), 3) for x in dev],
            "tinta_gradi": round(float(h[0, 0]), 1),
            "verso": nome_tinta(float(h[0, 0])),
            "intensita": round(float(np.abs(dev).max()), 3)}


def misura(img_piena):
    H, W = img_piena.shape[:2]
    img = riduci(img_piena)
    y = C.luma(img)
    h, s, v = C.rgb_a_hsv(img)
    p = np.percentile(y, [0.5, 2, 5, 25, 50, 75, 95, 98, 99.5])
    # vignettatura: luminosità ai bordi rispetto al centro
    hh, ww = y.shape
    cy, cx = hh // 2, ww // 2
    centro = y[cy - hh // 6:cy + hh // 6, cx - ww // 6:cx + ww // 6].mean()
    k = max(4, min(hh, ww) // 10)
    angoli = np.mean([y[:k, :k].mean(), y[:k, -k:].mean(), y[-k:, :k].mean(), y[-k:, -k:].mean()])
    # grana: rumore fine nelle zone piatte
    piena_y = C.luma(img_piena[::max(1, H // 1500), ::max(1, W // 1500)])
    alta = piena_y - C.sfoca(piena_y, 1.5)
    struttura = np.abs(C.sfoca(piena_y, 1.5) - C.sfoca(piena_y, 6))
    piatte = struttura < np.percentile(struttura, 30)
    # bande nere
    righe = C.luma(img_piena).mean(1)
    sopra = int(np.argmax(righe > 0.02)) if righe[0] < 0.02 else 0
    sotto = int(np.argmax(righe[::-1] > 0.02)) if righe[-1] < 0.02 else 0
    utile = H - sopra - sotto
    tinte = {}
    colorati = s > 0.15
    for nome, centro_h in C.FASCE.items():
        w = C.peso_fascia(h, centro_h) * colorati
        if w.sum() > 0.01 * w.size:
            tinte[nome] = {"quota": round(float(w.sum() / w.size), 3),
                           "saturazione_media": round(float((s * w).sum() / w.sum()), 3),
                           "luminosita_media": round(float((v * w).sum() / w.sum()), 3)}
    return {
        "dimensioni": [W, H],
        "formato": round(W / H, 3),
        "formato_utile_senza_bande": round(W / max(utile, 1), 3),
        "bande_nere_px": [sopra, sotto],
        "luminosita": {
            "nero_0.5%": round(float(p[0]), 3), "p2": round(float(p[1]), 3), "p5": round(float(p[2]), 3),
            "p25": round(float(p[3]), 3), "mediana": round(float(p[4]), 3), "p75": round(float(p[5]), 3),
            "p95": round(float(p[6]), 3), "p98": round(float(p[7]), 3), "bianco_99.5%": round(float(p[8]), 3),
            "contrasto_p75-p25": round(float(p[5] - p[3]), 3),
            "pixel_bruciati_%": round(float((y > 0.985).mean() * 100), 2),
            "pixel_neri_%": round(float((y < 0.01).mean() * 100), 2),
        },
        "colore_zone": {
            "ombre": colore_zona(img, y < np.percentile(y, 20)),
            "medi": colore_zona(img, (y > np.percentile(y, 40)) & (y < np.percentile(y, 60))),
            "luci": colore_zona(img, y > np.percentile(y, 85)),
        },
        "saturazione": {"media": round(float(s.mean()), 3), "p90": round(float(np.percentile(s, 90)), 3)},
        "tinte_presenti": tinte,
        "vignetta_angoli_su_centro": round(float(angoli / max(centro, 1e-6)), 3),
        "grana_rumore_zone_piatte": round(float(alta[piatte].std()), 4),
        "nitidezza_dettaglio": round(float(np.abs(alta).mean()), 4),
    }


def riassunto(m):
    l = m["luminosita"]
    righe = [f"  formato {m['formato']} (utile {m['formato_utile_senza_bande']}), bande {m['bande_nere_px']}",
             f"  nero {l['nero_0.5%']}  mediana {l['mediana']}  bianco {l['bianco_99.5%']}  contrasto {l['contrasto_p75-p25']}"
             f"  bruciati {l['pixel_bruciati_%']}%",
             f"  saturazione media {m['saturazione']['media']}  vignetta {m['vignetta_angoli_su_centro']}"
             f"  grana {m['grana_rumore_zone_piatte']}"]
    for z, c in m["colore_zone"].items():
        if c:
            righe.append(f"  {z:6s} -> {c['verso']} ({c['tinta_gradi']}°), intensità {c['intensita']}")
    return "\n".join(righe)


def curva_da_coppia(prima, dopo, n=256):
    """Per ogni canale: valore medio 'dopo' per ogni valore 'prima' (curva monotona, 256 punti)."""
    tab = {}
    for i, c in enumerate("rgb"):
        x = (prima[..., i].ravel() * (n - 1)).round().astype(int)
        somma = np.bincount(x, dopo[..., i].ravel(), minlength=n)
        cont = np.bincount(x, minlength=n)
        ok = cont > 20
        xs = np.arange(n)
        ys = np.interp(xs, xs[ok], somma[ok] / cont[ok]) if ok.sum() > 2 else xs / (n - 1)
        ys = np.convolve(np.pad(ys, 4, mode="edge"), np.ones(9) / 9, mode="valid")
        ys = np.maximum.accumulate(ys)
        tab[c] = [round(float(v), 4) for v in ys]
    return tab


def allinea(prima, dopo):
    """Se il 'dopo' è ritagliato o ridimensionato, porta il 'prima' alle stesse dimensioni (centro)."""
    hp, wp = prima.shape[:2]
    hd, wd = dopo.shape[:2]
    fp, fd = wp / hp, wd / hd
    if abs(fp - fd) > 0.01:
        if fp > fd:
            nw = int(hp * fd); x0 = (wp - nw) // 2; prima = prima[:, x0:x0 + nw]
        else:
            nh = int(wp / fd); y0 = (hp - nh) // 2; prima = prima[y0:y0 + nh]
    im = Image.fromarray((prima * 255).astype(np.uint8)).resize((wd, hd), Image.LANCZOS)
    return np.asarray(im, np.float32) / 255


def confronta(prima, dopo):
    prima = allinea(prima, dopo)
    a, b = riduci(prima), riduci(dopo)
    ma, mb = misura(prima), misura(dopo)
    ya, yb = C.luma(a), C.luma(b)
    ha, sa, _ = C.rgb_a_hsv(a)
    _, sb, _ = C.rgb_a_hsv(b)
    per_fascia = {}
    for nome, centro in C.FASCE.items():
        w = C.peso_fascia(ha, centro) * (sa > 0.12)
        if w.sum() > 0.005 * w.size:
            per_fascia[nome] = round(float((sb * w).sum() / max((sa * w).sum(), 1e-6)) - 1, 3)
    return {
        "prima": ma, "dopo": mb,
        "variazioni": {
            "esposizione_stop": round(float(np.log2(max(np.median(C.a_lineare(yb)), 1e-4) / max(np.median(C.a_lineare(ya)), 1e-4))), 2),
            "nero": round(mb["luminosita"]["nero_0.5%"] - ma["luminosita"]["nero_0.5%"], 3),
            "bianco": round(mb["luminosita"]["bianco_99.5%"] - ma["luminosita"]["bianco_99.5%"], 3),
            "contrasto": round(mb["luminosita"]["contrasto_p75-p25"] - ma["luminosita"]["contrasto_p75-p25"], 3),
            "saturazione_x": round(mb["saturazione"]["media"] / max(ma["saturazione"]["media"], 1e-6), 3),
            "saturazione_per_fascia": per_fascia,
            "vignetta": round(mb["vignetta_angoli_su_centro"] - ma["vignetta_angoli_su_centro"], 3),
            "grana": round(mb["grana_rumore_zone_piatte"] - ma["grana_rumore_zone_piatte"], 4),
        },
        "curve_apprese": curva_da_coppia(a, b),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("modo", choices=["esempi", "coppia", "coppie"])
    ap.add_argument("a")
    ap.add_argument("b", nargs="?")
    ap.add_argument("--json", help="salva tutti i numeri in questo file")
    ap.add_argument("--scrivi-curve", help="look.json in cui salvare le curve medie apprese dalle coppie")
    x = ap.parse_args()
    risultato = {}
    if x.modo == "esempi":
        for f in C.elenca(x.a):
            m = misura(C.carica(f))
            risultato[f.name] = m
            print(f"\n{f.name}\n{riassunto(m)}")
    else:
        if x.modo == "coppia":
            coppie = [(Path(x.a), Path(x.b))]
        else:
            dopo = {f.stem: f for f in C.elenca(x.b)}
            coppie = [(f, dopo[f.stem]) for f in C.elenca(x.a) if f.stem in dopo]
            if not coppie:
                raise SystemExit("Nessuna coppia: i file prima/dopo devono avere lo stesso nome.")
        tutte = []
        for pa, pb in coppie:
            r = confronta(C.carica(pa), C.carica(pb))
            risultato[pa.name] = r
            tutte.append(r["curve_apprese"])
            print(f"\n{pa.name}  ->  {pb.name}")
            print(" prima:\n" + riassunto(r["prima"]))
            print(" dopo:\n" + riassunto(r["dopo"]))
            print(" variazioni: " + json.dumps(r["variazioni"], ensure_ascii=False))
        if x.scrivi_curve:
            media = {c: [round(float(v), 4) for v in np.mean([t[c] for t in tutte], 0)] for c in "rgb"}
            p = Path(x.scrivi_curve)
            look = json.loads(p.read_text()) if p.exists() else {}
            look.setdefault("curve", {})["tabelle"] = media
            p.write_text(json.dumps(look, indent=2, ensure_ascii=False))
            print(f"\nCurve medie salvate in {p}")
    if x.json:
        Path(x.json).write_text(json.dumps(risultato, indent=1, ensure_ascii=False))


if __name__ == "__main__":
    main()
