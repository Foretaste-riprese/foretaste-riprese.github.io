#!/usr/bin/env python3
"""Clean up a property / listing photo: level, straighten, fix verticals, colour, exposure, crop, export.

Only Pillow and NumPy are needed. Every correction is optional and has a strength, so the
photo can be adjusted step by step after looking at the preview.

Example:
  python3 edit_photo.py in.jpg out.jpg --rotate -1.2 --keystone 0.04 --wb 0.8 \
      --exposure auto --crop 0.06,0,1,1 --aspect 3:2 --max-side 2400 --preview preview.jpg
"""
import argparse
import sys

import numpy as np
from PIL import Image, ImageCms, ImageOps


def parse_args():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("src")
    p.add_argument("dst")
    p.add_argument("--rotate", type=float, default=0.0,
                   help="degrees, positive = counter-clockwise; the borders are cropped away")
    p.add_argument("--keystone", type=float, default=0.0,
                   help="vertical perspective fix, about -0.15..0.15. Positive when walls lean "
                        "inward towards the top (camera tilted up), negative when they lean outward")
    p.add_argument("--wb", type=float, default=0.0,
                   help="white-balance strength 0..1 (grey world, removes colour casts)")
    p.add_argument("--warmth", type=float, default=0.0,
                   help="after white balance: + warmer, - cooler, about -0.1..0.1")
    p.add_argument("--exposure", default="none",
                   help="'auto' (levels from percentiles) or a number of stops, e.g. 0.3 / -0.2")
    p.add_argument("--shadows", type=float, default=0.0, help="lift shadows 0..1")
    p.add_argument("--highlights", type=float, default=0.0, help="recover highlights 0..1")
    p.add_argument("--saturation", type=float, default=1.0, help="1 = unchanged")
    p.add_argument("--crop", default=None,
                   help="left,top,right,bottom as fractions of the image (e.g. 0.05,0,1,0.95)")
    p.add_argument("--aspect", default=None, help="final centred crop to a ratio, e.g. 3:2, 4:5, 16:9")
    p.add_argument("--max-side", type=int, default=0, help="resize so the long side is at most N px")
    p.add_argument("--quality", type=int, default=90)
    p.add_argument("--preview", default=None, help="write a before/after image here")
    return p.parse_args()


def to_float(img):
    return np.asarray(img.convert("RGB"), dtype=np.float32) / 255.0


def to_img(a):
    return Image.fromarray((np.clip(a, 0, 1) * 255 + 0.5).astype(np.uint8))


def rotate_and_crop(img, deg):
    """Rotate, then keep the largest axis-aligned rectangle with no empty corners."""
    if abs(deg) < 1e-3:
        return img
    w, h = img.size
    r = img.rotate(deg, resample=Image.BICUBIC, expand=False)
    a = np.radians(abs(deg))
    # largest rectangle of the same aspect that fits inside the rotated frame
    cos, sin = np.cos(a), np.sin(a)
    scale = min(w / (w * cos + h * sin), h / (w * sin + h * cos))
    cw, ch = int(w * scale), int(h * scale)
    left, top = (w - cw) // 2, (h - ch) // 2
    return r.crop((left, top, left + cw, top + ch))


def keystone(img, k):
    """Correct converging verticals by widening the top (k>0) or the bottom (k<0)."""
    if abs(k) < 1e-4:
        return img
    w, h = img.size
    d = abs(k) * w / 2
    if k > 0:   # verticals lean inward at the top: sample a narrower top band
        quad = (d, 0, 0, h, w, h, w - d, 0)
    else:       # verticals lean outward at the top: sample a narrower bottom band
        quad = (0, 0, d, h, w - d, h, w, 0)
    out = img.transform((w, h), Image.QUAD, quad, resample=Image.BICUBIC)
    # stretching adds a little height distortion; crop the edges that went soft
    m = int(d * 0.15)
    return out.crop((m, 0, w - m, h)) if m else out


