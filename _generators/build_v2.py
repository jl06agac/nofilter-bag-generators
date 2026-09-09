#!/usr/bin/env python3
"""NoFilter 1 kg bag — dieline V2.
Front + left side lifted verbatim from NoFilter_1kg_Bag_NATIVEV1.ai (PDF-compatible stream).
Back, right side, bottom gusset and spec block rebuilt; boundary line made contiguous.
Output: ../NoFilter_1kg_Bag_DIELINE_V2.pdf  (single source of truth for V2; edit this script, rerun)."""
import os, math, copy, datetime
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
NATIVE = os.path.join(HERE, '..', 'NoFilter_1kg_Bag_NATIVEV1.ai')
OUT    = os.path.join(HERE, '..', 'NoFilter_1kg_Bag_DIELINE_V2.pdf')
OVERLAY= os.path.join(HERE, 'overlay.pdf')
REFIMG = os.path.join(HERE, 'v2-ref-cmyk.jpg')
RAW    = os.path.join(HERE, 'im0-v2.raw')     # extended canopy/clearing raster from raster_v2.py (9064x6072 CMYK)

PT = 72/25.4
PW, PH = 2275.33, 1501.33
AH = PH/PT                       # artboard height, mm
def X(x): return x*PT            # mm (from left) -> pt
def Y(y): return (AH - y)*PT     # mm (from top)  -> pt

# ---- die geometry (mm, from the native's BLEED / Die Cut layers) ----
TOP, BOT = 60.9, 385.9           # bag body
GUS_BOT  = 480.9                 # bottom gusset (under the front)
FRONT, LEFT, BACK, RIGHT = 123.5, 273.5, 368.5, 518.5
FLAT_R = 613.5
BLEED_MM = 3.0
BACK_CX = BACK + 75.0            # 443.5
RIGHT_CX = RIGHT + 47.5          # 566.0
GUS_CX = FRONT + 75.0            # 198.5

# ---- fonts ----
rl_config.canvas_basefontname = 'Archivo'
pdfmetrics.registerFont(TTFont('BigShoulders', os.path.join(HERE, 'fonts/BigShoulders-Medium.ttf')))
pdfmetrics.registerFont(TTFont('BigShouldersXB', os.path.join(HERE, 'fonts/BigShoulders-Black.ttf')))
pdfmetrics.registerFont(TTFont('ArchivoM',      os.path.join(HERE, 'fonts/Archivo-Medium.ttf')))
pdfmetrics.registerFont(TTFont('Archivo',      os.path.join(HERE, 'fonts/Archivo-Regular.ttf')))
pdfmetrics.registerFont(TTFont('Mono',         os.path.join(HERE, 'fonts/JetBrainsMono-Regular.ttf')))

WHITE = CMYKColor(0, 0, 0, 0)
BLACK = CMYKColor(0, 0, 0, 1)
PANT  = CMYKColorSep(0, 0.73, 0.87, 0, spotName='PANTONE 172 U')
DIE   = CMYKColorSep(1, 0, 0, 0, spotName='Die cut')
DIMS  = CMYKColorSep(0, 1, 0, 0, spotName='DIMENSIONS')
BLD   = CMYKColorSep(0, 0, 1, 0, spotName='BLEED')

# ---- the contiguous boundary: picks up where the native front/left-side path starts (367.8, 227.9) ----
# surveyed line across the back: sharp rise, short plateau, dip, second rise, then an easing descent across the far side
# back panel: quiet entry -> small shoulder with one inflection -> deliberate rise -> broad, irregular crest at u=0.68
# -> clear descent inside the panel -> a resolved low shoulder carrying into the fold. Ten segments, no repeated slopes.
L_BACK = [(367.8,227.9),(374.5,226.9),(378.5,228.0),(400.0,200.5),(414.0,198.5),(430.0,191.0),
          (436.0,189.5),(468.0,187.5),(484.0,196.0),(506.0,218.5),(518.5,222.0)]
BACK_TICKS = [((378.5,228.0),(400.0,200.5),0.5), ((484.0,196.0),(506.0,218.5),0.5)]
# the far side: a short near-flat shoulder just inside the panel, a decisive drop straight through the T, then a last irregular fall to the edge
L_RIGHT= [(518.5,222.0),(527.0,225.0),(542.0,227.0),(557.0,242.0),(570.0,260.5),(592.0,267.5),(605.0,280.0),
          (FLAT_R+BLEED_MM,285.0)]                 # diagonal through the T, with surveyed jogs on the way down
LINE = L_BACK + L_RIGHT[1:]
ORANGE_POLY = LINE + [(FLAT_R+BLEED_MM, BOT+BLEED_MM), (367.8, BOT+BLEED_MM)]

