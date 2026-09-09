#!/usr/bin/env python3
"""NoFilter 250 g bag — dieline V2 (same system as the 1 kg V2).
Front lifted verbatim from NoFilter_250g_Bag_PRINT_NATIVEv1.ai; side 1, back, side 2, gusset and spec block rebuilt;
boundary line made contiguous (front -> side 1 native, back + side 2 new, through the T of HOLD THE LINE).
Background re-embedded from the 300 dpi CMYK TIF (the native carried a 2048 px RGB copy).
Output: ../../NoFilter_250g_Bag_DIELINE_V2.pdf   (edit this script, rerun)."""
import os, math, copy, datetime, zlib
import pypdf.filters; pypdf.filters.MAX_DECLARED_STREAM_LENGTH = 10**10
from pypdf import PdfReader, PdfWriter
from pypdf.generic import (ContentStream, NameObject, ArrayObject, DictionaryObject,
                           FloatObject, TextStringObject, NumberObject, IndirectObject)
from reportlab import rl_config
rl_config.canvas_basefontname = 'Archivo'
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import CMYKColor, CMYKColorSep

HERE   = os.path.dirname(os.path.abspath(__file__))
FONTS  = os.path.join(HERE, '..', 'fonts')
NATIVE = os.path.join(HERE, '..', '..', 'NoFilter_250g_Bag_PRINT_NATIVEv1.ai')
TIF    = os.path.join(HERE, '..', '..', '250 G BACKGROUND IMAGE.tif')
OUT    = os.path.join(HERE, '..', '..', 'NoFilter_250g_Bag_DIELINE_V2.pdf')
OVERLAY= os.path.join(HERE, 'overlay250.pdf')
REFIMG = os.path.join(HERE, 'v2-ref-cmyk.jpg')
RAW    = os.path.join(HERE, 'im0-250.raw')

PT = 72/25.4
PW, PH = 1778.1, 1066.86
AH = PH/PT
def X(x): return x*PT
def Y(y): return (AH - y)*PT

# ---- die geometry (mm) ----
TOP, BOT = 69.1, 269.1
GUS_BOT  = 339.1
FRONT, LEFT, BACK, RIGHT = 59.3, 189.3, 259.3, 389.3
FLAT_R = 459.3
BLEED_MM = 3.0
BACK_CX = BACK + 65.0            # 324.3
RIGHT_CX = RIGHT + 35.0          # 424.3
GUS_CX = FRONT + 65.0            # 124.3
# native photo placement (Im0 cm): x 55.5..462.5, y 65.3..274.4 mm
IMG_X0, IMG_Y1 = 157.374176/PT, AH - 289.071416/PT
IMG_W, IMG_H   = 1153.40808/PT, 592.841365/PT
IMG_Y0 = IMG_Y1 - IMG_H

