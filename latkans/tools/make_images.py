"""Builds the Amazon/Flipkart gallery (other1-other8) and A+ images for the Atreya Ganesh lotus bell latkan.
Look follows BhogKart's live Amazon gallery (B0HHPHVJ42): ivory grounds, centred bronze eyebrow, bold
Playfair headline in deep teal, gold hairline-and-diamond divider, festive brass/diya/teal-silk props.

Backgrounds are Azure gpt-image-2 plates (tools/plates.py) with no product in them. Every latkan you see
is the real photo from source/, pasted on with its original pixels (tools/mattes.py), so the model never
redraws the Ganesha, lotus buds, bells, flowers or pearl tassel. main.jpg is not touched here.

python tools/make_images.py        (from latkans/)"""
import os, sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from design import *

ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "source")
S = 1600
LENGTH_TXT = ("86 cm", "34 inch")
WIDTH_TXT = ("12.7 cm", "5 inch")

def plate(n, W=S, H=S, fx=0.5, fy=0.5):
    return cover(Image.open(os.path.join(HERE, "plates", n + ".jpg")).convert("RGB"), W, H, fx, fy)

def photo(n):
    return Image.open(os.path.join(SRC, n + ".jpg")).convert("RGB")

def matte(n):
    return Image.open(os.path.join(HERE, "mattes", f"matte_{n}.png")).convert("RGBA")

def strands():
    """the two single strands of the pair photo, left and right"""
    p = matte("pair_white"); a = np.asarray(p)[:, :, 3]
    cols = (a > 40).sum(axis=0) > 3
    runs, i = [], 0
    while i < len(cols):
        if cols[i]:
            j = i
            while j < len(cols) and cols[j]: j += 1
            runs.append((i, j)); i = j
        else: i += 1
    out = []
    for x0, x1 in (r for r in runs if r[1] - r[0] > 20):
        u = p.crop((x0, 0, x1, p.height))
        out.append(u.crop(u.split()[3].point(lambda v: 255 if v > 40 else 0).getbbox()))
    assert len(out) == 2, f"expected 2 strands, found {len(out)}"
    return out

# landmarks on a single strand, as a fraction of its height (measured on the 1250 px strand)
PARTS = [
    (30 / 1250, "Braided cord loop", "Hangs on a nail, hook or adhesive hook"),
    (185 / 1250, "Yellow and pink flowers", "Soft fabric petals, top and bottom"),
    (335 / 1250, "Gold-finish bells", "5 on every strand"),
    (445 / 1250, "Lotus buds", "One above and one below Ganesha"),
    (605 / 1250, "Painted Ganesha on MDF", "The centrepiece, facing outward"),
    (1110 / 1250, "Pearl tassel", "With flower drops that sway when the door opens"),
]

def scaled(u, h=None, w=None):
    k = h / u.height if h else w / u.width
    return u.resize((max(1, round(u.width * k)), max(1, round(u.height * k))), Image.LANCZOS)

def grade(u, bright=1.0, warm=1.0):
    """match the product's light to the scene; alpha untouched"""
    rgb = ImageEnhance.Brightness(u.convert("RGB")).enhance(bright)
    r, g, b = rgb.split()
    r = r.point(lambda v: min(255, int(v * warm))); b = b.point(lambda v: int(v / warm))
    out = Image.merge("RGB", (r, g, b)).convert("RGBA"); out.putalpha(u.split()[3])
    return out

def scene(u, bright, warm, sat=0.9):
    """for photographed scenes: drop the faint studio-white fringe (alpha > 110, 1 px erode, as in the
    approved limewash lifestyle pipeline) and match the product to the dusk light"""
    al = u.split()[3].point(lambda v: 0 if v < 110 else 255).filter(ImageFilter.MinFilter(3)).filter(ImageFilter.GaussianBlur(0.8))
    rgb = ImageEnhance.Color(u.convert("RGB")).enhance(sat)
    u = Image.merge("RGBA", (*rgb.split(), al))
    return grade(u, bright, warm)

