#!/usr/bin/env python3
"""Applica il look di /editing a una foto o a una cartella di foto.

Uso:
  python3 applica.py <foto-o-cartella> <cartella-uscita> [--look ../look.json] [--confronto]

Scrive le foto modificate in <cartella-uscita> e, con --confronto, anche
<nome>_prima-dopo.jpg (originale a sinistra, risultato a destra).
Ogni voce di look.json ha un valore "neutro" che non cambia nulla:
si può togliere o mettere a zero quello che non serve.
"""
import argparse
import json
from pathlib import Path
import numpy as np
import comune as C

QUI = Path(__file__).resolve().parent


def ritaglia(img, formato, centro_y=0.5):
    if not formato:
        return img
    h, w = img.shape[:2]
    if w / h > formato:          # troppo larga: taglio ai lati
        nw = int(round(h * formato))
        x0 = (w - nw) // 2
        return img[:, x0:x0 + nw]
    nh = int(round(w / formato))  # troppo alta: taglio sopra e sotto
    y0 = int(np.clip(round((h - nh) * centro_y), 0, h - nh))
    return img[y0:y0 + nh]


def bilanciamento(img, temperatura, tinta):
    # temperatura: + caldo / - freddo; tinta: + magenta / - verde (circa -100..100)
    t, g = temperatura / 100.0, tinta / 100.0
    guadagni = np.array([1 + 0.20 * t, 1 - 0.12 * g, 1 - 0.20 * t], dtype=np.float32)
    lin = C.a_lineare(img) * guadagni
    return C.da_lineare(lin)


def toni_divisi(img, cfg):
    """Colora ombre, toni medi e luci separatamente (color wheels / split toning)."""
    y = C.luma(img)[..., None]
    pesi = {
        "ombre": np.clip(1 - y / 0.45, 0, 1) ** 1.5,
        "medi": np.clip(1 - np.abs(y - 0.5) / 0.35, 0, 1),
        "luci": np.clip((y - 0.55) / 0.45, 0, 1) ** 1.2,
    }
    out = img.copy()
    for zona, p in pesi.items():
        z = cfg.get(zona)
        if not z or not z.get("forza"):
            continue
        tono = C.hsv_a_rgb(np.array(z["tinta_gradi"], np.float32), np.array(1.0, np.float32), np.array(1.0, np.float32))
        spinta = (tono - tono.mean()) * z["forza"]  # sposta il colore senza cambiare la luminosità media
        out = out + p * spinta
    return np.clip(out, 0, 1)


def hsl(img, cfg, sat_globale, vividezza):
    h, s, v = C.rgb_a_hsv(img)
    fattore_s = np.full_like(s, sat_globale)
    fattore_v = np.ones_like(v)
    sposta_h = np.zeros_like(h)
    for nome, centro in C.FASCE.items():
        f = cfg.get(nome)
        if not f:
            continue
        w = C.peso_fascia(h, centro) * np.clip(s * 4, 0, 1)
        fattore_s *= 1 + w * f.get("saturazione", 0)
        fattore_v *= 1 + w * f.get("luminosita", 0)
        sposta_h += w * f.get("tinta", 0)
    if vividezza:
        fattore_s *= 1 + vividezza * (1 - s) ** 2   # spinge di più i colori spenti
    s2 = np.clip(s * fattore_s, 0, 1)
    v2 = np.clip(v * fattore_v, 0, 1)
    return C.hsv_a_rgb(h + sposta_h, s2, v2)


def curve(img, cfg):
    out = img
    if cfg.get("tabelle"):  # curve apprese dalle coppie prima/dopo (256 valori per canale)
        t = cfg["tabelle"]
        out = np.stack([C.applica_tabella(out[..., i], np.array(t[c], np.float32))
                        for i, c in enumerate("rgb")], -1)
    if cfg.get("generale"):
        tab = C.curva_morbida(cfg["generale"])
        out = C.applica_tabella(out, tab)
    for i, c in enumerate("rgb"):
        if cfg.get(c):
            out[..., i] = C.applica_tabella(out[..., i], C.curva_morbida(cfg[c]))
    return out


def comprimi_luci(img, inizio):
    """Le luci arrivano al bianco piano, come in pellicola, invece di bruciarsi di colpo."""
    if inizio >= 1:
        return img
    k = 1 - inizio
    sopra = img > inizio
    out = img.copy()
    out[sopra] = inizio + k * (1 - np.exp(-(img[sopra] - inizio) / k))
    return out