pdfmetrics.registerFont(TTFont('BigShoulders',   os.path.join(FONTS, 'BigShoulders-Medium.ttf')))
pdfmetrics.registerFont(TTFont('BigShouldersXB', os.path.join(FONTS, 'BigShoulders-Black.ttf')))
pdfmetrics.registerFont(TTFont('ArchivoM',       os.path.join(FONTS, 'Archivo-Medium.ttf')))
pdfmetrics.registerFont(TTFont('Archivo',        os.path.join(FONTS, 'Archivo-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Mono',           os.path.join(FONTS, 'JetBrainsMono-Regular.ttf')))

WHITE = CMYKColor(0, 0, 0, 0)
BLACK = CMYKColor(0, 0, 0, 1)
PANT  = CMYKColorSep(0, 0.73, 0.87, 0, spotName='PANTONE 172 U')
DIE   = CMYKColorSep(1, 0, 0, 0, spotName='Die cut')
DIMS  = CMYKColorSep(0, 1, 0, 0, spotName='DIMENSIONS')
BLD   = CMYKColorSep(0, 0, 1, 0, spotName='BLEED')

# ---- side 2 lettering: fixed first so the line can be aimed through the T ----
HOLD_PT = 64
HOLD_BOTTOM = 222.0                                  # mm from top: where the H starts (text reads upwards)
def hold_metrics():
    cs = -0.01*HOLD_PT; ws = 0.12*HOLD_PT
    def w(s): return pdfmetrics.stringWidth(s, 'BigShouldersXB', HOLD_PT) + cs*len(s)
    pre = w('HOLD ') + ws                             # advance up to the T
    t_w = pdfmetrics.stringWidth('T', 'BigShouldersXB', HOLD_PT)
    total = w('HOLD THE LINE') + 2*ws
    pre_i = w('HOLD THE L') + 2*ws                    # advance up to the I of LINE
    i_w = pdfmetrics.stringWidth('I', 'BigShouldersXB', HOLD_PT)
    return pre/PT, t_w/PT, total/PT, pre_i/PT, i_w/PT
HOLD_PRE, HOLD_TW, HOLD_LEN, HOLD_PRE_I, HOLD_IW = hold_metrics()
I_Y = HOLD_BOTTOM - HOLD_PRE_I - HOLD_IW/2            # centre of the I's stem
T_Y = HOLD_BOTTOM - HOLD_PRE - HOLD_TW*0.55          # the T's stem, a touch below its middle
HOLD_TOP = HOLD_BOTTOM - HOLD_LEN
CROSS_Y = HOLD_TOP - 13.0

# ---- the contiguous boundary ----
# Native path kept, with its ticks, dots and coordinate labels, up to the top of the last riser at (341.6, 101.8). There is no crest:
# from that vertex the line follows Alex's sketch straight into a long, quiet descent: gentle fall, ledge, over the fold, gentle fall
# through THE / LINE, a short drop, then easing out low through the bleed.
NATIVE_CUT = (349.0, 110.0)                          # native apex (341.6, 101.8) pulled down-right so the last riser climbs at ~40 degrees, not 68
NATIVE_APEX = (341.6, 101.8)
BACK_CHAIN = [(258.9,151.0),(260.9,150.5),(267.9,148.7),(270.2,149.7),(279.4,144.3),(298.5,143.7),(315.4,130.5),(332.1,125.0),NATIVE_CUT]
# the descent keeps the native's own rhythm and angles: risers at 38-40 degrees, treads at 7-9, segments 10-20 mm long
DESCENT_BACK = [(358.0,110.7),(386.0,122.0)]                 # short crest, then one continuous fall; the step is held back to the fold itself
ENTRY = (RIGHT, 125.5)                               # the small step lands exactly on the fold; side 2 only trails away from it                               # the fold falls on the ledge, not on a riser
L_RIGHT = [ENTRY,(422.0,130.5),(434.0,140.0),(446.0,141.5),(FLAT_R+BLEED_MM,150.5)]   # shoulder, drop (cuts the foot of the L), brief flattening, taper out
LINE = [NATIVE_CUT] + DESCENT_BACK + L_RIGHT
COORDS = []
DOTS = []
TICKS = [((358.0,110.7),(386.0,122.0),0.5),((389.3,125.5),(422.0,130.5),0.5),((446.0,141.5),(462.3,150.5),0.45)]   # kept clear of the lettering and of the crossing
NATIVE_DOT = (354.65, 96.25); NEW_DOT = NATIVE_CUT   # the second coordinate dot + label move onto the new line
TOP_CHAIN = BACK_CHAIN + DESCENT_BACK + L_RIGHT
ORANGE_POLY = TOP_CHAIN + [(FLAT_R+BLEED_MM, BOT+BLEED_MM), (BACK, BOT+BLEED_MM), (BACK, BACK_CHAIN[0][1])]

# ---- copy ----
HEAD = ["MOST COFFEE BEGINS WITH", "PRICE AND TASTE."]
HEAD2 = "WE BEGIN WITH PLACE."
QUESTION = "Where can your cuppa do the most good?"
COUPLET = ["Grown one way, coffee can clear forest.", "Grown another, it can help keep forest standing."]
BODY = ["NoFilter partners exclusively with conservation NGOs and farming communities on the edges of threatened forests, backing the agroforestry coffee grown there and coming back for more."]
PROOF = "That’s why a share of every sale goes straight back to conservation in the same landscape."
SIDE1 = ["COFFEE FROM", "FORESTS", "STILL STANDING."]
SIDE1_SUB = ["BETTER COFFEE", "STRONGER COMMUNITIES", "HEALTHIER FORESTS"]
LEGAL = ["NoFilter Pte. Ltd.",
         "31 Kaki Bukit Road 3, #01-02C, TechLink, Singapore 417818",
         "UEN 201839882N · hello@nofilter.sg"]
GUSSET = ["IF YOU CAN READ THIS,", "YOU\u2019RE OUT OF COFFEE."]

# ================= drawing helpers =================
def text(c, s, x, y, font, size, align='l', tracking=0.0, color=WHITE):
    cs = tracking*size
    w = pdfmetrics.stringWidth(s, font, size) + cs*(len(s)-1)
    x0 = X(x) - (w/2 if align=='c' else w if align=='r' else 0)
    t = c.beginText(); t.setFont(font, size); t.setCharSpace(cs); t.setFillColor(color)
    t.setTextOrigin(x0, Y(y)); t.textOut(s); c.drawText(t)
    return w/PT

def paragraph(c, txt, x0, width_mm, y_first, font, size, leading_mm, ragged=True):
    W = width_mm*PT; words = txt.split(' ')
    n = len(words); sp = pdfmetrics.stringWidth(' ', font, size)
    wl = [pdfmetrics.stringWidth(w, font, size) for w in words]
    INF = float('inf'); best = [INF]*(n+1); brk = [0]*(n+1); best[0] = 0
    for j in range(1, n+1):
        width = -sp
        for i in range(j-1, -1, -1):
            width += wl[i] + sp
            if width > W and i < j-1: break
            slack = W - width
            cost = best[i] + (0.35*slack*slack if j == n else slack*slack)
            if cost < best[j]: best[j], brk[j] = cost, i
    lines = []; j = n
    while j > 0: lines.insert(0, words[brk[j]:j]); j = brk[j]
    y = y_first
    for ln in lines:
        s = ' '.join(ln)
        t = c.beginText(); t.setFont(font, size); t.setFillColor(WHITE); t.setCharSpace(0); t.setWordSpace(0)
        t.setTextOrigin(X(x0), Y(y)); t.textOut(s); c.drawText(t); y += leading_mm
    return y - leading_mm, len(lines)

def path_from(c, pts, close=False):
    p = c.beginPath(); p.moveTo(X(pts[0][0]), Y(pts[0][1]))
    for q in pts[1:]: p.lineTo(X(q[0]), Y(q[1]))
    if close: p.close()
    return p

def polyline(c, pts, lw, color=WHITE):
    c.setStrokeColor(color); c.setLineWidth(lw); c.setLineJoin(1); c.setLineCap(1)
    c.drawPath(path_from(c, pts), stroke=1, fill=0)

def polygon(c, pts, color):
    c.setFillColor(color); c.drawPath(path_from(c, pts, close=True), stroke=0, fill=1)

def rule(c, x0, x1, y, lw=0.5, color=WHITE):
    c.setStrokeColor(color); c.setLineWidth(lw); c.setLineCap(0)
    c.line(X(x0), Y(y), X(x1), Y(y))

def tick(c, pts, idx, length_mm=4.5):
    (x0,y0),(x1,y1),(x2,y2) = pts[idx-1], pts[idx], pts[idx+1]
    dx, dy = x2-x0, y2-y0; L = math.hypot(dx, dy); nx, ny = -dy/L, dx/L; h = length_mm/2
    polyline(c, [(x1-nx*h, y1-ny*h), (x1+nx*h, y1+ny*h)], 2.5)

def tick_seg(c, p, q, t, length_mm=4.5):
    (x0,y0),(x1,y1) = p, q; dx, dy = x1-x0, y1-y0; L = math.hypot(dx, dy); nx, ny = -dy/L, dx/L; h = length_mm/2
    mx, my = x0+t*dx, y0+t*dy
    polyline(c, [(mx-nx*h, my-ny*h), (mx+nx*h, my+ny*h)], 2.5)

def coord_label(c, lat, lon, dx, dy):                # native placement: right-aligned, to the left of the dot, two mono lines
    text(c, lat, dx-4.5, dy-2.5, 'Mono', 8.5, 'r', tracking=0.04)
    text(c, lon, dx-4.5, dy+0.9, 'Mono', 8.5, 'r', tracking=0.04)

def dot(c, x, y, r=3.0):
    c.setFillColor(WHITE); c.circle(X(x), Y(y), r, stroke=0, fill=1)

# ================= overlay: GRAPHICS =================
def draw_graphics(c):
    c.saveState()
    polygon(c, ORANGE_POLY, PANT)
    polyline(c, LINE, 3.5)
    # vertex dots on the surveyed corners (3-5 mm off folds), as on the 1 kg
    for p in DOTS: dot(c, *p)
    for (p, q, t) in TICKS: tick_seg(c, p, q, t)
    for (dx, dy), lat, lon in COORDS: coord_label(c, lat, lon, dx, dy)

    # ---- back panel ----
    COL = 72.0; x0 = BACK_CX - COL/2
    y = 161.0
    for ln in HEAD:
        text(c, ln, BACK_CX, y, 'BigShouldersXB', 16, 'c', tracking=0.05); y += 16.5/PT
    y = y - 16.5/PT + 10.0
    text(c, HEAD2, BACK_CX, y, 'BigShouldersXB', 25, 'c', tracking=0.05)
    y += 6.8
    text(c, QUESTION, BACK_CX, y, 'BigShouldersXB', 11.5, 'c', tracking=0.03)
    rule(c, BACK_CX-6.5, BACK_CX+6.5, y+4.8, 0.4)
    y += 12.0
    BODY_PT, BODY_LEAD = 9.5, 13.2
    for ln in COUPLET:
        text(c, ln, x0, y, 'Archivo', BODY_PT, 'l'); y += BODY_LEAD/PT
    y += 2.4
    for para in BODY:
        last, n = paragraph(c, para, x0, COL, y, 'Archivo', BODY_PT, BODY_LEAD/PT)
        y = last + BODY_LEAD/PT + 4/PT
    y += 2.4
    last, n = paragraph(c, PROOF, x0, COL, y, 'ArchivoM', BODY_PT, BODY_LEAD/PT)
    y = 250.4
    rule(c, BACK_CX-6.5, BACK_CX+6.5, y-4.6, 0.4)
    assert last + 5 <= y, ('story runs into the footer', last)
    for ln in LEGAL:
        text(c, ln, BACK_CX, y, 'Mono', 6, 'c', tracking=0.02); y += 3.0
    assert y - 2.7 <= BOT - 8, ('legal block too low', y)

    # ---- front: weight mark ----
    text(c, '250G', LEFT-12.5, BOT-8.5, 'Mono', 8, 'r', tracking=0.10)

    # ---- side 1: proposition, above the native line (which runs ~145-152 here) ----
    y = 107.0
    for ln in SIDE1:
        text(c, ln, LEFT+8.5, y, 'BigShouldersXB', 18, 'l', tracking=0.02); y += 6.9
    rule(c, LEFT+8.5, LEFT+17.0, y-3.4, 0.5)
    for ln in SIDE1_SUB:
        text(c, ln, LEFT+8.5, y, 'Archivo', 5.6, 'l', tracking=0.12); y += 2.9

    # ---- side 2 lettering ----
    cap = 0.8*HOLD_PT/PT
    c.saveState(); c.translate(X(RIGHT_CX + cap/2), Y(HOLD_BOTTOM)); c.rotate(90)
    t = c.beginText(); t.setFont('BigShouldersXB', HOLD_PT); t.setCharSpace(-0.01*HOLD_PT); t.setWordSpace(0.12*HOLD_PT)
    t.setFillColor(WHITE); t.setTextOrigin(0, 0); t.textOut('HOLD THE LINE'); c.drawText(t)
    c.restoreState()
    text(c, 'NOFILTER.SG · NOFILTER.AE', RIGHT_CX, BOT-9.5, 'Archivo', 5.2, 'c', tracking=0.15)
    c.restoreState()

def draw_gusset(c):
    c.saveState(); c.setDash([])
    p = c.beginPath(); p.rect(X(FRONT-BLEED_MM), Y(GUS_BOT+BLEED_MM), (130+2*BLEED_MM)*PT, (70+BLEED_MM)*PT); c.clipPath(p, stroke=0, fill=0)
    tint = CMYKColorSep(0, 0.73, 0.87, 0, spotName='PANTONE 172 U', density=0.84)
    c.setStrokeColor(tint); c.setLineWidth(0.5); c.setLineJoin(1)
    for k in range(12):
        y0 = 268.0 + k*6.4
        pts = [(x, y0 + 2.2*math.sin(x/8.0 + k*1.7) + 1.4*math.sin(x/21.0 + k*0.9) + 0.8*math.sin(x/3.9 + k)) for x in range(54, 196, 2)]
        c.drawPath(path_from(c, pts), stroke=1, fill=0)
    cy = (BOT + GUS_BOT)/2                           # 304.1
    w = max(pdfmetrics.stringWidth(t, 'BigShoulders', 13) + 0.08*13*(len(t)-1) for t in GUSSET)/PT
    r = min(w*0.42, (130-2*7.5)/2 - 4)               # rules kept proportionate to the longer line, inside the safe area
    rule(c, GUS_CX-r, GUS_CX+r, cy-8.5)
    text(c, GUSSET[0], GUS_CX, cy-1.0, 'BigShoulders', 13, 'c', tracking=0.08)
    text(c, GUSSET[1], GUS_CX, cy+5.2, 'BigShoulders', 13, 'c', tracking=0.08)
    rule(c, GUS_CX-r, GUS_CX+r, cy+9.7)
    assert GUS_CX - w/2 >= FRONT + 7.5 and GUS_CX + w/2 <= FRONT + 130 - 7.5, ('gusset line too wide', w)
    c.restoreState()

# ================= overlay: NOTES =================
def draw_notes(c):
    c.saveState()
    x0, x1 = 502.3, 592.3
    rows = [("DATE:", datetime.date.today().strftime("%d/%m/%Y")), ("CLIENT:", "Alexander Clarke"),
            ("PROJECT:", "Hold The Line"), ("DIMENSIONS:", "400 mm x 200 mm + 70 mm gusset"), ("ITEM:", "250 g Bag"),
            ("VERSION:", "V2 dieline, build " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))]
    y = 83.0
    for lab, val in rows:
        text(c, lab, x0, y, 'Archivo', 9, 'l', color=BLACK)
        text(c, val, x1, y, 'Archivo', 9, 'r', color=BLACK)
        rule(c, x0, x1, y+3.8, 0.2, BLACK); y += 15.5
    y += 3
    text(c, "KEY COLOURS BREAKDOWN", (x0+x1)/2, y, 'Archivo', 9, 'c', color=BLACK)
    sy = y + 4.5
    c.setFillColor(PANT); c.rect(X(x0+22.1), Y(sy+11.1), 11.1*PT, 11.1*PT, stroke=0, fill=1)
    for (dx, dy, col) in ((0,0,CMYKColor(1,0,0,0)), (5.55,0,CMYKColor(0,1,0,0)), (0,5.55,CMYKColor(0,0,1,0)), (5.55,5.55,BLACK)):
        c.setFillColor(col); c.rect(X(x0+56.3+dx), Y(sy+dy+5.55), 5.55*PT, 5.55*PT, stroke=0, fill=1)
    text(c, "Pantone 172 U", x0+27.65, sy+15.4, 'Archivo', 6.5, 'c', color=BLACK)
    text(c, "CMYK", x0+61.85, sy+15.4, 'Archivo', 6.5, 'c', color=BLACK)
    y = sy + 20; rule(c, x0, x1, y, 0.4, BLACK)
    for i, (col, lab) in enumerate(((DIE, "CUTTER (DO NOT PRINT)"), (DIMS, "DIMENSIONS (DO NOT PRINT)"), (BLD, "BLEED (DO NOT PRINT)"))):
        yy = y + 9.5 + i*10.5
        rule(c, x0+6, x0+33, yy-1.2, 1.0, col)
        text(c, lab, x1, yy, 'Archivo', 9, 'r', color=BLACK)
    y = y + 9.5 + 3*10.5
    for ln in ("Orange solids (back/far-side field, gusset incl. 84% tint contours, front logo panel) print PANTONE 172 U spot.",
               "Canopy and cleared-land photograph (front/side 1 and above the line) is one CMYK raster at 300 ppi.",
               "Boundary line, lettering and marks knock out to white. Bleed 3 mm. Fonts embedded: Big Shoulders",
               "Medium/Black, Archivo Regular/Medium, JetBrains Mono Regular. Built from NoFilter_250g_Bag_PRINT_NATIVEv1.ai."):
        text(c, ln, x0, y, 'Archivo', 6.5, 'l', color=BLACK); y += 3.4
    y += 4
    text(c, "VISUAL REFERENCE", x0, y, 'Archivo', 9, 'l', color=BLACK)
    if os.path.exists(REFIMG):
        from PIL import Image as _I; _iw, _ih = _I.open(REFIMG).size
        w = 105.0; h = w*_ih/_iw
        c.drawImage(REFIMG, X(x0-7.5), Y(y+4+h), w*PT, h*PT)
    c.restoreState()