def put(canvas, u, x, y, sh=(14, 16), blur=14, alpha=70):
    """alpha-composite u at (x, y) with a soft drop shadow; returns its box"""
    c = canvas.convert("RGBA")
    s = Image.new("RGBA", u.size, (40, 25, 10, 0))
    s.putalpha(u.split()[3].point(lambda v: alpha if v > 40 else 0).filter(ImageFilter.GaussianBlur(blur)))
    c.alpha_composite(s, (int(x + sh[0]), int(y + sh[1])))
    c.alpha_composite(u, (int(x), int(y)))
    return c.convert("RGB"), (int(x), int(y), int(x + u.width), int(y + u.height))

def grain(img, sd=2.2, seed=5):
    a = np.asarray(img).astype(float)
    a += np.random.default_rng(seed).normal(0, sd, a.shape[:2])[:, :, None]
    return Image.fromarray(np.clip(a, 0, 255).astype("uint8"))

def save(img, path, label):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    img.convert("RGB").save(path, "JPEG", quality=92, optimize=True, subsampling=0)
    print("wrote", os.path.relpath(path, ROOT), img.size)

# type scale (BhogKart's 2000 px sizes x 0.8)
EYE = lambda: font(F_BODY, 36, 600)
HEAD = lambda sz=90: font(F_HEAD, sz, 700)
BODYF = lambda sz=40: font(F_BODY, sz, 500)

def header(d, y, eyebrow, lines, color=INK, eyecolor=GOLD_TEXT, divcolor=GOLD, sz=90, cx=S / 2):
    """centred eyebrow, headline lines and gold divider; returns the y under the divider"""
    if eyebrow:
        text(d, cx, y, eyebrow, EYE(), eyecolor, tracking=7, anchor="ms"); y += 30
    for ln in lines:
        y += int(sz * 1.12); text(d, cx, y, ln, HEAD(sz), color, anchor="ms")
    y += 44; divider(d, cx, y, 240, divcolor, align="center")
    return y

# ---------------- gallery ----------------
def g_lifestyle(out):
    """other1: one strand on each side of the main door frame, at true scale (86 cm vs a ~210 cm door)"""
    img = plate("door_sq")
    L, R = strands()
    h = 500                                   # door opening ~1222 px tall on this plate = ~210 cm
    for u, cx in ((L, 455), (R, 1132)):       # centres of the two frame strips, measured on the plate
        u2 = scene(scaled(u, h=h), bright=0.88, warm=1.07)
        img, _ = put(img, u2, cx - u2.width / 2, 150, sh=(12, 10), blur=8, alpha=80)
    save(grain(img, 3.0), out, "lifestyle")

def g_anatomy(out):
    img = grain(plate("ivory_stage"), 1.6)
    st = strands()[0]
    top, H = 370, 1160
    u = scaled(st, h=H)
    img, (x0, y0, x1, y1) = put(img, u, (S - u.width) / 2, top, sh=(10, 12), blur=12, alpha=55)
    BG = img.copy(); RECORD.clear(); d = ImageDraw.Draw(img)
    header(d, 110, "WHAT IS ON EVERY STRAND", ["Ganesha at the centre,", "a lotus on either side"], sz=78)
    cx = S // 2
    for i, (fy, title, sub) in enumerate(PARTS):
        yy = top + int(fy * H)
        left = i % 2 == 0
        xe = cx - int(u.width * 0.45) if left else cx + int(u.width * 0.45)
        xt = 640 if left else S - 640
        d.line((xe, yy, xt, yy), fill=GOLD, width=2)
        diamond(d, xe, yy, 8, GOLD)
        tf, sf = font(F_HEAD, 40, 700), BODYF(32)
        lines = wrap(sub, sf, 560)
        if left:
            text(d, xt - 18, yy - 14, title, tf, INK, anchor="rs")
            for k, ln in enumerate(lines): text(d, xt - 18, yy + 30 + k * 36, ln, sf, BODY, anchor="rs")
        else:
            text(d, xt + 18, yy - 14, title, tf, INK)
            for k, ln in enumerate(lines): text(d, xt + 18, yy + 30 + k * 36, ln, sf, BODY)
    audit(BG, "other2"); save(img, out, "anatomy")

