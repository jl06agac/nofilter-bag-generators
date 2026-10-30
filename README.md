# Packaging print masters — what is here and why (9 Sep 2026)

| | Why it is here |
|---|---|
| `NoFilter_1kg_Bag_DIELINE_V3_2.pdf`, `NoFilter_250g_Bag_DIELINE_V2_2.pdf` | **Current SG print files (29 Sep 2026).** Same artwork as V3.1 / V2.1 with the legal block changed to "Roasted for NoFilter Pte. Ltd. / at 31 Kaki Bukit Road 3… / hello@nofilter.sg" (no UEN). Built by `_generators/`, checked against the V3.1 / V2.1 files: only the legal block and the job-sheet date/version differ |
| `_working-2026-09/` | The two files **at the printer**: `NoFilter_1kg_Bag_DIELINE_V3_1.pdf`, `NoFilter_250g_Bag_DIELINE_V2_1.pdf`, plus the 1 kg background PDF. Frozen. Drive copy: `Packaging (Print Files)/Packaging-Print-Masters/_working-2026-09` (the separate root-level `_working-2026-09` duplicate was removed 24 Oct 2026) |
| `_generators/` | The scripts that rebuild them, proven against the printed files. In git `nofilter-bag-generators` |
| `NoFilter_1kg_Bag_NATIVEV1.ai`, `NoFilter_250g_Bag_PRINT_NATIVEv1.ai` | **Ingredients**: the generators lift the front and left panels from these |
| `BACKGROUND PICTURE 1KG.tif`, `250 G BACKGROUND IMAGE.tif` | **Ingredients**: `raster_v2.py` / `build_250.py` read them |
| `FONTS/` | Ingredient |
| `origin-stickers/` | The sticker system for the bags, in git |
| `NoFilter_8oz_Cup_ARTWORK.zip` | Not yet in Drive. Drag to `Packaging (Print Files)/NF _CUP`, then delete here |

Deleted 9 Sep: the V1 PROOF and PDF/X-4 outputs (781 MB). They are what went to print in June and
they live in Drive under `NF_1 KG_BAG` / `NF_250 G _BAG`, byte-verified. Outputs are not kept locally.