# ---- copy ----
HEAD = ["MOST COFFEE BEGINS WITH", "PRICE AND TASTE."]
HEAD2 = "WE BEGIN WITH PLACE."
FOREST = CMYKColor(0.80, 0.48, 0.72, 0.62)          # deep canopy green sampled from the photograph (CMYK build, no new plate)
QUESTION = "Where can your cuppa do the most good?"
COUPLET = ["Grown one way, coffee can clear forest.", "Grown another, it can help keep forest standing."]
BODY = [
 "NoFilter partners exclusively with conservation NGOs and local farming communities on the edges of some of the world\u2019s most threatened forests, home to some of its rarest wildlife.",
 "We back the agroforestry coffee grown there, build the market behind it, and keep coming back for more.",
]
PROOF = "That\u2019s why a share of every sale goes straight back to conservation in the same landscape."
CLOSE = ["GOOD COFFEE.", "PUT TO BETTER USE."]
SIDE1 = ["COFFEE FROM", "FORESTS", "STILL STANDING."]
SIDE1_SUB = ["BETTER COFFEE", "STRONGER COMMUNITIES", "HEALTHIER FORESTS"]
ICONS = [("leaf",   ["FORESTS", "PEOPLE", "WILDLIFE"]),
         ("people", ["STRONGER", "COMMUNITIES"]),
         ("sun",    ["BRIGHTER", "FUTURES"])]
LEGAL = ["NoFilter Pte. Ltd.",
         "31 Kaki Bukit Road 3, #01-02C, TechLink, Singapore 417818",
         "UEN 201839882N \u00b7 hello@nofilter.sg"]
RIGHT_SMALL = ["FORESTS", "PEOPLE", "WILDLIFE", "A BRIGHTER FUTURE"]
GUSSET = ["IF YOU CAN READ THIS,", "YOU\u2019RE OUT OF COFFEE."]

# ================= drawing helpers =================
def text(c, s, x, y, font, size, align='l', tracking=0.0, color=WHITE):
    cs = tracking*size
    w = pdfmetrics.stringWidth(s, font, size) + cs*(len(s)-1)
    x0 = X(x) - (w/2 if align=='c' else w if align=='r' else 0)
    t = c.beginText(); t.setFont(font, size); t.setCharSpace(cs); t.setFillColor(color)
    t.setTextOrigin(x0, Y(y)); t.textOut(s); c.drawText(t)
    return w/PT

def paragraph(c, txt, x0, width_mm, y_first, font, size, leading_mm, ragged=False):
    """Justified, last line centred (as the native)."""
    W = width_mm*PT; words = txt.split(' ')
    # minimum-raggedness line breaking (sum of squared slack, last line free) so justified gaps stay even
    n = len(words); sp = pdfmetrics.stringWidth(' ', font, size)
    wl = [pdfmetrics.stringWidth(w, font, size) for w in words]
    INF = float('inf'); best = [INF]*(n+1); brk = [0]*(n+1); best[0] = 0
    for j in range(1, n+1):
        width = -sp
        for i in range(j-1, -1, -1):
            width += wl[i] + sp
            if width > W and i < j-1: break
            slack = W - width
            cost = best[i] + (0.35*slack*slack if j == n else slack*slack)   # last line weighted too, so no orphans
            if cost < best[j]: best[j], brk[j] = cost, i
    lines = []; j = n
    while j > 0: lines.insert(0, words[brk[j]:j]); j = brk[j]
    y = y_first
    short = len(lines) <= 2
    for i, ln in enumerate(lines):
        s = ' '.join(ln); sw = pdfmetrics.stringWidth(s, font, size)
        t = c.beginText(); t.setFont(font, size); t.setFillColor(WHITE); t.setCharSpace(0)
        if ragged:
            t.setWordSpace(0); t.setTextOrigin(X(x0), Y(y))
        elif i < len(lines)-1 and not short:
            t.setWordSpace((W-sw)/max(1, len(ln)-1)); t.setTextOrigin(X(x0), Y(y))
        else:
            t.setWordSpace(0); t.setTextOrigin(X(x0)+(W-sw)/2, Y(y))
        t.textOut(s); c.drawText(t); y += leading_mm
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

def tick(c, pts, idx, length_mm=4.6):
    (x0,y0),(x1,y1),(x2,y2) = pts[idx-1], pts[idx], pts[idx+1]
    dx, dy = x2-x0, y2-y0; L = math.hypot(dx, dy); nx, ny = -dy/L, dx/L; h = length_mm/2
    polyline(c, [(x1-nx*h, y1-ny*h), (x1+nx*h, y1+ny*h)], 3.4)

def coord_label(c, lat, lon, dx, dy):
    c.setFillColor(WHITE); c.circle(X(dx), Y(dy), 4, stroke=0, fill=1)
    text(c, lat, dx-3.8, dy-5.5, 'Mono', 8, 'r', tracking=0.04)
    text(c, lon, dx-3.8, dy-1.5, 'Mono', 8, 'r', tracking=0.04)

def rule(c, x0, x1, y, lw=0.5, color=WHITE):
    c.setStrokeColor(color); c.setLineWidth(lw); c.setLineCap(0)
    c.line(X(x0), Y(y), X(x1), Y(y))