def build_overlay():
    c = canvas.Canvas(OVERLAY, pagesize=(PW, PH))
    c.setTitle('overlay'); draw_graphics(c)
    c._code.append('/NFGUS BMC EMC')
    draw_gusset(c)
    c._code.append('/NFSPLIT BMC EMC')
    draw_notes(c)
    c.showPage(); c.save()

# ================= raster: 300 dpi CMYK crop of the TIF onto the native placement =================
BX0, BX1, BY0, BY1 = FRONT-BLEED_MM, FLAT_R+BLEED_MM, TOP-BLEED_MM, BOT+BLEED_MM     # bleed box of the body
IMG_PX_W, IMG_PX_H = int(round((BX1-BX0)*300/25.4)), int(round((BY1-BY0)*300/25.4))   # 300 ppi over 406 x 206 mm
def build_raster():
    if os.path.exists(RAW) and os.path.getsize(RAW) == IMG_PX_W*IMG_PX_H*4: return
    import numpy as np
    from PIL import Image
    Image.MAX_IMAGE_PIXELS = None
    a = np.asarray(Image.open(TIF)); assert a.shape[2] == 4
    # picture inside the TIF's white margins = rows 131:2581, cols 336:5137, placed by the native at IMG_X0..+IMG_W, IMG_Y0..IMG_Y1
    kx, ky = 4801/IMG_W, 2450/IMG_H
    c0, c1 = 336 + (BX0-IMG_X0)*kx, 336 + (BX1-IMG_X0)*kx
    r0, r1 = 131 + (BY0-IMG_Y0)*ky, 131 + (BY1-IMG_Y0)*ky
    crop = a[int(round(r0)):int(round(r1)), int(round(c0)):int(round(c1))]
    im = Image.fromarray(crop, 'CMYK').resize((IMG_PX_W, IMG_PX_H), Image.LANCZOS)
    px = np.asarray(im).copy(); S = 300/25.4
    # the clearing in the photograph pokes ~1 mm above the new line just right of the side-1/back fold: cover with canopy from above
    def line_y(x):
        for (x0, y0), (x1, y1) in zip(TOP_CHAIN, TOP_CHAIN[1:]):
            if x0 <= x <= x1: return y0 + (x-x0)/(x1-x0)*(y1-y0)
        return None
    orange = (px[..., 1] > 100) & (px[..., 2] > 100) & (px[..., 0] < 80)
    for c in range(int((BACK-BX0)*S), int((BACK+25-BX0)*S)):
        xm = BX0 + c/S; ly = line_y(xm)
        if ly is None: continue
        r1 = int((ly - 0.2 - BY0)*S); r0 = r1 - int(4*S)
        idx = np.where(orange[r0:r1, c])[0]
        if len(idx):
            top = r0 + idx[0] - int(0.4*S)
            px[top:r1, c] = px[top-int(7*S):r1-int(7*S), c]
    open(RAW, 'wb').write(px.tobytes()); print('raster', im.size)


