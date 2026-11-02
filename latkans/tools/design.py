"""Shared type + drawing helpers, copied from the BhogKart Satvik Panjiri build so Atreya slides share its look."""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

F_HEAD = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'PlayfairDisplay[wght].ttf')
F_BODY = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'fonts', 'EBGaramond[wght].ttf')

INK = (14, 42, 46)          # deep teal, from the pouch title ink
GOLD = (150, 106, 44)       # antique gold for hairlines and ornaments on ivory
GOLD_TEXT = (96, 62, 18)   # deeper bronze for gold TEXT on ivory (>= 4.5:1)
GOLD_LIGHT = (232, 196, 128)  # gold on dark grounds
IVORY = (247, 240, 229)
BODY = (44, 40, 36)
NIGHT = (16, 11, 7)

_cache = {}
def font(path, size, wght):
    k = (path, int(size), int(wght))
    if k not in _cache:
        f = ImageFont.truetype(path, int(size)); f.set_variation_by_axes([wght]); _cache[k] = f
    return _cache[k]

def tw(f, s, tracking=0):
    return sum(f.getlength(c) for c in s) + tracking * max(0, len(s) - 1) if tracking else f.getlength(s)

RECORD = []   # (box, fill, text) of every line drawn, for contrast checks against the pre-text background

def text(d, x, y, s, f, fill, tracking=0, anchor='ls'):
    """baseline-anchored text with optional letter spacing; anchor 'ls' left or 'ms' centre or 'rs' right"""
    w = tw(f, s, tracking)
    if anchor == 'ms': x = x - w / 2
    elif anchor == 'rs': x = x - w
    RECORD.append(((x, y - f.size * 0.78, x + w, y + f.size * 0.22), fill, s))
    if not tracking:
        d.text((x, y), s, font=f, fill=fill, anchor='ls'); return w
    cx = x
    for ch in s:
        d.text((cx, y), ch, font=f, fill=fill, anchor='ls'); cx += f.getlength(ch) + tracking
    return w

def wrap(s, f, maxw):
    words = s.split(); lines = []; cur = ''
    for wd in words:
        t = (cur + ' ' + wd).strip()
        if f.getlength(t) <= maxw or not cur: cur = t
        else: lines.append(cur); cur = wd
    if cur: lines.append(cur)
    return lines

def fit_size(path, wght, lines, maxw, start, minsize=10):
    size = start
    while size > minsize and max(font(path, size, wght).getlength(l) for l in lines) > maxw:
        size -= 2
    return size

def cover(img, W, H, fx=0.5, fy=0.5):
    """scale to fill W x H, crop around focus fraction"""
    s = max(W / img.width, H / img.height)
    im = img.resize((int(round(img.width * s)), int(round(img.height * s))), Image.LANCZOS)
    x = int(round((im.width - W) * fx)); y = int(round((im.height - H) * fy))
    return im.crop((x, y, x + W, y + H))

def ease(t):
    return t * t * (3 - 2 * t)

def hscrim(img, color, x0, x1, a0, a1):
    """horizontal gradient overlay from alpha a0 at x0 to a1 at x1 (holds a0 left of x0, a1 right of x1)"""
    W, H = img.size
    xs = np.arange(W, dtype=float)
    t = np.clip((xs - x0) / max(1, (x1 - x0)), 0, 1)
    a = a0 + (a1 - a0) * ease(t)
    A = np.asarray(img).astype(float)
    C = np.array(color, float)[None, None, :]
    out = A * (1 - a[None, :, None]) + C * a[None, :, None]
    return Image.fromarray(np.clip(out, 0, 255).round().astype('uint8'))

def vscrim(img, color, y0, y1, a0, a1):
    W, H = img.size
    ys = np.arange(H, dtype=float)
    t = np.clip((ys - y0) / max(1, (y1 - y0)), 0, 1)
    a = a0 + (a1 - a0) * ease(t)
    A = np.asarray(img).astype(float)
    C = np.array(color, float)[None, None, :]
    out = A * (1 - a[:, None, None]) + C * a[:, None, None]
    return Image.fromarray(np.clip(out, 0, 255).round().astype('uint8'))

def divider(d, x, y, w, color, align='left', lw=2, gem=7):
    """a gold hairline with a small diamond, echoing the pouch's filigree"""
    if align == 'center':
        x = x - w / 2
    d.line([(x, y), (x + w, y)], fill=color, width=lw)
    cx = x + (w / 2 if align == 'center' else w * 0.18)
    d.polygon([(cx, y - gem), (cx + gem, y), (cx, y + gem), (cx - gem, y)], fill=color)

def diamond(d, cx, cy, r, color):
    d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=color)

def frame(d, W, H, inset, color, lw=2):
    d.rectangle([inset, inset, W - 1 - inset, H - 1 - inset], outline=color, width=lw)

def lum(rgb):
    def ch(c):
        c = c / 255; return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    r, g, b = rgb; return 0.2126 * ch(r) + 0.7152 * ch(g) + 0.0722 * ch(b)

def worst_contrast(img, box, text_rgb, step=24):
    """WCAG contrast of the text colour against the worst (closest) strip of the background box"""
    x0, y0, x1, y1 = [int(v) for v in box]
    A = np.asarray(img.convert('RGB')).astype(float)
    Lt = lum(text_rgb); worst = 99
    for y in range(y0, y1, step):
        strip = A[y:min(y + step, y1), x0:x1].reshape(-1, 3)
        if not len(strip): continue
        # use the 90th percentile pixel in the direction that hurts contrast
        Ls = np.array([lum(p) for p in strip[::max(1, len(strip) // 400)]])
        # worst case: for dark text the DARKEST background, for light text the BRIGHTEST
        Lb = np.percentile(Ls, 5) if Lt < 0.5 else np.percentile(Ls, 95)
        hi, lo = max(Lt, Lb), min(Lt, Lb)
        worst = min(worst, (hi + 0.05) / (lo + 0.05))
    return round(worst, 2)


def audit(bg, label):
    """WCAG contrast of every recorded line against the background it sits on (worst 5% of pixels)."""
    worst = []
    for box, fill, s in RECORD:
        c = worst_contrast(bg, box, fill, step=10)
        worst.append((c, s))
    worst.sort()
    RECORD.clear()
    bad = [(c, s) for c, s in worst if c < 4.5]
    print(f'  {label}: min contrast {worst[0][0] if worst else None} on "{worst[0][1] if worst else ""}"' + (f'  FAIL<4.5: {bad}' if bad else '  all >= 4.5'))
    return worst