def g_closeup(out):
    img = Image.new("RGB", (S, S), IVORY)
    ph = cover(photo("pack4_closeup"), S, 1060, 0.5, 0.42)
    img.paste(ph, (0, 0))
    fade = vscrim(img.crop((0, 900, S, 1060)), IVORY, 0, 160, 0.0, 1.0); img.paste(fade, (0, 900))
    img = grain(img, 1.6)
    BG = img.copy(); RECORD.clear(); d = ImageDraw.Draw(img)
    y = header(d, 1110, "THE CENTREPIECE", ["Shri Ganesh at your doorstep"], sz=86)
    body = "Painted on MDF wood and framed by lotus buds. Vighnaharta at the entrance, the way Indian homes have welcomed every festival for generations."
    for k, ln in enumerate(wrap(body, BODYF(42), 1280)):
        text(d, S / 2, y + 90 + k * 56, ln, BODYF(42), BODY, anchor="ms")
    audit(BG, "other3"); save(img, out, "closeup")

def g_size(out):
    img = grain(plate("ivory_stage"), 1.6)
    st = strands()[0]
    top, H = 350, 1060
    u = scaled(st, h=H)
    sx = 560 - u.width / 2
    img, (x0, y0, x1, y1) = put(img, u, sx, top, sh=(10, 12), blur=12, alpha=55)
    BG = img.copy(); RECORD.clear(); d = ImageDraw.Draw(img)
    header(d, 110, "SIZE OF ONE STRAND", ["Long enough for a door frame,", "light enough for one nail"], sz=74)
    ax = x1 + 70
    d.line((ax, y0, ax, y1), fill=GOLD, width=3)
    for yy in (y0, y1): d.line((ax - 22, yy, ax + 22, yy), fill=GOLD, width=3)
    # width marker under the widest flowers
    wy = y1 + 34
    d.line((x0, wy, x1, wy), fill=GOLD, width=3)
    for xx in (x0, x1): d.line((xx, wy - 16, xx, wy + 16), fill=GOLD, width=3)
    tx = ax + 70; mid = (y0 + y1) / 2
    text(d, tx, mid - 230, "LENGTH", EYE(), GOLD_TEXT, tracking=7)
    text(d, tx, mid - 130, LENGTH_TXT[0], font(F_HEAD, 104, 700), INK)
    text(d, tx, mid - 70, f"{LENGTH_TXT[1]}, loop to tassel", BODYF(38), BODY)
    divider(d, tx, mid + 10, 200, GOLD)
    text(d, tx, mid + 110, "WIDTH", EYE(), GOLD_TEXT, tracking=7)
    text(d, tx, mid + 210, WIDTH_TXT[0], font(F_HEAD, 104, 700), INK)
    text(d, tx, mid + 270, f"{WIDTH_TXT[1]}, at the widest flowers", BODYF(38), BODY)
    audit(BG, "other4"); save(img, out, "size")

def g_inbox(out, n):
    img = grain(plate("ivory_stage"), 1.6)
    head = ["2 latkans, one for each", "side of the door"] if n == 2 else ["4 latkans for the main door", "and the mandir, both sides"]
    if n == 2:
        u = matte("pair_white"); u = scaled(u, h=980)
    else:
        u = matte("pack4_white"); u = scaled(u, h=1000)
    img, _ = put(img, u, (S - u.width) / 2, 385, sh=(12, 14), blur=14, alpha=60)
    BG = img.copy(); RECORD.clear(); d = ImageDraw.Draw(img)
    header(d, 110, "IN THE BOX", head, sz=78)
    f = font(F_BODY, 40, 600)
    items = [f"Pack of {n}", "Ready to hang", "No assembly"]
    widths = [tw(f, s) for s in items]; gap = 70
    x = (S - sum(widths) - gap * (len(items) - 1)) / 2
    for i, (s, w) in enumerate(zip(items, widths)):
        text(d, x, 1450, s, f, INK)
        if i < len(items) - 1: diamond(d, x + w + gap / 2, 1437, 8, GOLD)
        x += w + gap
    audit(BG, "other5"); save(img, out, "inbox")

