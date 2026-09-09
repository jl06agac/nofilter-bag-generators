# What V3.1 and V2.1 actually changed — measured, not remembered

> **RESULT, 9 Sep 2026: PASSED.** `build_1kg_v3_1.py` and `build_250g_v2_1.py` (GPT reconstructions,
> read from the frozen PDFs against this test) were run locally and their output compared with the
> frozen files. 250 g: 60/60 text items within 0.5 pt, **zero differing pixels** at 72 ppi. 1 kg:
> 66/66 after one measured correction (R12, the VERSION caption 2.696 mm right; cause unrecovered),
> 0.027 % pixels differing before R12, all in that caption or sub-pixel noise. Page boxes, image
> XObject sizes, fonts and the `/Separation /PANTONE 172 U` colour space match on both.
> The bags now have a generator that rebuilds the printed files.

_9 Sep 2026. Measured from the PDFs themselves with pypdf: text positions, image XObjects,
content-stream fingerprints. This is the test any reconstructed build script must pass.
A script that reproduces GPT's summary ("3 mm rightward text shift, white outline extended")
and nothing else will FAIL it._

**Status: `DIELINE_V3_1.pdf` and `250g_DIELINE_V2_1.pdf` were sent to the printer on 9 Sep 2026.**
They are frozen. The generator matters for the next change, not this one.

## 1 kg — V2 → V3.1  (page 2275.33 × 1501.33 pt, unchanged)

| Change | Measured |
|---|---|
| Back-panel body text, 11 lines | dx −22.6 pt (**8 mm LEFT**), dy +0.1 … +35.1 pt (up to 12 mm up, more at the top). Re-set, not shifted |
| Headline, 3 lines | `MOST COFFEE BEGINS WITH` dx −31.4 dy +75.9 · `PRICE AND TASTE.` dx −75.5 dy +74.9 · `WE BEGIN WITH PLACE.` dx +10.5 dy +69.0 |
| `Where can your cuppa do the most good?` | dx −8.8 dy +65.9 |
| `CONSERVATION COFFEE` | **new** text item at (470.0, 989.0) |
| Spec block | V2: "Orange solids … one CMYK raster (461 ppi)". V3.1: "**PANTONE 172 U spot orange.** Original CMYK artwork retained. Back and far-side canopy reframed. White text and boundary k[nock out]… Original cutter, dimensions, page boxes and FOGRA39 profile … PDF/X-4 metadata retained; independent preflight required" |
| Version caption | `V2 dieline, build 06/09/2026 13:42` → `V3.1 dieline, revised 07/09/2026`; date `06/09/2026` → `07/09/2026` |
| Sheet reference thumbnail `/FormXob.6583…` | **1400 × 1052 → 930 × 799**. _Corrected 9 Sep: this form is the visual-reference thumbnail, not the canopy placement; the canopy is a separate clipped enlargement. GPT identified this from the frozen PDF._ |
| `/Im0` 9064 × 6072 canopy raster, `/Im1` 1082 × 804 | unchanged |
| Fonts | identical set |
| Content stream | 123,206 b `6db1bfce37c8` → 122,676 b `374f466d1c45` — regenerated, not patched |

## 250 g — V2 → V2.1  (page 1778.1 × 1066.86 pt, unchanged)

| Change | Measured |
|---|---|
| `CONSERVATION COFFEE` | **new** at (264.1, 735.0) |
| Address block | `NoFilter Pte. Ltd.` dx −8.4 · `31 Kaki Bukit Road 3…` dx −26.5 dy −2.2 · `UEN … hello@nofilter.sg` dx −15.8 dy −4.3 |
| `250G` | dy +14.8 |
| `STRONGER COMMUNITIES` / `HEALTHIER FORESTS` | dy −2.3 / −4.5 |
| Sheet reference thumbnail | **1400 × 950 → 1038 × 705** (same correction as the 1 kg) |
| `/Im0` 4795 × 2433, `/Im1` 1448 × 1086 | unchanged |
| Content stream | 102,674 b `f9bc6d475b84` → 102,761 b `26832e51872f` |

## How to run the test

1. Run the reconstructed script. It must write a PDF, not a PNG.
2. Re-run the probe (pypdf: MediaBox, XObject sizes, text positions via `visitor_text`) on its
   output and on the frozen PDF above.
3. Every row must match to within 0.5 pt. The content-stream md5 will NOT match (reportlab
   emits timestamps); the byte length should be within ~1%.
4. Render both at 150 ppi and diff the rasters. Anything above JPEG noise in the vector
   layer is a miss.

Hand GPT this table, not its own summary.
