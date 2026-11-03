"""Funzioni condivise da analizza.py e applica.py (solo Pillow + numpy)."""
from pathlib import Path
import numpy as np
from PIL import Image, ImageOps

ESTENSIONI = {".jpg", ".jpeg", ".png", ".webp", ".tif", ".tiff", ".heic"}


def carica(percorso):
    """Apre un'immagine, la raddrizza secondo l'EXIF e la restituisce float32 0..1 (H, W, 3)."""
    im = Image.open(percorso)
    im = ImageOps.exif_transpose(im).convert("RGB")
    return np.asarray(im, dtype=np.float32) / 255.0


def salva(arr, percorso, qualita=95):
    arr = np.clip(arr, 0, 1)
    im = Image.fromarray((arr * 255 + 0.5).astype(np.uint8))
    p = Path(percorso)
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.suffix.lower() in (".jpg", ".jpeg"):
        im.save(p, quality=qualita, subsampling=0)
    else:
        im.save(p)


def elenca(cartella_o_file):
    p = Path(cartella_o_file)
    if p.is_file():
        return [p]
    return sorted(f for f in p.iterdir() if f.suffix.lower() in ESTENSIONI)


# --- spazi colore -----------------------------------------------------------

def a_lineare(x):
    return np.where(x <= 0.04045, x / 12.92, ((x + 0.055) / 1.055) ** 2.4)


def da_lineare(x):
    x = np.clip(x, 0, None)
    return np.where(x <= 0.0031308, x * 12.92, 1.055 * np.power(x, 1 / 2.4) - 0.055)


def luma(rgb):
    return rgb[..., 0] * 0.2126 + rgb[..., 1] * 0.7152 + rgb[..., 2] * 0.0722


def rgb_a_hsv(rgb):
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    mx = rgb.max(-1)
    mn = rgb.min(-1)
    d = mx - mn
    h = np.zeros_like(mx)
    m = d > 1e-6
    rr = m & (mx == r)
    gg = m & (mx == g) & ~rr
    bb = m & ~rr & ~gg
    h[rr] = ((g - b)[rr] / d[rr]) % 6
    h[gg] = (b - r)[gg] / d[gg] + 2
    h[bb] = (r - g)[bb] / d[bb] + 4
    h = h * 60.0
    s = np.where(mx > 1e-6, d / np.maximum(mx, 1e-6), 0)
    return h, s, mx


def hsv_a_rgb(h, s, v):
    h = (h % 360) / 60.0
    i = np.floor(h).astype(int) % 6
    f = h - np.floor(h)
    p = v * (1 - s)
    q = v * (1 - s * f)
    t = v * (1 - s * (1 - f))
    scelte = [
        np.stack([v, t, p], -1), np.stack([q, v, p], -1), np.stack([p, v, t], -1),
        np.stack([p, q, v], -1), np.stack([t, p, v], -1), np.stack([v, p, q], -1),
    ]
    out = np.zeros(h.shape + (3,), dtype=np.float32)
    for k in range(6):
        out[i == k] = scelte[k][i == k]
    return out


# Sei fasce di colore, centro in gradi (come il pannello HSL di Lightroom, semplificato)
FASCE = {"rossi": 0, "arancioni": 30, "gialli": 60, "verdi": 120, "azzurri": 195, "blu": 230, "viola": 280}


def peso_fascia(h, centro, larghezza=40.0):
    d = np.abs(((h - centro + 180) % 360) - 180)
    return np.clip(1 - d / larghezza, 0, 1)


# --- sfocatura (senza scipy) ------------------------------------------------

def _box(a, r, asse):
    if r < 1:
        return a
    pad = [(0, 0)] * a.ndim
    pad[asse] = (r + 1, r)
    c = np.cumsum(np.pad(a, pad, mode="edge"), axis=asse, dtype=np.float64)
    n = a.shape[asse]
    alto = np.take(c, np.arange(2 * r + 1, 2 * r + 1 + n), axis=asse)
    basso = np.take(c, np.arange(0, n), axis=asse)
    return ((alto - basso) / (2 * r + 1)).astype(np.float32)


def sfoca(a, sigma):
    """Gaussiana approssimata con 3 passate di media mobile."""
    if sigma <= 0.3:
        return a
    r = max(1, int(round(np.sqrt(12 * sigma * sigma / 3 + 1) / 2 - 0.5)))
    for _ in range(3):
        a = _box(_box(a, r, 0), r, 1)
    return a


# --- curve --------------------------------------------------------------------

def curva_morbida(punti, n=1024):
    """Curva monotona passante per i punti [[x, y], ...] (0..1), Fritsch-Carlson."""
    p = np.array(sorted(punti), dtype=np.float64)
    if p[0, 0] > 0:
        p = np.vstack([[0, p[0, 1]], p])
    if p[-1, 0] < 1:
        p = np.vstack([p, [1, p[-1, 1]]])
    x, y = p[:, 0], p[:, 1]
    d = np.diff(y) / np.maximum(np.diff(x), 1e-9)
    m = np.zeros_like(y)
    m[1:-1] = np.where(d[:-1] * d[1:] > 0, (d[:-1] + d[1:]) / 2, 0)
    m[0], m[-1] = d[0], d[-1]
    for k in range(len(d)):
        if d[k] == 0:
            m[k] = m[k + 1] = 0
        else:
            a, b = m[k] / d[k], m[k + 1] / d[k]
            s = a * a + b * b
            if s > 9:
                t = 3 / np.sqrt(s)
                m[k], m[k + 1] = t * a * d[k], t * b * d[k]
    xs = np.linspace(0, 1, n)
    k = np.clip(np.searchsorted(x, xs) - 1, 0, len(x) - 2)
    h = x[k + 1] - x[k]
    t = (xs - x[k]) / h
    h00 = 2 * t**3 - 3 * t**2 + 1
    h10 = t**3 - 2 * t**2 + t
    h01 = -2 * t**3 + 3 * t**2
    h11 = t**3 - t**2
    ys = h00 * y[k] + h10 * h * m[k] + h01 * y[k + 1] + h11 * h * m[k + 1]
    return np.clip(ys, 0, 1).astype(np.float32)


def applica_tabella(x, tabella):
    n = len(tabella)
    idx = np.clip(x, 0, 1) * (n - 1)
    return np.interp(idx, np.arange(n), tabella).astype(np.float32)