def g_compare(out):
    """dark festive slide, like BhogKart's 'One prasad for the whole festive season'"""
    img = plate("night_sq")
    A = np.asarray(img).astype(float); night = tuple(int(c) for c in np.median(A[:300, :400].reshape(-1, 3), axis=0))
    img = vscrim(img, night, 0, 1150, 0.55, 0.0)
    img = grain(img, 1.6)
    L, R = strands()
    h = 470
    for u, cx in ((L, S / 2 - 46), (R, S / 2 + 46)):
        u2 = scaled(u, h=h)
        img, _ = put(img, u2, cx - u2.width / 2, 400, sh=(0, 0), blur=24, alpha=0)
    BG = img.copy(); RECORD.clear(); d = ImageDraw.Draw(img)
    f1 = HEAD(70)
    text(d, S / 2, 170, "A fresh flower toran lasts till morning.", f1, IVORY, anchor="ms")
    text(d, S / 2, 260, "This one comes back every festival.", f1, GOLD_LIGHT, anchor="ms")
    divider(d, S / 2, 315, 240, GOLD_LIGHT, align="center")
    cols = [("Fresh flower toran", ["Wilts by the next day", "Drops petals on the floor", "Bought again every festival", "Flowers only"], (205, 190, 170), 110),
            ("This latkan", ["Same colour, year after year", "Nothing to sweep up", "Wipe, store flat, hang again", "Ganesha, lotus and bells in one"], IVORY, 1000)]
    for h_, items, col, x in cols:
        x = x - 40 if x > S / 2 else x
        text(d, x, 470, h_, font(F_HEAD, 46, 700), GOLD_LIGHT)
        y = 560
        for it in items:
            for k, ln in enumerate(wrap(it, BODYF(38), 520)):
                if k == 0: diamond(d, x + 8, y - 13, 8, GOLD_LIGHT)
                text(d, x + 32, y, ln, BODYF(38), col); y += 48
            y += 30
    text(d, S / 2, 1500, "For Diwali, Ganpati, Navratri and every Griha Pravesh in between", font(F_BODY, 42, 600), GOLD_LIGHT, anchor="ms")
    audit(BG, "other6"); save(img, out, "compare")

def g_uses(out):
    img = grain(plate("ivory_stage"), 1.6)
    st = strands()[1]
    u = scaled(st, h=1150)
    img, _ = put(img, u, S - 250 - u.width / 2, 360, sh=(10, 12), blur=12, alpha=55)
    BG = img.copy(); RECORD.clear(); d = ImageDraw.Draw(img)
    header(d, 110, "WHERE IT GOES", ["Where you pray, and", "where your guests walk in"], sz=78)
    uses = [("Main door", "Both sides of the frame, the way a toran is meant to frame it"),
            ("Pooja room and mandir", "Either side of the mandir or the idol"),
            ("Ganpati and Diwali", "Backdrop for Ganesh Chaturthi, Diwali and Lakshmi Puja"),
            ("Griha Pravesh and weddings", "Housewarming, mehndi and haldi corners")]
    y = 520
    for t, s in uses:
        diamond(d, 130, y - 15, 11, GOLD)
        text(d, 162, y, t, font(F_HEAD, 50, 700), INK)
        for k, ln in enumerate(wrap(s, BODYF(38), 860)):
            text(d, 162, y + 62 + k * 48, ln, BODYF(38), BODY)
        y += 62 + 48 * len(wrap(s, BODYF(38), 860)) + 70
    audit(BG, "other7"); save(img, out, "uses")

def g_real(out):
    img = grain(plate("ivory_stage", fx=0.2), 1.6)
    ph = photo("pack4_real").resize((800, 1422), Image.LANCZOS)
    img.paste(ph, (S - 800 - 60, 89))
    d0 = ImageDraw.Draw(img)
    d0.rectangle([S - 800 - 60 - 14, 89 - 14, S - 60 + 13, 89 + 1422 + 13], outline=GOLD, width=2)
    BG = img.copy(); RECORD.clear(); d = ImageDraw.Draw(img)
    cx = 380
    text(d, cx, 560, "REAL PHOTO", EYE(), GOLD_TEXT, tracking=7, anchor="ms")
    for k, ln in enumerate(["Photographed", "at home.", "Not a render."]):
        text(d, cx, 680 + k * 92, ln, HEAD(76), INK, anchor="ms")
    divider(d, cx, 920, 200, GOLD, align="center")
    for k, ln in enumerate(wrap("The Pack of 4, held up before packing. Colours and bells are exactly what you receive.", BODYF(38), 520)):
        text(d, cx, 1010 + k * 50, ln, BODYF(38), BODY, anchor="ms")
    audit(BG, "other8"); save(img, out, "real")

