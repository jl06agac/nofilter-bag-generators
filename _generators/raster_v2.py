#!/usr/bin/env python3
"""Raster repairs on the canopy/clearing image for V2, written as im0-v2.raw for build_v2.py to embed:
 A) stray clearing above the new line on the back (native arc) -> canopy texture
 B) forest strip at the bottom of side 1 -> clearing texture (so side 1 runs orange to the bottom)"""
import numpy as np, importlib.util, os
from PIL import Image, ImageDraw, ImageFilter
Image.MAX_IMAGE_PIXELS = None
HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location('b', os.path.join(HERE, 'build_v2.py')); b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
rng = np.random.default_rng(7)
a = np.asarray(Image.open(os.path.join(HERE, 'im-000.tif'))).copy()
H, W, _ = a.shape; S = W/499.4
def px(x, y): return (x-119.6)*S, (y-56.2)*S
def polymask(pts):
    m = Image.new('L', (W, H), 0); ImageDraw.Draw(m).polygon([px(x, y) for x, y in pts], fill=255); return np.asarray(m) > 0
clear = (a[..., 1] > 140) & (a[..., 0] < 80)

def quilt(F, src_ok, clean, P=480, ST=300):
    ys, xs = np.nonzero(F)
    if len(ys) == 0: return
    y0, y1 = max(0, ys.min()-40), min(H, ys.max()+40); x0, x1 = max(0, xs.min()-40), min(W, xs.max()+40)
    oy, ox = np.nonzero(src_ok); ok = [(x*8, y*8) for x, y in zip(ox, oy) if x*8+P < W and y*8+P < H]
    win1 = 0.5-0.5*np.cos(2*np.pi*(np.arange(P)+0.5)/P); win = np.outer(win1, win1).astype(np.float32)
    acc = np.zeros((y1-y0, x1-x0, 4), np.float32); wgt = np.zeros((y1-y0, x1-x0), np.float32)
    for ty in range(y0-P//2, y1, ST):
        for tx in range(x0-P//2, x1, ST):
            for _ in range(200):
                sx, sy = ok[rng.integers(len(ok))]
                if clean(sy, sx, P): break
            patch = a[sy:sy+P, sx:sx+P].astype(np.float32)
            if rng.random() < 0.5: patch = patch[:, ::-1]
            ay0, ax0 = max(ty, y0), max(tx, x0); ay1, ax1 = min(ty+P, y1), min(tx+P, x1)
            if ay1 <= ay0 or ax1 <= ax0: continue
            py0, px0 = ay0-ty, ax0-tx; py1, px1 = py0+(ay1-ay0), px0+(ax1-ax0)
            w = win[py0:py1, px0:px1]
            acc[ay0-y0:ay1-y0, ax0-x0:ax1-x0] += patch[py0:py1, px0:px1]*w[..., None]; wgt[ay0-y0:ay1-y0, ax0-x0:ax1-x0] += w
    tex = acc/np.maximum(wgt, 1e-6)[..., None]
    Fm = np.asarray(Image.fromarray((F[y0:y1, x0:x1]*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(5))).astype(np.float32)/255
    reg = a[y0:y1, x0:x1].astype(np.float32)*(1-Fm[..., None]) + tex*Fm[..., None]
    a[y0:y1, x0:x1] = np.clip(reg, 0, 255).astype(np.uint8)
    print('filled', int(F.sum()), 'px')

def eroded(mask, r):
    sm = np.asarray(Image.fromarray((mask[::8, ::8]*255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(4))) > 128
    return np.asarray(Image.fromarray((sm*255).astype(np.uint8)).filter(ImageFilter.MinFilter(2*r+1))) > 0

# A) canopy over the native clearing arc that pokes above our field
T = polymask(b.ORANGE_POLY)
NAT = [(368.2,225.0),(373.9,229.3),(381.1,235.9),(390.4,238.3),(396.2,233.4),(400.8,225.7),(402.7,218.7),(409.5,208.9),(414.9,201.9),
       (425.2,191.9),(437.6,182.9),(457.1,181.4),(485.9,181.5),(501.2,183.2),(519.6,187.7),(521.0,187.7),(521.0,390.0),(368.2,390.0)]
Td = np.asarray(Image.fromarray((T*255).astype(np.uint8)).filter(ImageFilter.MaxFilter(15))) > 0
FA = polymask(NAT) & ~Td
canopy_src = eroded(~clear, 30); canopy_src[int(px(0,175)[1])//8:, :] = False
quilt(FA, canopy_src, lambda sy, sx, P: (~clear[sy:sy+P, sx:sx+P]).mean() >= 0.995)

# B) clearing over the forest strip at the bottom of side 1 (x 270..368.5, y 340..bleed)
FB = polymask([(270.0,340.0),(368.6,340.0),(368.6,390.0),(270.0,390.0)]) & ~clear
clear_src = eroded(clear, 30); clear_src[:, int(px(368.5,0)[0])//8:] = False
def clean_clear(sy, sx, P):
    pp = a[sy:sy+P, sx:sx+P]
    return clear[sy:sy+P, sx:sx+P].mean() >= 0.90 and np.percentile(pp[..., 3], 99.5) < 40 and np.percentile(pp[..., 0], 99.5) < 60 and pp[..., 3].mean() < 2.0
quilt(FB, clear_src, clean_clear)

# C) the forest inlet at the side-1/back fold (native notch) -> clearing
FC = polymask([(360.0,228.7),(369.5,228.7),(369.5,243.0),(360.0,243.0)]) & ~clear     # starts under the stroke's lower edge; nothing above the line is touched
quilt(FC, clear_src, clean_clear, P=240, ST=150)
# D) ragged clearing edge in the front's bottom-right pocket, between the line and the fold -> clean clearing
FD = polymask([(266.0,362.0),(276.0,362.0),(276.0,392.0),(268.0,392.0),(269.5,386.5),(264.0,380.5),(261.0,379.2),(260.0,374.5),(263.5,373.5),(267.8,368.0)]) & ~clear
quilt(FD, clear_src, clean_clear, P=240, ST=150)
# E) sliver of clearing between the lifted crossbar and the gusset fold -> canopy
FE = polymask([(152.0,384.3),(188.0,384.3),(188.0,391.0),(152.0,391.0)]) & clear
quilt(FE, canopy_src, lambda sy, sx, P: (~clear[sy:sy+P, sx:sx+P]).mean() >= 0.995, P=240, ST=150)
open(os.path.join(HERE, 'im0-v2.raw'), 'wb').write(a.tobytes()); print('wrote im0-v2.raw')
