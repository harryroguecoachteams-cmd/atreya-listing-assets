# Atreya Ganesh lotus bell latkan

| SKU | Pack | Price | MRP |
|---|---|---|---|
| ATR-GANESH-LOTUSBELL-LATKAN-2 | 2 strands | Rs 249 | Rs 599 |
| ATR-GANESH-LOTUSBELL-LATKAN-4 | 4 strands | Rs 399 | Rs 999 |

All copy lives in `listing.json`. Images are 1600 x 1600 and served from this repo's raw URLs.

## Check before going live

1. **Length and width.** 55 x 9 cm is estimated from the photos. Measure one strand. If it's
   different, change `LENGTH_TXT` / `WIDTH_TXT` in `tools/make_images.py`, `strand_length_cm`
   in `listing.json` and bullet 1, then re-render:
   `python tools/make_images.py`
2. **Package size and weight** for each pack (`package_cm`, `package_weight_g`).
3. **Stock**: `quantity` is 0 for both SKUs.
4. **HSN / GST**: copy them from your existing Ganesh latkan.

## Amazon (run on the PC that has `E:/atreya/listing/atreya-aplus/.env`)

```
node amazon_push.mjs listings            # validation only, prints Amazon's issues
node amazon_push.mjs listings --live     # creates both listings
node amazon_push.mjs status              # wait for both ASINs (15-30 min)
node amazon_push.mjs aplus               # uploads A+ images, validates against the ASINs
node amazon_push.mjs aplus --live        # creates A+ and submits it for approval
```

## Flipkart

The Listings API v3 adds a listing to an existing FSN. For a new Atreya product, first upload the
catalog in Seller Hub (Toran vertical) using the `flipkart` block in `listing.json` and the same images.
Once the FSNs appear:

```
node flipkart_push.mjs --fsn2 <FSN> --fsn4 <FSN>          # prints the request
node flipkart_push.mjs --fsn2 <FSN> --fsn4 <FSN> --live   # creates both listings
```

## Images

| File | What it shows |
|---|---|
| main | Pack on pure white (pair for -2, bunch for -4) |
| other1 | Lifestyle: hung on both sides of a main door |
| other2 | What is on every strand (labelled parts) |
| other3 | Ganesha close-up |
| other4 | Size (estimate, see above) |
| other5 | In the box |
| other6 | Fresh flower toran vs this latkan |
| other7 | Where it goes |
| other8 | Real photo at home (Pack of 4 only) |
| aplus/ | Header 970x600 (made at 1940x1200), three image+text tiles, single image highlights (made at 600x600) |

How they are made (look matches BhogKart's live Amazon gallery, B0HHPHVJ42):

1. `python tools/plates.py`: empty background plates on Azure gpt-image-2 (no product in them).
2. `python tools/mattes.py`: cutouts of `source/pair_white.jpg` and `source/pack4_white.jpg` with the
   original photo pixels (isnet + white-difference matte; run it through `safe_heavy.ps1`).
3. `python tools/make_images.py`: pastes the real product onto the plates and sets the type
   (Playfair Display + EB Garamond, BhogKart colours). `main.jpg` is never rebuilt.

The model never sees or redraws the product, so the Ganesha, lotus buds, bells, flowers and pearl
tassel are exactly as photographed. Only brightness and warmth are matched in the two door scenes.