# ---------------- A+ ----------------
def aplus(outdir):
    W, H = 1940, 1200                         # Standard Image Header with Text, 970 x 600 at 2x
    img = plate("door_wide", W, H)
    L, R = strands()
    h = 470                                   # ~86 cm against the ~210 cm door on this plate
    for u, cx in ((L, 1035), (R, 1695)):
        u2 = scene(scaled(u, h=h), bright=0.88, warm=1.07)
        img, _ = put(img, u2, cx - u2.width / 2, 60, sh=(12, 10), blur=8, alpha=80)
    img = hscrim(img, IVORY, 0, 980, 0.35, 0.0)
    img = grain(img, 3.0)
    BG = img.copy(); RECORD.clear(); d = ImageDraw.Draw(img)
    cx = 480
    text(d, cx, 360, "ATREYA", font(F_BODY, 44, 600), GOLD_TEXT, tracking=12, anchor="ms")
    text(d, cx, 490, "Shubh aarambh,", HEAD(100), INK, anchor="ms")
    text(d, cx, 610, "at every doorway", HEAD(100), INK, anchor="ms")
    divider(d, cx, 670, 260, GOLD, align="center")
    for k, ln in enumerate(wrap("Ganesha lotus latkan with gold bells and a pearl tassel. Ready to hang for Diwali, Ganpati and every Griha Pravesh.", BODYF(42), 760)):
        text(d, cx, 770 + k * 56, ln, BODYF(42), BODY, anchor="ms")
    audit(BG, "aplus header"); save(img, f"{outdir}/aplus_1_header_970x600.jpg", "aplus")

    T = 600                                   # three images and text, 300 x 300 at 2x
    close = photo("pack4_closeup")
    tiles = [(close.crop((440, 470, 1040, 1070)), "aplus_2a_ganesha"),
             (close.crop((230, 60, 700, 530)), "aplus_2b_lotus")]
    for im, name in tiles:
        t = grain(im.resize((T, T), Image.LANCZOS), 1.4)
        frame(ImageDraw.Draw(t), T, T, 16, GOLD_LIGHT, 2)
        save(t, f"{outdir}/{name}_300x300.jpg", name)
    pk = matte("pack4_white")                 # bells and pearl tassels: bottom of the Pack of 4 photo, ~1.1x
    seg = scaled(pk.crop((0, pk.height - 520, pk.width, pk.height)), h=584)
    t = grain(plate("ivory_stage", T, T, 0.5, 0.3), 1.4)
    t, _ = put(t, seg, (T - seg.width) / 2, 0, sh=(8, 10), blur=10, alpha=55)
    frame(ImageDraw.Draw(t), T, T, 16, GOLD, 2)
    save(t, f"{outdir}/aplus_2c_bells_pearls_300x300.jpg", "pearls")

    t = plate("ivory_stage", T, T)            # single image and highlights, 300 x 300 at 2x
    pair = scaled(matte("pair_white"), h=540)
    t, _ = put(t, pair, (T - pair.width) / 2, 30, sh=(8, 10), blur=10, alpha=55)
    t = grain(t, 1.4); frame(ImageDraw.Draw(t), T, T, 16, GOLD, 2)
    save(t, f"{outdir}/aplus_3_pair_300x300.jpg", "pair")

if __name__ == "__main__":
    for n in (2, 4):
        d = os.path.join(ROOT, f"ATR-GANESH-LOTUSBELL-LATKAN-{n}")
        g_lifestyle(f"{d}/other1.jpg")
        g_anatomy(f"{d}/other2.jpg")
        g_closeup(f"{d}/other3.jpg")
        g_size(f"{d}/other4.jpg")
        g_inbox(f"{d}/other5.jpg", n)
        g_compare(f"{d}/other6.jpg")
        g_uses(f"{d}/other7.jpg")
        if n == 4: g_real(f"{d}/other8.jpg")
    aplus(os.path.join(ROOT, "aplus"))