def alone(img, cfg, diag):
    """Halation (alone rosso attorno alle luci forti) e bloom (bagliore morbido)."""
    out = img
    lin = C.a_lineare(img)
    y = C.luma(lin)
    hcfg = cfg.get("halation", {})
    if hcfg.get("forza"):
        maschera = np.clip((y - hcfg.get("soglia", 0.8)) / 0.2, 0, 1)
        blur = C.sfoca(maschera, diag * hcfg.get("raggio", 0.006))
        colore = np.array(hcfg.get("colore", [1.0, 0.35, 0.15]), np.float32)
        lin = lin + blur[..., None] * colore * hcfg["forza"]
    bcfg = cfg.get("bloom", {})
    if bcfg.get("forza"):
        luci = lin * np.clip((y - bcfg.get("soglia", 0.7)) / 0.3, 0, 1)[..., None]
        blur = np.stack([C.sfoca(luci[..., i], diag * bcfg.get("raggio", 0.02)) for i in range(3)], -1)
        lin = lin + blur * bcfg["forza"]
    if hcfg.get("forza") or bcfg.get("forza"):
        out = C.da_lineare(lin)
    return np.clip(out, 0, 1)


def vignetta(img, cfg):
    f = cfg.get("forza", 0)
    if not f:
        return img
    h, w = img.shape[:2]
    yy, xx = np.mgrid[0:h, 0:w].astype(np.float32)
    dx = (xx / (w - 1) - 0.5) * 2
    dy = (yy / (h - 1) - 0.5) * 2 * (h / w) ** cfg.get("rotondita", 0.5)
    r = np.sqrt(dx * dx + dy * dy) / np.sqrt(2)
    inizio, morb = cfg.get("inizio", 0.35), cfg.get("morbidezza", 0.6)
    m = np.clip((r - inizio) / morb, 0, 1) ** 2
    return img * (1 - f * m)[..., None]


def grana(img, cfg, seme):
    f = cfg.get("forza", 0)
    if not f:
        return img
    rng = np.random.default_rng(seme)
    h, w = img.shape[:2]
    rumore = rng.standard_normal((h, w)).astype(np.float32)
    rumore = C.sfoca(rumore, cfg.get("dimensione", 0.8))
    rumore /= rumore.std() + 1e-6
    y = C.luma(img)
    peso = 4 * y * (1 - y)          # più visibile nei toni medi, come la pellicola
    out = img + (rumore * peso * f)[..., None]
    if cfg.get("colore", 0):
        rc = C.sfoca(rng.standard_normal((h, w, 3)).astype(np.float32), cfg.get("dimensione", 0.8) * 1.5)
        rc /= rc.std() + 1e-6
        out = out + rc * (peso * f * cfg["colore"])[..., None]
    return np.clip(out, 0, 1)


def bande(img, formato):
    """Bande nere per arrivare al formato (letterbox) senza tagliare la foto."""
    if not formato:
        return img
    h, w = img.shape[:2]
    if w / h >= formato:
        return img
    nh = int(round(w / formato))
    b = (h - nh) // 2
    out = img.copy()
    out[:b] = 0
    out[b + nh:] = 0
    return out


def _trasforma(img, fn):
    """Applica una trasformazione di PIL a ogni canale in virgola mobile (niente perdita a 8 bit)."""
    from PIL import Image
    return np.stack([np.asarray(fn(Image.fromarray(img[..., i].astype(np.float32), "F")), np.float32)
                     for i in range(img.shape[2])], -1)


def raddrizza(img, gradi):
    """Ruota (positivo = antiorario) e taglia via gli angoli vuoti, tenendo le proporzioni."""
    if not gradi:
        return img
    from PIL import Image
    h, w = img.shape[:2]
    out = _trasforma(img, lambda c: c.rotate(gradi, resample=Image.BICUBIC, expand=False))
    a = np.radians(abs(gradi))
    s = min(w / (w * np.cos(a) + h * np.sin(a)), h / (w * np.sin(a) + h * np.cos(a)))
    cw, ch = int(w * s), int(h * s)
    x0, y0 = (w - cw) // 2, (h - ch) // 2
    return np.clip(out[y0:y0 + ch, x0:x0 + cw], 0, 1)