# ---- icons: white line art in an s×s mm box centred at (cx, cy) ----
def icon_leaf(c, cx, cy, s):
    c.setStrokeColor(WHITE); c.setLineWidth(0.75); c.setLineJoin(1); c.setLineCap(1)
    r = s/2*0.85
    p = c.beginPath()
    p.moveTo(X(cx-r), Y(cy+r))
    p.curveTo(X(cx-r), Y(cy-r*0.35), X(cx-r*0.35), Y(cy-r), X(cx+r), Y(cy-r))
    p.curveTo(X(cx+r), Y(cy+r*0.35), X(cx+r*0.35), Y(cy+r), X(cx-r), Y(cy+r))
    p.close(); c.drawPath(p, stroke=1, fill=0)
    p = c.beginPath(); p.moveTo(X(cx-r*0.85), Y(cy+r*0.85))
    p.curveTo(X(cx-r*0.2), Y(cy+r*0.2), X(cx+r*0.2), Y(cy-r*0.2), X(cx+r*0.75), Y(cy-r*0.75))
    c.drawPath(p, stroke=1, fill=0)

def icon_people(c, cx, cy, s):
    c.setStrokeColor(WHITE); c.setLineWidth(0.75); c.setLineJoin(1); c.setLineCap(1)
    for dx, dy, k in ((-0.30, 0.02, 0.85), (0.30, 0.02, 0.85), (0.0, -0.10, 1.0)):
        hx, hy = cx+dx*s, cy - s*0.18 + dy*s; hr = s*0.13*k
        c.circle(X(hx), Y(hy), hr*PT, stroke=1, fill=0)
        # shoulders: arc from left to right under the head
        w = s*0.30*k; top = hy + hr + s*0.06
        p = c.beginPath(); p.moveTo(X(hx-w), Y(top+s*0.30*k))
        p.curveTo(X(hx-w), Y(top+s*0.02), X(hx-w*0.55), Y(top), X(hx), Y(top))
        p.curveTo(X(hx+w*0.55), Y(top), X(hx+w), Y(top+s*0.02), X(hx+w), Y(top+s*0.30*k))
        c.drawPath(p, stroke=1, fill=0)

def icon_sun(c, cx, cy, s):
    c.setStrokeColor(WHITE); c.setLineWidth(0.75); c.setLineCap(1)
    r = s*0.22; c.circle(X(cx), Y(cy), r*PT, stroke=1, fill=0)
    for k in range(8):
        a = k*math.pi/4; r0, r1 = s*0.32, s*0.47
        c.line(X(cx+math.cos(a)*r0), Y(cy-math.sin(a)*r0), X(cx+math.cos(a)*r1), Y(cy-math.sin(a)*r1))

