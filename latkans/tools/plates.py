"""Empty background plates for the Ganesh lotus bell latkan images, made on Azure gpt-image-2.
The plates never contain the product: the latkans are pasted on afterwards from the real photos in
source/, so the model cannot redraw the Ganesha, lotus buds, bells, flowers or pearl tassel.
Look follows BhogKart's live Amazon gallery (B0HHPHVJ42): warm ivory, antique brass, peacock teal, marigold.
python tools/plates.py [id ...] [--force]   -> tools/plates/<id>.jpg"""
import base64, io, pathlib, sys, time, concurrent.futures as cf
sys.path.insert(0, r"E:\bhogkart\amazon_ready\panjiri_satvik")
import az                                    # key from the Azure keys docx, never stored here
from PIL import Image

OUT = pathlib.Path(__file__).parent / "plates"; OUT.mkdir(exist_ok=True)

HOUSE = ("A real photograph taken on a DSLR for a premium Indian home-decor brand: natural, true-to-life colour, "
         "realistic imperfect textures, soft film-like grain, shallow depth of field. Not a 3D render, not CGI, "
         "not an illustration. Palette: warm ivory, antique brass gold and deep peacock teal, with marigold "
         "orange accents. Light: soft, warm late-afternoon window light and the gentle glow of small diya flames. "
         "Props are few and refined. Calm, uncluttered, generous negative space. The picture contains no words, "
         "letters, numbers, logos, watermarks or people, and nothing hangs anywhere: no latkans, no torans, no "
         "garlands, no wall hangings, no ornaments, no bells. ")

JOBS = {
    "door_sq": ("2048x2048",
        HOUSE + "Straight-on, eye-level view of the main entrance of a calm Indian home at Diwali dusk. A simple "
        "wooden front door painted deep peacock teal with a plain, flat, light-wood door frame, set in a warm "
        "off-white limewash plaster wall with a gentle hand-troweled texture. The door and frame fill the middle "
        "half of the picture, from near the top edge down to the floor. The wall on both sides of the frame is "
        "plain and completely empty. On the floor at the threshold: a small, simple rangoli of marigold petals "
        "and four lit clay diyas, and a brass urli with floating marigolds at one side. Warm, soft light."),
    "door_wide": ("2048x1264",
        HOUSE + "Straight-on, eye-level view of the main entrance of a calm Indian home at Diwali dusk. On the "
        "right half of the picture: a simple wooden front door painted deep peacock teal with a plain, flat, "
        "light-wood door frame, from near the top edge down to the floor, in a warm off-white limewash plaster "
        "wall. The left 45 percent of the picture is that same plain limewash wall, softly lit and completely "
        "empty. On the floor at the threshold: a few lit clay diyas and marigold petals."),
    "ivory_stage": ("2048x2048",
        HOUSE + "An empty product backdrop. A plain warm ivory limewash plaster wall fills almost the whole "
        "frame, evenly and softly lit, with a faint warm glow of out-of-focus golden festive lights only in "
        "the top two corners. Along the very bottom edge only, a sliver of ivory handloom cloth with, at the "
        "far left corner, a fold of deep peacock-teal silk and a lit clay diya, and at the far right corner a "
        "few marigold flowers and a small brass bell lying on its side. The middle 80 percent of the frame is "
        "completely empty, smooth ivory wall."),
    "night_sq": ("2048x2048",
        HOUSE + "Diwali night, low key. The top half of the frame is a deep, warm, almost black background with "
        "a faint scatter of tiny out-of-focus golden lights. In the bottom third: a round hand-beaten brass puja "
        "thali on a dark wooden surface with five lit clay diyas, a few marigold flowers and petals, a little "
        "heap of rice and kumkum, and a fold of deep peacock-teal silk behind it, all glowing warmly."),
}

def run(jid, force):
    out = OUT / f"{jid}.jpg"
    if out.exists() and not force: return f"{jid}: exists"
    size, prompt = JOBS[jid]
    tmp = OUT / f"_{jid}.png"
    t = time.time()
    if not az.generate(prompt, str(tmp), size=size, quality="high"): return f"{jid}: FAILED"
    Image.open(tmp).convert("RGB").save(out, quality=95); tmp.unlink()
    return f"{jid}: {Image.open(out).size} in {time.time() - t:.0f}s"

if __name__ == "__main__":
    force = "--force" in sys.argv
    ids = [a for a in sys.argv[1:] if not a.startswith("--")] or list(JOBS)
    with cf.ThreadPoolExecutor(4) as ex:
        for r in ex.map(lambda j: run(j, force), ids): print(r, flush=True)