def clone_cross(ops, i0, i1, src_c, size_src, dst_c, size_mm, deg, PT, AH):
    """Clone the native cross (a native path group q..Q) scaled, rotated and moved to dst_c (mm from top-left)."""
    import copy as _c
    from pypdf.generic import FloatObject
    s = size_mm/size_src; th = math.radians(deg)
    a, b_, c_, d = s*math.cos(th), s*math.sin(th), -s*math.sin(th), s*math.cos(th)
    C0x, C0y = src_c[0]*PT, (AH-src_c[1])*PT
    Cx, Cy   = dst_c[0]*PT, (AH-dst_c[1])*PT
    out = []
    for i in range(i0, i1):
        args, op = ops[i]
        if op == b'cm':
            tx, ty = float(args[4]), float(args[5])
            vx, vy = tx-C0x, ty-C0y
            args = [FloatObject(a), FloatObject(b_), FloatObject(c_), FloatObject(d),
                    FloatObject(a*vx + c_*vy + Cx), FloatObject(b_*vx + d*vy + Cy)]
        out.append((_c.deepcopy(args), op))
    return [([], b'q'), ([FloatObject(0),FloatObject(0),FloatObject(0),FloatObject(0)], b'k')] + out + [([], b'Q')]

# ================= composition =================
def block_bounds(ops, layer):
    i = next(i for i,(args,op) in enumerate(ops) if op==b'BDC' and args and str(args[1])==layer)
    j = next(j for j in range(i+1, len(ops)) if ops[j][1]==b'EMC')
    return i, j