# ================= overlay: GRAPHICS (goes into the native's Graphics layer) =================
def draw_graphics(c):
    c.saveState()
    # orange field, back + right side: vector Pantone only when no extended raster exists
    polygon(c, ORANGE_POLY, PANT)
    # tone-on-tone contours over the back/far-side field (same plate, 94% tint), clipped to the field
    c.saveState(); c.clipPath(path_from(c, ORANGE_POLY, close=True), stroke=0, fill=0); c.setDash([])
    c.setStrokeColor(CMYKColorSep(0, 0.73, 0.87, 0, spotName='PANTONE 172 U', density=0.94)); c.setLineWidth(0.5); c.setLineJoin(1)
    for k in range(22):
        y0 = 176.0 + k*10.2
        pts = [(x, y0 + 3.4*math.sin(x/12.5 + k*1.9) + 2.3*math.sin(x/33.0 + k*0.7) + 1.2*math.sin(x/5.9 + k)) for x in range(366, 618, 2)]
        c.drawPath(path_from(c, pts), stroke=1, fill=0)
    c.restoreState()
    # the line itself
    polyline(c, LINE, 3.5)
    for (p, q, t) in BACK_TICKS:                                          # two survey ticks on the back, native weight, clear of both folds
        (ax, ay), (bx, by) = p, q; dx, dy = bx-ax, by-ay; L = math.hypot(dx, dy); nx, ny = -dy/L, dx/L; h = 4.6/2
        mx, my = ax+t*dx, ay+t*dy
        polyline(c, [(mx-nx*h, my-ny*h), (mx+nx*h, my+ny*h)], 3.4)
    for (vx, vy) in ((304.1,235.2),(345.3,228.4),(414.0,198.5),(468.0,187.5),(542.0,227.0),(592.0,267.5)):   # vertex dots, kept 3-5 mm off folds
        c.setFillColor(WHITE); c.circle(X(vx), Y(vy), 4, stroke=0, fill=1)

    # ---- back panel: the quiet editorial explanation. One left edge, one body size; no sign-off ----
    COL = 96.0; x0 = BACK_CX - COL/2                                          # body column, centred in the panel, text left-aligned
    y = 213.0 + 6.5                                                           # H2: setup, 23 pt
    for ln in HEAD:
        text(c, ln, BACK_CX, y, 'BigShouldersXB', 23, 'c', tracking=0.05); y += 24/PT
    y = y - 24/PT + 14.5                                                      # H1: hero, 36 pt, one line
    text(c, HEAD2, BACK_CX, y, 'BigShouldersXB', 36, 'c', tracking=0.05)
    y += 9.5                                                                  # H3: the question, same family, tight under the hero
    text(c, QUESTION, BACK_CX, y, 'BigShouldersXB', 17, 'c', tracking=0.03)
    rule(c, BACK_CX-9.0, BACK_CX+9.0, y+7.0, 0.5)                              # the one divider: closes the headline unit
    y += 17.0                                                                 # break into the story
    BODY_PT, BODY_LEAD = 13.0, 18.0
    for ln in COUPLET:
        text(c, ln, x0, y, 'Archivo', BODY_PT, 'l'); y += BODY_LEAD/PT
    y += 3.0
    for para in BODY:
        last, n = paragraph(c, para, x0, COL, y, 'Archivo', BODY_PT, BODY_LEAD/PT, ragged=True)
        y = last + BODY_LEAD/PT + 6/PT
    y += 3.0                                                                  # conclusion: 11.5 mm below the last paragraph, medium weight; the footer is what's detached
    last, n = paragraph(c, PROOF, x0, COL, y, 'ArchivoM', BODY_PT, BODY_LEAD/PT, ragged=True)
    y = 364.5                                                                 # legal footer at the foot (last line 14 mm above the cut)
    rule(c, BACK_CX-9.0, BACK_CX+9.0, y-6.5, 0.5)                             # matching hairline above the footer
    assert last + 7 <= y, ('story runs into the footer', last)
    for ln in LEGAL:
        text(c, ln, BACK_CX, y, 'Mono', 7, 'c', tracking=0.02); y += 3.7
    assert y - 3.4 <= BOT - 12, ('legal block too low', y)

    # ---- front: weight mark, mockup treatment (small mono, bottom right) ----
    text(c, '1KG', 253.0, 372.0, 'Mono', 11, 'r', tracking=0.10)

    # ---- side 1: proposition ----
    y = 184.0
    for ln in SIDE1:
        text(c, ln, LEFT+9.5, y, 'BigShouldersXB', 29, 'l', tracking=0.02); y += 11.2
    rule(c, LEFT+9.5, LEFT+23.5, y-5.5, 0.6)
    y += 0.0
    for ln in SIDE1_SUB:
        text(c, ln, LEFT+9.5, y, 'Archivo', 8.5, 'l', tracking=0.12); y += 4.4

    # ---- right side lettering: vertical, reading upwards, heavy ----
    size = 93; cap = 0.8*size/PT
    c.saveState(); c.translate(X(RIGHT_CX + cap/2), Y(305.0)); c.rotate(90)
    t = c.beginText(); t.setFont('BigShouldersXB', size); t.setCharSpace(-0.01*size); t.setWordSpace(0.12*size); t.setFillColor(WHITE); t.setTextOrigin(0, 0); t.textOut('HOLD THE LINE'); c.drawText(t)
    c.restoreState()
    text(c, 'NOFILTER.SG \u00b7 NOFILTER.AE', RIGHT_CX, 370.0, 'Archivo', 7, 'c', tracking=0.15)
    c.restoreState()

def draw_gusset(c):
    c.saveState(); c.setDash([])
    p = c.beginPath(); p.rect(X(FRONT-BLEED_MM), Y(GUS_BOT+BLEED_MM), (150+2*BLEED_MM)*PT, (95+BLEED_MM)*PT); c.clipPath(p, stroke=0, fill=0)
    tint = CMYKColorSep(0, 0.73, 0.87, 0, spotName='PANTONE 172 U', density=0.84)
    c.setStrokeColor(tint); c.setLineWidth(0.6); c.setLineJoin(1)
    for k in range(11):
        y0 = 384.0 + k*9.4
        pts = [(x, y0 + 3.2*math.sin(x/11.0 + k*1.7) + 2.1*math.sin(x/29.0 + k*0.9) + 1.1*math.sin(x/5.3 + k)) for x in range(118, 280, 2)]
        c.drawPath(path_from(c, pts), stroke=1, fill=0)
    w = max(pdfmetrics.stringWidth(t, 'BigShoulders', 20) + 0.08*20*(len(t)-1) for t in GUSSET)/PT
    r = min(w*0.42, (150-2*7.5)/2 - 6)               # rules kept proportionate to the longer line, inside the safe area
    rule(c, GUS_CX-r, GUS_CX+r, 419.5)
    text(c, GUSSET[0], GUS_CX, 431.0, 'BigShoulders', 20, 'c', tracking=0.08)
    text(c, GUSSET[1], GUS_CX, 440.5, 'BigShoulders', 20, 'c', tracking=0.08)
    rule(c, GUS_CX-r, GUS_CX+r, 447.5)
    assert GUS_CX - w/2 >= FRONT + 7.5 and GUS_CX + w/2 <= FRONT + 150 - 7.5, ('gusset line too wide', w)
    c.restoreState()

