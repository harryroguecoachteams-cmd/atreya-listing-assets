"""Product mattes from the white-background photos in source/. Product RGB stays the original photo
pixels; only alpha is computed: isnet alpha OR a difference matte against the pure-white backdrop
(isnet alone drops the white pearls). Run heavy step via C:/Users/hp/tools/safe_heavy.ps1
(birefnet does not fit in RAM here; isnet peaks ~1.6 GB).
python tools/mattes.py -> tools/mattes/matte_<name>.png"""
import os, numpy as np
from PIL import Image, ImageFilter
HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "source")
M = os.path.join(HERE, "mattes")

def isnet(n):
    p = os.path.join(M, f"cut_{n}.png")
    if not os.path.exists(p):
        from rembg import remove, new_session
        remove(Image.open(os.path.join(SRC, n + ".jpg")).convert("RGB"), session=new_session("isnet-general-use")).save(p)
    return np.asarray(Image.open(p).split()[3]).astype(float)

for n in ("pair_white", "pack4_white"):
    rgb = Image.open(os.path.join(SRC, n + ".jpg")).convert("RGB")
    A = np.asarray(rgb).astype(float)
    dist = np.maximum(255 - A.min(axis=2), A.max(axis=2) - A.min(axis=2))
    a = np.maximum(isnet(n), np.clip((dist - 6) * 255 / 22, 0, 255))
    a[a < 18] = 0
    # the studio floor shadow under the tassel is grey-white and unsaturated: from the bottom up, while
    # a row's opaque pixels average under 30 saturation, keep only its coloured (flower) pixels
    sat = A.max(axis=2) - A.min(axis=2)
    ys = np.where((a > 60).any(axis=1))[0]
    for y in ys[::-1]:
        m = a[y] > 60
        if sat[y, m].mean() >= 30: break
        a[y, sat[y] < 40] = 0
    am = Image.fromarray(a.astype("uint8")).filter(ImageFilter.GaussianBlur(0.6))
    out = rgb.convert("RGBA"); out.putalpha(am)
    out.crop(am.point(lambda v: 255 if v > 30 else 0).getbbox()).save(os.path.join(M, f"matte_{n}.png"))
    print("matte", n)