def check_balanced(ops, idxs):
    q = sum(1 for i in idxs if ops[i][1]==b'q'); Q = sum(1 for i in idxs if ops[i][1]==b'Q')
    assert q==Q, ('unbalanced q/Q in deletions', q, Q)

def main():
    build_overlay(); build_raster()
    reader = PdfReader(NATIVE)
    src = reader.pages[0]
    if '/PieceInfo' in src: del src[NameObject('/PieceInfo')]
    writer = PdfWriter(); writer.pdf_header = b'%PDF-1.6'
    writer.add_page(src)
    writer._root_object[NameObject('/OCProperties')] = reader.trailer['/Root']['/OCProperties'].clone(writer)
    page = writer.pages[0]
    if '/LastModified' in page: del page[NameObject('/LastModified')]

    cs = ContentStream(page.get_contents(), writer); ops = cs.operations
    # photo placement -> the bleed box (the re-cropped raster fills it exactly)
    assert ops[3][1]==b'cm' and ops[4][1]==b'Do'
    ops[3] = ([FloatObject((BX1-BX0)*PT), FloatObject(0), FloatObject(0), FloatObject((BY1-BY0)*PT), FloatObject(BX0*PT), FloatObject((AH-BY1)*PT)], b'cm')
    # the front tongue: start the line just above the gusset fold instead of running 2.5 mm onto the gusset
    ox, oy = 236.7316, 296.9463
    assert ops[1028][1]==b'm' and ops[1029][1]==b'l'
    x0_, y0_ = (float(ops[1028][0][0])+ox)/PT, (PH-float(ops[1028][0][1])-oy)/PT
    x1_, y1_ = (float(ops[1029][0][0])+ox)/PT, (PH-float(ops[1029][0][1])-oy)/PT
    assert abs(x0_-83.5) < 0.2 and abs(y0_-271.6) < 0.2
    ys = BOT - 0.8; t = (y0_-ys)/(y0_-y1_); xs = x0_ + t*(x1_-x0_)
    ops[1028] = ([FloatObject(xs*PT-ox), FloatObject(PH-ys*PT-oy)], b'm')
    # gusset field: the native rectangle starts 2.5 mm below the fold (271.6), leaving a strip of photograph on the gusset; run it up to the fold
    assert ops[30][1]==b're' and ops[31][1]==b'f'
    ops[30] = ([FloatObject((FRONT-BLEED_MM)*PT), FloatObject((AH-(GUS_BOT+BLEED_MM))*PT), FloatObject((130+2*BLEED_MM)*PT), FloatObject((GUS_BOT+BLEED_MM-BOT)*PT)], b're')
    # sanity anchors
    assert ops[11][1]==b'q' and ops[28][1]==b'f' and ops[29][1]==b'Q'          # back orange polygon
    assert ops[37][1]==b'q' and ops[42][1]==b'Q'                                # back rule
    assert ops[43][1]==b'q' and ops[65][1]==b'Q' and ops[66][1]==b'Q'           # sticker window
    assert ops[71][1]==b're' and ops[72][1]==b'f' and ops[75][1]==b'q' and ops[267][1]==b'Q'   # side-1 logo
    assert ops[268][1]==b'q' and ops[458][1]==b'Q'                              # side-2 HOLD THE LINE glyphs
    assert ops[659][1]==b'q' and ops[683][1]==b'Q'                              # back dots
    assert ops[691][1]==b'q' and ops[720][1]==b'Q'                              # back ticks
    assert ops[723][1]==b'q' and ops[806][1]==b'Q'                              # back cross
    assert ops[807][1]==b'q' and ops[1019][1]==b'Q'                             # outlined "250 g"
    assert ops[1430][1]==b'BT' and ops[1444][1]==b'ET' and ops[1431][1]==b'cs' and ops[1432][1]==b'scn'
    assert ops[1493][1]==b'ET' and ops[1494][1]==b'BT' and ops[1513][1]==b'ET'
    dele = set()
    assert ops[709][1]==b'q' and ops[714][1]==b'Q' and ops[715][1]==b'q' and ops[716][1]==b'cm' and ops[719][1]==b'S' and ops[720][1]==b'Q'
    for a, b in [(11,29),(37,42),(43,66),(71,72),(75,267),(268,458),(709,720),(723,806),(807,1019),
                 (1430,1430),(1433,1444),(1445,1493)]:
        dele.update(range(a, b+1))
    # Notes layer content
    i, j = block_bounds(ops, '/MC3'); k = i+1
    while ops[k][1]==b'Q': k += 1
    dele.update(range(k, j))
    # the line: cut at the top of the last riser (341.6, 101.8); the native's crest and climb to the corner (1086-1088) go
    assert ops[1085][1]==b'l' and ops[1088][1]==b'l' and ops[1089][1]==b'S'
    ex, ey = (float(ops[1085][0][0])+ox)/PT, (PH-float(ops[1085][0][1])-oy)/PT
    assert abs(ex-NATIVE_APEX[0]) < 0.15 and abs(ey-NATIVE_APEX[1]) < 0.15, (ex, ey)
    ops[1085] = ([FloatObject(NATIVE_CUT[0]*PT-ox), FloatObject(PH-NATIVE_CUT[1]*PT-oy)], b'l')
    dele.update(range(1086, 1089))
    # the second coordinate dot and its label sat on the removed crest: move them onto the new descent
    ddx, ddy = NEW_DOT[0]-NATIVE_DOT[0], NEW_DOT[1]-NATIVE_DOT[1]
    for i in range(674, 682):
        if ops[i][1]==b'cm': ops[i] = (ops[i][0][:4] + [FloatObject(float(ops[i][0][4]) + ddx*PT), FloatObject(float(ops[i][0][5]) - ddy*PT)], b'cm')
    for i in range(1494, 1505):
        if ops[i][1]==b'Tm': ops[i] = (ops[i][0][:4] + [FloatObject(float(ops[i][0][4]) + ddx*PT), FloatObject(float(ops[i][0][5]) - ddy*PT)], b'Tm')
    check_balanced(ops, dele)
    # clone the cross onto side 2, scaled to 8 mm, above the lettering
    cross = []
    for i in range(723, 807):
        args, op = ops[i]
        if op==b'cm':
            sc = 8.0/18.1; cx, cy = 370.25*PT, (AH-107.05)*PT
            tx, ty = float(args[4]), float(args[5])
            args = [FloatObject(sc), FloatObject(0), FloatObject(0), FloatObject(sc),
                    FloatObject(cx + sc*(tx-cx) + (RIGHT_CX-370.25)*PT), FloatObject(cy + sc*(ty-cy) + (107.05-CROSS_Y)*PT)]
        cross.append((copy.deepcopy(args), op))
    cross = [([], b'q'), ([FloatObject(0),FloatObject(0),FloatObject(0),FloatObject(0)], b'k')] + cross + [([], b'Q')]
    # front ticks: square each to the boundary at its point
    verts = []
    for i in range(1028, 1086):
        a, op = ops[i]
        if op in (b'm', b'l'): verts.append((float(a[0])+ox, float(a[1])+oy))
        elif op == b'c': verts.append((float(a[4])+ox, float(a[5])+oy))
        elif op in (b'v', b'y'): verts.append((float(a[2])+ox, float(a[3])+oy))
    def foot_and_normal(px, py):
        best = None
        for (x1, y1), (x2, y2) in zip(verts, verts[1:]):
            dx, dy = x2-x1, y2-y1; L2 = dx*dx+dy*dy
            if L2 == 0: continue
            t = max(0.0, min(1.0, ((px-x1)*dx+(py-y1)*dy)/L2)); fx, fy = x1+t*dx, y1+t*dy
            d = (px-fx)**2+(py-fy)**2
            if best is None or d < best[0]: best = (d, fx, fy, -dy/L2**0.5, dx/L2**0.5)
        return best[1:]
    for cm_i in (692, 698, 704, 1100, 1106, 1112, 1118, 1124, 1130, 1136, 1142):    # back ticks + front ticks
        a_cm, op_cm = ops[cm_i]; a_l, op_l = ops[cm_i+2]
        assert op_cm==b'cm' and ops[cm_i+1][1]==b'm' and op_l==b'l' and ops[cm_i+3][1]==b'S', cm_i
        tx, ty = float(a_cm[4]), float(a_cm[5]); ex_, ey_ = float(a_l[0]), float(a_l[1])
        cx, cy = tx+ex_/2, ty+ey_/2
        fx, fy, nx, ny = foot_and_normal(cx, cy); h = 3.4*PT/2
        ops[cm_i] = ([FloatObject(1),FloatObject(0),FloatObject(0),FloatObject(1),FloatObject(fx-nx*h),FloatObject(fy-ny*h)], b'cm')
        ops[cm_i+2] = ([FloatObject(2*nx*h), FloatObject(2*ny*h)], b'l')
    kept = [o for i,o in enumerate(ops) if i not in dele]
    cs.operations = kept; page.replace_contents(cs)

    # merge overlay, relocate into layers
    ov = PdfReader(OVERLAY).pages[0]
    page.merge_page(ov)
    ops_native = list(ops)
    cs = ContentStream(page.get_contents(), writer); ops = cs.operations
    assert ops[0][1]==b'q'
    depth=0; close_native=None
    for i,(a,op) in enumerate(ops):
        if op==b'q': depth+=1
        elif op==b'Q':
            depth-=1
            if depth==0: close_native=i; break
    native = ops[1:close_native]; appended = ops[close_native+1:]
    assert appended[0][1]==b'q' and appended[-1][1]==b'Q'
    inner = appended[1:-1]; k = 0
    while k < len(inner) and inner[k][1] in (b're', b'W', b'n', b'cm'): k += 1
    inner = inner[k:]
    gus   = next(i for i,(a,op) in enumerate(inner) if op==b'BMC' and a and str(a[0])=='/NFGUS')
    split = next(i for i,(a,op) in enumerate(inner) if op==b'BMC' and a and str(a[0])=='/NFSPLIT')
    graphics = [([], b'q')] + inner[:gus] + [([], b'Q')]
    gusset   = [([], b'q')] + inner[gus+2:split] + [([], b'Q')]
    # the mark, square, under the gusset line
    gusset  += clone_cross(ops_native, 723, 807, (370.25, 107.05), 18.1, (GUS_CX, 321.5), 7.5, 0.0, PT, AH)
    notes    = [([], b'q')] + inner[split+2:] + [([], b'Q')]
    gi, gj = block_bounds(native, '/MC1')
    native = native[:gi+1] + graphics + cross + native[gi+1:gj] + gusset + native[gj:]
    ni, nj = block_bounds(native, '/MC3')
    native = native[:nj] + notes + native[nj:]
    cs.operations = native; page.replace_contents(cs)

    # swap the photo: 300 ppi CMYK, same placement
    im0 = page['/Resources']['/XObject']['/Im0'].get_object()
    raw = open(RAW, 'rb').read(); assert len(raw) == IMG_PX_W*IMG_PX_H*4
    im0._data = zlib.compress(raw, 6); im0.decoded_self = None
    im0[NameObject('/Filter')] = NameObject('/FlateDecode')
    if '/DecodeParms' in im0: del im0[NameObject('/DecodeParms')]
    im0[NameObject('/Width')] = NumberObject(IMG_PX_W); im0[NameObject('/Height')] = NumberObject(IMG_PX_H)
    im0[NameObject('/BitsPerComponent')] = NumberObject(8)
    im0[NameObject('/ColorSpace')] = page['/Resources']['/ColorSpace']['/CS2']      # the native's ICC CMYK (N=4)
    print('embedded 300 ppi CMYK raster')
    # spot colours -> the native's Separation objects
    natcs = {str(v.get_object()[1]): v for k, v in reader.pages[0]['/Resources']['/ColorSpace'].items() if isinstance(v.get_object(), ArrayObject) and str(v.get_object()[0])=='/Separation'}
    csd = page['/Resources']['/ColorSpace']
    for k in list(csd.keys()):
        v = csd[k].get_object()
        if isinstance(v, ArrayObject) and str(v[0])=='/Separation' and str(v[1]) in natcs:
            csd[NameObject(k)] = natcs[str(v[1])].clone(writer)
    # metadata / PDF-X-4
    if '/Metadata' in writer._root_object: del writer._root_object[NameObject('/Metadata')]
    import datetime as _dt, uuid, hashlib
    from pypdf.generic import DecodedStreamObject, ByteStringObject
    ICC = '/usr/share/texlive/texmf-dist/tex/generic/colorprofiles/FOGRA39L_coated.icc'
    if not os.path.exists(ICC): ICC = os.path.join(HERE, '..', 'icc', 'FOGRA39L_coated.icc')
    icc = DecodedStreamObject(); icc.set_data(open(ICC, 'rb').read()); icc[NameObject('/N')] = NumberObject(4)
    icc_ref = writer._add_object(icc)
    oi = DictionaryObject({NameObject('/Type'): NameObject('/OutputIntent'), NameObject('/S'): NameObject('/GTS_PDFX'),
        NameObject('/OutputConditionIdentifier'): TextStringObject('FOGRA39'), NameObject('/RegistryName'): TextStringObject('http://www.color.org'),
        NameObject('/OutputCondition'): TextStringObject('Offset printing, ISO 12647-2:2004, paper type 1/2 (ISO Coated v2 / FOGRA39)'),
        NameObject('/Info'): TextStringObject('ISO Coated v2 (ECI) / FOGRA39L'), NameObject('/DestOutputProfile'): icc_ref})
    writer._root_object[NameObject('/OutputIntents')] = ArrayObject([writer._add_object(oi)])
    if '/ArtBox' in page: del page[NameObject('/ArtBox')]
    now = _dt.datetime.now().astimezone(); iso = now.strftime('%Y-%m-%dT%H:%M:%S%z'); iso = iso[:-2] + ':' + iso[-2:]
    docid = 'uuid:' + str(uuid.uuid4())
    xmp = f"""<?xpacket begin="﻿" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about="" xmlns:pdfxid="http://www.npes.org/pdfx/ns/id/" pdfxid:GTS_PDFXVersion="PDF/X-4"/>
<rdf:Description rdf:about="" xmlns:pdf="http://ns.adobe.com/pdf/1.3/" pdf:Producer="NoFilter build_250.py (pypdf, reportlab)" pdf:Trapped="False"/>
<rdf:Description rdf:about="" xmlns:xmp="http://ns.adobe.com/xap/1.0/" xmp:CreateDate="{iso}" xmp:ModifyDate="{iso}" xmp:MetadataDate="{iso}" xmp:CreatorTool="NoFilter build_250.py"/>
<rdf:Description rdf:about="" xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/" xmpMM:DocumentID="{docid}" xmpMM:InstanceID="{docid}" xmpMM:RenditionClass="default"/>
<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title><rdf:Alt><rdf:li xml:lang="x-default">NoFilter 250 g Bag Dieline V2</rdf:li></rdf:Alt></dc:title><dc:format>application/pdf</dc:format></rdf:Description>
</rdf:RDF></x:xmpmeta>
<?xpacket end="w"?>"""
    meta = DecodedStreamObject(); meta.set_data(xmp.encode('utf-8'))
    meta[NameObject('/Type')] = NameObject('/Metadata'); meta[NameObject('/Subtype')] = NameObject('/XML')
    writer._root_object[NameObject('/Metadata')] = writer._add_object(meta)
    writer.add_metadata({'/GTS_PDFXVersion': 'PDF/X-4', '/Trapped': '/False', '/Title': 'NoFilter 250 g Bag Dieline V2',
                         '/Creator': 'NoFilter build_250.py (from NoFilter_250g_Bag_PRINT_NATIVEv1.ai)',
                         '/Subject': 'Hold The Line 250 g bag, 400 x 200 mm + 70 mm gusset, 3 mm bleed'})
    writer._info[NameObject('/Trapped')] = NameObject('/False')
    h = hashlib.md5((docid + iso).encode()).digest()
    writer._ID = ArrayObject([ByteStringObject(h), ByteStringObject(h)])
    with open(OUT, 'wb') as f: writer.write(f)
    print('wrote', OUT, os.path.getsize(OUT)//1_000_000, 'MB')
    print('HOLD_TOP %.1f' % HOLD_TOP); print('LINE', LINE)

if __name__ == '__main__':
    main()