def white_balance(a, strength, warmth):
    if strength > 0:
        lum = a.mean(-1, keepdims=True)
        mask = (lum > 0.08) & (lum < 0.92)                 # ignore clipped areas
        sel = a[mask[..., 0]]
        if len(sel) > 1000:
            means = sel.mean(0)
            gain = means.mean() / np.maximum(means, 1e-4)
            gain = np.clip(gain, 0.8, 1.25)                # a room can be genuinely warm: never over-correct
            gain = 1 + (gain - 1) * strength
            a = a * gain
    if warmth:
        a = a * np.array([1 + warmth, 1 + warmth * 0.3, 1 - warmth], np.float32)
    return a


def exposure(a, mode, shadows, highlights):
    if mode == "auto":
        lum = (a * [0.2126, 0.7152, 0.0722]).sum(-1)
        lo, hi = np.percentile(lum, 0.5), np.percentile(lum, 99.6)
        lo, hi = min(lo, 0.06), max(hi, 0.85)               # never crush or clip hard
        a = (a - lo) / max(hi - lo, 1e-3)
        mid = np.median(np.clip((lum - lo) / max(hi - lo, 1e-3), 0, 1))
        if 0.05 < mid < 0.95:                                # pull the midtones towards 0.45
            g = np.log(0.45) / np.log(mid)
            g = float(np.clip(g, 0.7, 1.4))
            a = np.clip(a, 0, None) ** g
    elif mode not in ("none", "", None):
        a = a * (2 ** float(mode))
    if shadows or highlights:
        lum = np.clip((a * [0.2126, 0.7152, 0.0722]).sum(-1, keepdims=True), 0, 1)
        a = a + shadows * 0.25 * (1 - lum) ** 3              # lift only the dark end
        a = a - highlights * 0.25 * lum ** 4 * np.clip(a, 0, None)
    return a


def saturate(a, s):
    if abs(s - 1) < 1e-3:
        return a
    lum = (a * [0.2126, 0.7152, 0.0722]).sum(-1, keepdims=True)
    return lum + (a - lum) * s


def crop_frac(img, spec):
    if not spec:
        return img
    l, t, r, b = (float(x) for x in spec.split(","))
    w, h = img.size
    return img.crop((int(l * w), int(t * h), int(r * w), int(b * h)))


def crop_aspect(img, spec):
    if not spec:
        return img
    aw, ah = (float(x) for x in spec.split(":"))
    w, h = img.size
    target = aw / ah
    if w / h > target:
        nw = int(h * target)
        return img.crop(((w - nw) // 2, 0, (w - nw) // 2 + nw, h))
    nh = int(w / target)
    return img.crop((0, (h - nh) // 2, w, (h - nh) // 2 + nh))


def main():
    args = parse_args()
    try:
        src = Image.open(args.src)
    except Exception as exc:  # noqa: BLE001 - report any unreadable input plainly
        sys.exit(f"Impossibile aprire {args.src}: {exc}")
    src = ImageOps.exif_transpose(src).convert("RGB")
    img = rotate_and_crop(src, args.rotate)
    img = keystone(img, args.keystone)
    a = to_float(img)
    a = white_balance(a, args.wb, args.warmth)
    a = exposure(a, args.exposure, args.shadows, args.highlights)
    a = saturate(a, args.saturation)
    img = to_img(a)
    img = crop_frac(img, args.crop)
    img = crop_aspect(img, args.aspect)
    if args.max_side and max(img.size) > args.max_side:
        img.thumbnail((args.max_side, args.max_side), Image.LANCZOS)
    icc = ImageCms.ImageCmsProfile(ImageCms.createProfile("sRGB")).tobytes()
    img.save(args.dst, quality=args.quality, icc_profile=icc, optimize=True)

    if args.preview:
        h = 700
        before = src.copy(); before.thumbnail((10_000, h), Image.LANCZOS)
        after = img.copy(); after.thumbnail((10_000, h), Image.LANCZOS)
        sheet = Image.new("RGB", (before.width + after.width + 30, h + 20), (25, 25, 25))
        sheet.paste(before, (10, 10)); sheet.paste(after, (before.width + 20, 10))
        sheet.save(args.preview, quality=85)
    print(f"Salvata {args.dst} ({img.width}x{img.height})")


if __name__ == "__main__":
    main()
