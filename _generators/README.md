# Bag dieline generators — INCOMPLETE, read this before trusting it

Rescued 9 Sep 2026 from `Desktop/.nf-build/`, a **hidden** folder that no survey of the
workspace had ever shown. That is why nobody knew the bags had a generator at all.

## What is here, and what it makes

| script | makes | dated |
|---|---|---|
| `build_v2.py` — **this is the 1 kg build**; the size is missing from its name | `NoFilter_1kg_Bag_DIELINE_V2.pdf` | 6 Sep 2026 |
| `raster_v2.py` | `im0-v2.raw`, the 9064x6072 CMYK canopy raster `build_v2.py` consumes | 6 Sep |
| `250/build_250.py` | `NoFilter_250g_Bag_DIELINE_V2.pdf` | 6 Sep |
| `analyse.py`, `250/analyse250.py` | checking passes | 6 Sep |

`build_v2.py` says it plainly in its own docstring: *"single source of truth for V2; edit this
script, rerun"*. Front and left side are lifted verbatim from `NoFilter_1kg_Bag_NATIVEV1.ai`,
so that native file is an **ingredient**, not just an archive copy. Do not delete it.

## Naming

`build_v2.py` is the 1 kg bag. `250/build_250.py` is the 250 g bag. Only one of them says so.
Not renamed, because GPT is being asked to reconstruct from it under that name. The reconstructed
files are to be named `build_1kg_v3_1.py` and `build_250g_v2_1.py`; from then on the size is in
every name.

## THE GAP — CLOSED 9 Sep 2026

`build_1kg_v3_1.py` and `build_250g_v2_1.py` are GPT reconstructions, written against the measured
acceptance test and the frozen PDFs, then run here and compared: **250 g pixel-identical, 1 kg 66/66
after one 2.7 mm caption correction (R12).** See `ACCEPTANCE-TEST-…md` for the row-by-row result.
They are the bag generators from now on. `build_v2.py` / `build_250.py` are their ancestors, kept.

## How to run them

They expect their assets beside them, which today means `Desktop/.nf-build/` (1 kg) and
`Desktop/.nf-build/250/` (250 g): `im0-v2.raw` / `im0-250.raw` (rasters from `raster_v2.py`),
`fonts/`, and the native `.ai` one folder above. Copy the script there, run `python3 <script>`,
output is `*_RECONSTRUCTED.pdf` one folder above — never the frozen filename. Needs pypdf,
reportlab, Pillow, numpy, and the FOGRA39 profile (`NOFILTER_ICC` overrides the path).
Moving the assets out of the hidden folder into here is the obvious next tidy; not done yet.

`NoFilter_1kg_Artwork_V4.pdf` is a different lineage (PyMuPDF, 1405.98 × 1207.56 pt) and is
**discarded** per GPT 9 Sep. See register §8.
