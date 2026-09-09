# Generator assets — moved out of the hidden Desktop/.nf-build on 9 Sep 2026

`im0-v2.raw` / `250/im0-250.raw`: the extended CMYK canopy rasters (9064x6072, 4795x2433),
produced by `raster_v2.py`. `overlay*.pdf`, `v2-ref-cmyk.jpg`: the sheet overlay and reference
thumbnail each build consumes. `fonts/`: the twelve faces reportlab registers.

The scripts still expect these BESIDE them (HERE/...) and the native .ai one folder up. To run
today: copy the script into this folder's parent layout, or adjust HERE. Untangling that path
assumption is the next small job; the assets are no longer hidden, which was the point.
