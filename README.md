# Packaging print masters — what is here and why (9 Sep 2026)

| | Why it is here |
|---|---|
| `_working-2026-09/` | The two files **at the printer**: `NoFilter_1kg_Bag_DIELINE_V3_1.pdf`, `NoFilter_250g_Bag_DIELINE_V2_1.pdf`, plus the 1 kg background PDF. Frozen. Also in Drive `Packaging (Print Files)/_working-2026-09`, byte-verified |
| `_generators/` | The scripts that rebuild them, proven against the printed files. In git `nofilter-bag-generators` |
| `NoFilter_1kg_Bag_NATIVEV1.ai`, `NoFilter_250g_Bag_PRINT_NATIVEv1.ai` | **Ingredients**: the generators lift the front and left panels from these |
| `BACKGROUND PICTURE 1KG.tif`, `250 G BACKGROUND IMAGE.tif` | **Ingredients**: `raster_v2.py` / `build_250.py` read them |
| `FONTS/` | Ingredient |
| `origin-stickers/` | The sticker system for the bags, in git |
| `NoFilter_8oz_Cup_ARTWORK.zip` | Not yet in Drive. Drag to `Packaging (Print Files)/NF _CUP`, then delete here |

Deleted 9 Sep: the V1 PROOF and PDF/X-4 outputs (781 MB). They are what went to print in June and
they live in Drive under `NF_1 KG_BAG` / `NF_250 G _BAG`, byte-verified. Outputs are not kept locally.