def prospettiva(img, k):
    """Verticali dritte. k > 0: pareti che convergono verso l'alto (telefono inclinato in su,
    il caso tipico dello 0,5x); k < 0: pareti che si aprono verso l'alto. Valori tipici 0,03-0,15.
    Allarga il lato stretto senza inventare nulla, poi toglie le fasce laterali rimaste vuote."""
    if not k:
        return img
    from PIL import Image
    h, w = img.shape[:2]
    d = abs(k) * w / 2
    if k > 0:   # in alto la stanza è più stretta: si campiona una fascia alta più stretta
        quad = (d, 0, 0, h, w, h, w - d, 0)
    else:
        quad = (0, 0, d, h, w - d, h, w, 0)
    out = _trasforma(img, lambda c: c.transform((w, h), Image.QUAD, quad, resample=Image.BICUBIC))
    m = int(round(d * 0.15))
    return np.clip(out[:, m:w - m] if m else out, 0, 1)


def area(img, box):
    """Tiene solo la zona [x0, y0, x1, y1] (frazioni 0..1 di larghezza e altezza)."""
    if not box:
        return img
    h, w = img.shape[:2]
    x0, y0, x1, y1 = box
    return img[int(round(y0 * h)):int(round(y1 * h)), int(round(x0 * w)):int(round(x1 * w))]


def applica(img, look, seme=0):
    g = look.get("geometria", {})
    img = raddrizza(img, g.get("rotazione", 0))
    img = prospettiva(img, g.get("prospettiva", 0))
    img = area(img, look.get("ritaglio", {}).get("area"))
    img = ritaglia(img, look.get("ritaglio", {}).get("formato"), look.get("ritaglio", {}).get("centro_verticale", 0.5))
    diag = float(np.hypot(*img.shape[:2]))
    b = look.get("base", {})
    if b.get("esposizione"):
        img = C.da_lineare(C.a_lineare(img) * 2 ** b["esposizione"])
    if b.get("temperatura") or b.get("tinta"):
        img = bilanciamento(img, b.get("temperatura", 0), b.get("tinta", 0))
    img = curve(img, look.get("curve", {}))
    img = toni_divisi(img, look.get("toni", {}))
    img = hsl(img, look.get("colori", {}), b.get("saturazione", 1.0), b.get("vividezza", 0))
    img = comprimi_luci(img, b.get("compressione_luci_da", 1.0))
    img = alone(img, look.get("luce", {}), diag)
    img = vignetta(img, look.get("vignetta", {}))
    img = grana(img, look.get("grana", {}), seme)
    img = bande(img, look.get("bande", {}).get("formato"))
    return np.clip(img, 0, 1)


def confronto(prima, dopo):
    h = dopo.shape[0]
    # porta l'originale all'altezza del risultato (ritaglio compreso)
    from PIL import Image
    p = Image.fromarray((np.clip(prima, 0, 1) * 255).astype(np.uint8))
    p = p.resize((int(round(p.width * h / p.height)), h), Image.LANCZOS)
    sep = np.ones((h, max(4, h // 150), 3), np.float32)
    return np.concatenate([np.asarray(p, np.float32) / 255, sep, dopo], 1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ingresso")
    ap.add_argument("uscita")
    ap.add_argument("--look", default=str(QUI.parent / "look.json"))
    ap.add_argument("--confronto", action="store_true")
    ap.add_argument("--ruota", type=float, default=None,
                    help="gradi per raddrizzare (positivo = antiorario); sostituisce geometria.rotazione")
    ap.add_argument("--prospettiva", type=float, default=None,
                    help="correzione delle verticali (+ convergono in alto, - si aprono); sostituisce geometria.prospettiva")
    a = ap.parse_args()
    look = json.loads(Path(a.look).read_text())
    if a.ruota is not None or a.prospettiva is not None:
        g = look.setdefault("geometria", {})
        if a.ruota is not None:
            g["rotazione"] = a.ruota
        if a.prospettiva is not None:
            g["prospettiva"] = a.prospettiva
    for i, f in enumerate(C.elenca(a.ingresso)):
        img = C.carica(f)
        out = applica(img, look, seme=i)
        dest = Path(a.uscita) / (f.stem + "_editing.jpg")
        C.salva(out, dest)
        if a.confronto:
            C.salva(confronto(img, out), Path(a.uscita) / (f.stem + "_prima-dopo.jpg"), qualita=88)
        print(f"{f.name} -> {dest}")


if __name__ == "__main__":
    main()