# ================= overlay: NOTES (spec block, non-printing area) =================
def draw_notes(c):
    c.saveState()
    x0, x1 = 677.6, 767.6
    rows = [("DATE:", datetime.date.today().strftime("%d/%m/%Y")), ("CLIENT:", "Alexander Clarke"),
            ("PROJECT:", "Hold The Line"), ("DIMENSIONS:", "490 mm x 325 mm"), ("ITEM:", "1 kg Bag"),
            ("VERSION:", "V2 dieline, build " + datetime.datetime.now().strftime("%d/%m/%Y %H:%M"))]
    y = 53.5
    for lab, val in rows:
        text(c, lab, x0, y, 'Archivo', 9, 'l', color=BLACK)
        text(c, val, x1, y, 'Archivo', 9, 'r', color=BLACK)
        rule(c, x0, x1, y+3.8, 0.2, BLACK); y += 15.5
    y += 3
    text(c, "KEY COLOURS BREAKDOWN", (x0+x1)/2, y, 'Archivo', 9, 'c', color=BLACK)
    sy = y + 4.5
    c.setFillColor(PANT); c.rect(X(699.7), Y(sy+11.1), 11.1*PT, 11.1*PT, stroke=0, fill=1)
    for (dx, dy, col) in ((0,0,CMYKColor(1,0,0,0)), (5.55,0,CMYKColor(0,1,0,0)), (0,5.55,CMYKColor(0,0,1,0)), (5.55,5.55,BLACK)):
        c.setFillColor(col); c.rect(X(733.9+dx), Y(sy+dy+5.55), 5.55*PT, 5.55*PT, stroke=0, fill=1)
    text(c, "Pantone 172 U", 705.25, sy+15.4, 'Archivo', 6.5, 'c', color=BLACK)
    text(c, "CMYK", 739.45, sy+15.4, 'Archivo', 6.5, 'c', color=BLACK)
    y = sy + 20; rule(c, x0, x1, y, 0.4, BLACK)
    for i, (col, lab) in enumerate(((DIE, "CUTTER (DO NOT PRINT)"), (DIMS, "DIMENSIONS (DO NOT PRINT)"), (BLD, "BLEED (DO NOT PRINT)"))):
        yy = y + 9.5 + i*10.5
        rule(c, x0+6, x0+33, yy-1.2, 1.0, col)
        text(c, lab, x1, yy, 'Archivo', 9, 'r', color=BLACK)
    y = y + 9.5 + 3*10.5
    for ln in ("Orange solids (back/far-side field, gusset incl. 90% tint contours, front logo panel) print PANTONE 172 U spot. Canopy and cleared-land",
               "texture (front/left side) are one CMYK raster (461 ppi); back field is solid PANTONE 172 U. Boundary line,",
               "lettering and marks knock out to white. Bleed 3 mm. Fonts embedded: Big Shoulders Medium,",
               "Archivo Regular, JetBrains Mono Regular. Built from NoFilter_1kg_Bag_NATIVEV1.ai."):
        text(c, ln, x0, y, 'Archivo', 6.5, 'l', color=BLACK); y += 3.4
    y += 4
    text(c, "VISUAL REFERENCE", x0, y, 'Archivo', 9, 'l', color=BLACK)
    if os.path.exists(REFIMG):
        from PIL import Image as _I; _iw, _ih = _I.open(REFIMG).size
        w = 123.7; h = w*_ih/_iw
        c.drawImage(REFIMG, X(662.5), Y(y+4+h), w*PT, h*PT)
    c.restoreState()

def build_overlay():
    c = canvas.Canvas(OVERLAY, pagesize=(PW, PH))
    c.setTitle('overlay'); draw_graphics(c)
    c._code.append('/NFGUS BMC EMC')            # marker: gusset part follows (goes to the END of the Graphics layer)
    draw_gusset(c)
    c._code.append('/NFSPLIT BMC EMC')          # marker: Notes part follows
    draw_notes(c)
    c.showPage(); c.save()


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

# ================= composition with the native =================
def op_ranges_to_delete(ops):
    """Objects on the back panel and in the Notes layer that V2 replaces (indices in the native stream)."""
    dele = set()
    for a, b in [(73,91),(105,107),(111,113),(117,119),(123,125),(136,141),(145,150),(153,173),
                 (184,199),(382,391),(392,430),(1360,1371),(1382,1384),(1116,1121),(1144,1145),(1153,1183),(1192,1215),(1219,1237),(1241,1255),(1259,1267),(1271,1279),(1283,1303),(1312,1337),(1346,1357),(206,289),(299,352),(356,379),(1130,1140),(1105,1115),(1021,1023)]:   # 1021-1023: native tick sitting on the gusset fold
        dele.update(range(a, b+1))
    # Notes layer: everything between its BDC and EMC
    i = next(i for i,(args,op) in enumerate(ops) if op==b'BDC' and args and str(args[1])=='/MC3')
    j = next(j for j in range(i+1, len(ops)) if ops[j][1]==b'EMC')
    k = i+1
    while ops[k][1]==b'Q': k += 1          # Illustrator closes the previous layer's q inside this block; keep it
    dele.update(range(k, j))
    # Illustrator sets the white fill (0 0 0 0 k) inside the first coordinate text block; everything after relies on it
    assert ops[154][1]==b'k' and [float(x) for x in ops[154][0]]==[0,0,0,0]
    dele.discard(154)
    return dele

def check_balanced(ops, idxs):
    q = sum(1 for i in idxs if ops[i][1]==b'q'); Q = sum(1 for i in idxs if ops[i][1]==b'Q')
    assert q==Q, ('unbalanced q/Q in deletions', q, Q)

def block_bounds(ops, layer):
    i = next(i for i,(args,op) in enumerate(ops) if op==b'BDC' and args and str(args[1])==layer)
    j = next(j for j in range(i+1, len(ops)) if ops[j][1]==b'EMC')
    return i, j

def main():
    build_overlay()
    reader = PdfReader(NATIVE)
    src = reader.pages[0]
    if '/PieceInfo' in src: del src[NameObject('/PieceInfo')]   # drop Illustrator private data (400 MB, would override the PDF art)
    writer = PdfWriter()
    writer.pdf_header = b'%PDF-1.6'
    writer.add_page(src)
    root_src = reader.trailer['/Root']
    writer._root_object[NameObject('/OCProperties')] = root_src['/OCProperties'].clone(writer)
    page = writer.pages[0]
    if '/LastModified' in page: del page[NameObject('/LastModified')]

    # 1) strip the objects V2 replaces
    cs = ContentStream(page.get_contents(), writer)
    ops = cs.operations
    dele = op_ranges_to_delete(ops); check_balanced(ops, dele)
    # sanity: the things we delete are what we think they are
    assert ops[73][1]==b'm' and ops[91][1]==b'f' and ops[184][1]==b'm' and ops[199][1]==b'S'
    assert ops[382][1]==b'BT' and ops[430][1]==b'ET' and ops[1360][1]==b'BT' and ops[1371][1]==b'ET'
    # 2) clone the back's white cross onto the right side (+95 mm)
    cross = []
    for i in range(206, 290):
        args, op = ops[i]
        if op==b'cm':                                                       # scale the native cross to 12 mm about its centre, move to (566, 98)
            sc = 12.0/18.1; cx, cy = 501.75*PT, (AH-161.05)*PT
            tx, ty = float(args[4]), float(args[5])
            args = [FloatObject(sc), FloatObject(0), FloatObject(0), FloatObject(sc),
                    FloatObject(cx + sc*(tx-cx) + (RIGHT_CX-501.75)*PT), FloatObject(cy + sc*(ty-cy) + (161.05-98.0)*PT)]
        cross.append((copy.deepcopy(args), op))
    assert ops[206][1]==b'q' and ops[289][1]==b'Q'
    cross = [([], b'q'), ([FloatObject(0),FloatObject(0),FloatObject(0),FloatObject(0)], b'k')] + cross + [([], b'Q')]
    # native boundary path (663-755): drop the tail that fences the bottom of side 1 (after the vertex at 273.2, 386.9)
    ox, oy = 1042.6019, 855.203; cut = None
    for i in range(663, 756):
        args, op = ops[i]
        if op in (b'l', b'm') and abs((float(args[0])+ox)/PT-273.2) < 0.3 and abs((PH-float(args[1])-oy)/PT-386.9) < 0.3: cut = i
    # the tongue's crossbar sits on the gusset fold and gets half-covered: lift its two vertices 2 mm onto the front
    for i in range(663, 756):
        args, op = ops[i]
        if op==b'l':
            X_, Y_ = (float(args[0])+ox)/PT, (PH-float(args[1])-oy)/PT
            if (abs(X_-157.6) < 0.3 and abs(Y_-386.2) < 0.3) or (abs(X_-182.1) < 0.3 and abs(Y_-385.2) < 0.3):
                ops[i] = ([args[0], FloatObject(PH - (383.8*PT) - oy)], op)
    assert cut is not None and ops[755][1]==b'S'
    # native front ticks (q cm m l S at 1001-1005, 1007-1011, 1013-1017, 1025-1029): square each to the boundary at its point
    verts = []
    for i in range(663, 756):
        a, op = ops[i]
        if op in (b'm', b'l'): verts.append(((float(a[0])+ox), (float(a[1])+oy)))          # PDF pts, y up
    def foot_and_normal(px, py):
        best = None
        for (x1, y1), (x2, y2) in zip(verts, verts[1:]):
            dx, dy = x2-x1, y2-y1; L2 = dx*dx+dy*dy
            if L2 == 0: continue
            t = max(0.0, min(1.0, ((px-x1)*dx+(py-y1)*dy)/L2)); fx, fy = x1+t*dx, y1+t*dy
            d = (px-fx)**2+(py-fy)**2
            if best is None or d < best[0]: best = (d, fx, fy, -dy/L2**0.5, dx/L2**0.5)
        return best[1:]
    for cm_i in (1002, 1008, 1014, 1026):
        a_cm, op_cm = ops[cm_i]; a_l, op_l = ops[cm_i+2]
        assert op_cm==b'cm' and ops[cm_i+1][1]==b'm' and op_l==b'l' and ops[cm_i+3][1]==b'S', cm_i
        tx, ty = float(a_cm[4]), float(a_cm[5]); ex, ey = float(a_l[0]), float(a_l[1])
        cx, cy = tx+ex/2, ty+ey/2                                             # tick centre
        fx, fy, nx, ny = foot_and_normal(cx, cy); h = 4.6*PT/2
        ops[cm_i] = ([FloatObject(1),FloatObject(0),FloatObject(0),FloatObject(1),FloatObject(fx-nx*h),FloatObject(fy-ny*h)], b'cm')
        ops[cm_i+2] = ([FloatObject(2*nx*h), FloatObject(2*ny*h)], b'l')
    dele.update(range(cut+1, 755))
    # ... and the notch at the side-1/back fold (vertices 664-667: down to 241 and back) so the line runs straight through
    assert all(ops[i][1]==b'l' for i in range(664, 668))
    dele.update(range(664, 668))
    kept = [o for i,o in enumerate(ops) if i not in dele]
    cs.operations = kept; page.replace_contents(cs)

    # 3) merge the overlay, then move its two parts into the Graphics and Notes layers
    ops_native = list(ops)
    ov = PdfReader(OVERLAY).pages[0]
    page.merge_page(ov)
    cs = ContentStream(page.get_contents(), writer); ops = cs.operations
    # pypdf wraps: [q, <native...>, Q, q, <clip re W n>, <overlay...>, Q]
    assert ops[0][1]==b'q'
    depth=0; close_native=None
    for i,(a,op) in enumerate(ops):
        if op==b'q': depth+=1
        elif op==b'Q':
            depth-=1
            if depth==0: close_native=i; break
    native = ops[1:close_native]
    appended = ops[close_native+1:]
    assert appended[0][1]==b'q' and appended[-1][1]==b'Q'
    inner = appended[1:-1]
    # drop pypdf's clip (re W n) at the start
    k = 0
    while k < len(inner) and inner[k][1] in (b're', b'W', b'n', b'cm'): k += 1
    inner = inner[k:]
    gus   = next(i for i,(a,op) in enumerate(inner) if op==b'BMC' and a and str(a[0])=='/NFGUS')
    split = next(i for i,(a,op) in enumerate(inner) if op==b'BMC' and a and str(a[0])=='/NFSPLIT')
    graphics = [([], b'q')] + inner[:gus] + [([], b'Q')]
    gusset   = [([], b'q')] + inner[gus+2:split] + [([], b'Q')]
    # the mark, square, under the gusset line
    gusset  += clone_cross(ops_native, 206, 290, (501.75, 161.05), 18.1, (GUS_CX, 459.5), 11.0, 0.0, PT, AH)
    notes    = [([], b'q')] + inner[split+2:] + [([], b'Q')]
    # insert: field + line + back/right text at the START of Graphics (native lettering paints over it);
    # gusset text at the END of Graphics (over the native gusset rectangle)
    gi, gj = block_bounds(native, '/MC2')
    native = native[:gi+1] + graphics + cross + native[gi+1:gj] + gusset + native[gj:]
    ni, nj = block_bounds(native, '/MC3')
    native = native[:nj] + notes + native[nj:]
    cs.operations = native; page.replace_contents(cs)

    # 3b) swap in the extended raster (same dimensions, same placement, lossless Flate)
    if os.path.exists(RAW):
        import zlib
        im0 = page['/Resources']['/XObject']['/Im0'].get_object()
        assert int(im0['/Width'])==9064 and int(im0['/Height'])==6072
        raw = open(RAW,'rb').read(); assert len(raw)==9064*6072*4
        im0._data = zlib.compress(raw, 6); im0.decoded_self = None          # bypass pypdf's decode-on-set (stream is 180 MB)
        im0[NameObject('/Filter')] = NameObject('/FlateDecode')
        if '/DecodeParms' in im0: del im0[NameObject('/DecodeParms')]
        print('embedded extended raster')
        sm = im0['/SMask'].get_object()
        import numpy as np
        alpha = np.frombuffer(sm.get_data(), dtype=np.uint8).reshape(6072, 9064).copy()
        Spx = 9064/499.4
        x0 = int(round((FRONT-BLEED_MM-119.6)*Spx)); x1 = int(round((FLAT_R+BLEED_MM-119.6)*Spx))
        y0 = int(round((TOP-BLEED_MM-56.2)*Spx));   y1 = int(round((BOT+BLEED_MM-56.2)*Spx))
        alpha[:, :x0] = 0; alpha[:, x1:] = 0; alpha[:y0, :] = 0; alpha[y1:, :] = 0
        sm._data = zlib.compress(alpha.tobytes(), 6); sm.decoded_self = None
        sm[NameObject('/Filter')] = NameObject('/FlateDecode')
        if '/DecodeParms' in sm: del sm[NameObject('/DecodeParms')]
        print('photo masked to bleed box')
    # 4) point the overlay's spot colours at the native's Separation objects (same swatch, same alternate)
    natcs = {str(v.get_object()[1]): v for k, v in reader.pages[0]['/Resources']['/ColorSpace'].items()}
    csd = page['/Resources']['/ColorSpace']
    for k in list(csd.keys()):
        v = csd[k].get_object()
        if isinstance(v, ArrayObject) and str(v[0])=='/Separation' and str(v[1]) in natcs:
            csd[NameObject(k)] = natcs[str(v[1])].clone(writer)
    # 5) metadata
    if '/Metadata' in writer._root_object: del writer._root_object[NameObject('/Metadata')]
    writer.add_metadata({'/Title': 'NoFilter 1 kg Bag — Dieline V2', '/Creator': 'NoFilter build_v2.py (from NoFilter_1kg_Bag_NATIVEV1.ai)', '/Subject': 'Hold The Line 1 kg bag, 490 x 325 mm + 95 mm gusset, 3 mm bleed'})
    # 6) PDF/X-4: output intent, identification, page boxes
    import datetime as _dt, uuid
    ICC = '/usr/share/texlive/texmf-dist/tex/generic/colorprofiles/FOGRA39L_coated.icc'
    from pypdf.generic import StreamObject, DecodedStreamObject
    icc = DecodedStreamObject(); icc.set_data(open(ICC, 'rb').read()); icc[NameObject('/N')] = NumberObject(4)
    icc_ref = writer._add_object(icc)
    oi = DictionaryObject({NameObject('/Type'): NameObject('/OutputIntent'), NameObject('/S'): NameObject('/GTS_PDFX'),
        NameObject('/OutputConditionIdentifier'): TextStringObject('FOGRA39'), NameObject('/RegistryName'): TextStringObject('http://www.color.org'),
        NameObject('/OutputCondition'): TextStringObject('Offset printing, ISO 12647-2:2004, paper type 1/2 (ISO Coated v2 / FOGRA39)'),
        NameObject('/Info'): TextStringObject('ISO Coated v2 (ECI) / FOGRA39L'), NameObject('/DestOutputProfile'): icc_ref})
    writer._root_object[NameObject('/OutputIntents')] = ArrayObject([writer._add_object(oi)])
    if '/ArtBox' in page: del page[NameObject('/ArtBox')]                 # PDF/X: TrimBox or ArtBox, never both
    now = _dt.datetime.now().astimezone(); iso = now.strftime('%Y-%m-%dT%H:%M:%S%z'); iso = iso[:-2] + ':' + iso[-2:]
    docid = 'uuid:' + str(uuid.uuid4())
    xmp = f"""<?xpacket begin="\ufeff" id="W5M0MpCehiHzreSzNTczkc9d"?>
<x:xmpmeta xmlns:x="adobe:ns:meta/"><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">
<rdf:Description rdf:about="" xmlns:pdfxid="http://www.npes.org/pdfx/ns/id/" pdfxid:GTS_PDFXVersion="PDF/X-4"/>
<rdf:Description rdf:about="" xmlns:pdf="http://ns.adobe.com/pdf/1.3/" pdf:Producer="NoFilter build_v2.py (pypdf, reportlab)" pdf:Trapped="False"/>
<rdf:Description rdf:about="" xmlns:xmp="http://ns.adobe.com/xap/1.0/" xmp:CreateDate="{iso}" xmp:ModifyDate="{iso}" xmp:MetadataDate="{iso}" xmp:CreatorTool="NoFilter build_v2.py"/>
<rdf:Description rdf:about="" xmlns:xmpMM="http://ns.adobe.com/xap/1.0/mm/" xmpMM:DocumentID="{docid}" xmpMM:InstanceID="{docid}" xmpMM:RenditionClass="default"/>
<rdf:Description rdf:about="" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title><rdf:Alt><rdf:li xml:lang="x-default">NoFilter 1 kg Bag Dieline V2</rdf:li></rdf:Alt></dc:title><dc:format>application/pdf</dc:format></rdf:Description>
</rdf:RDF></x:xmpmeta>
<?xpacket end="w"?>"""
    meta = DecodedStreamObject(); meta.set_data(xmp.encode('utf-8'))
    meta[NameObject('/Type')] = NameObject('/Metadata'); meta[NameObject('/Subtype')] = NameObject('/XML')
    writer._root_object[NameObject('/Metadata')] = writer._add_object(meta)
    writer.add_metadata({'/GTS_PDFXVersion': 'PDF/X-4', '/Trapped': '/False', '/Title': 'NoFilter 1 kg Bag Dieline V2'})
    writer._info[NameObject('/Trapped')] = NameObject('/False')
    from pypdf.generic import ByteStringObject; import hashlib
    h = hashlib.md5((docid + iso).encode()).digest()
    writer._ID = ArrayObject([ByteStringObject(h), ByteStringObject(h)])          # PDF/X requires a file identifier
    with open(OUT, 'wb') as f: writer.write(f)
    print('wrote', OUT, os.path.getsize(OUT)//1_000_000, 'MB')

if __name__ == '__main__':
    main()
