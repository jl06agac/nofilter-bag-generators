"""UAE-only bilingual copy and layout. Wording is provisional, not regulatory approval."""
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import CMYKColor
import arabic_reshaper
from bidi.algorithm import get_display

# PLACEHOLDERS: native Arabic review and Bevarabia licence wording are pending.
UAE_LEGAL = ['NoFilter LLC',
 'Shams Business Center, Sharjah Media City Free Zone, Sharjah, UAE',
 'Licence TL 2540001.01 · hello@nofilter.ae']
MANUFACTURER_EN = 'Bevarabia, 364 18th St, Al Quoz Industrial 1, Dubai, UAE'
MANUFACTURER_AR = 'بيفارابيا، 364 شارع 18، القوز الصناعية 1، دبي، الإمارات'
FOR_EN = 'NoFilter LLC, Shams Business Center, Sharjah Media City FZ, Sharjah, UAE'
FOR_AR = 'نوفلتر ذ.م.م، مركز شمس للأعمال، المنطقة الحرة لمدينة الشارقة للإعلام، الشارقة'
AR_CAPTIONS = ['المنتج', 'الوزن الصافي', 'بلد المنشأ', 'صُنع وعُبِّئ بواسطة', 'لصالح']
AR_PRODUCT = 'حبوب قهوة محمصة كاملة'
AR_WEIGHT = {'1kg': '1 كجم', '250g': '250 جم'}
AR_ORIGIN = 'الإمارات العربية المتحدة'
AR_PRODUCTION = 'تاريخ الإنتاج'
AR_EXPIRY = 'تاريخ الانتهاء'
EN_CAPTIONS = ['PRODUCT', 'NET WEIGHT', 'COUNTRY OF ORIGIN', 'MANUFACTURED & PACKED BY', 'FOR']
WHITE = CMYKColor(0,0,0,0)
# Keep Arabic marks; bidi reorders the already-shaped display string.
RESHAPER = arabic_reshaper.ArabicReshaper(configuration={'delete_harakat': False, 'shift_harakat_position': True})

def shaped(value):
    return get_display(RESHAPER.reshape(value), base_dir='R')

def register_arabic(font_dir):
    pdfmetrics.registerFont(TTFont('PlexAr', str(Path(font_dir)/'IBMPlexSansArabic-Regular.ttf')))

def wrap(value, font, size, width, arabic=False):
    lines=[]; current=''
    for word in value.split():
        trial=(current+' '+word).strip()
        visual=shaped(trial) if arabic else trial
        if pdfmetrics.stringWidth(visual,font,size)>width:
            if not current: raise ValueError('UAE text contains a word wider than its column: '+word)
            lines.append(current);current=word
        else:current=trial
    if current:lines.append(current)
    for line in lines:
        if pdfmetrics.stringWidth(shaped(line) if arabic else line,font,size)>width:
            raise ValueError('UAE column overflow: '+line)
    return lines

def draw_uae_side(c, X, Y, text, left, right, start_y, website_y, size):
    """Coordinates in mm. 250g uses the 70/95 panel-width scale and four rows."""
    pt=72/25.4; scale=(right-left)/95
    margin=8*scale; inner_l=left+margin; inner_r=right-margin
    gutter=4*scale; width=(inner_r-inner_l-gutter)/2
    value_en=['Roasted whole coffee beans', '1 kg' if size=='1kg' else '250 g',
              'United Arab Emirates', MANUFACTURER_EN, FOR_EN]
    value_ar=[AR_PRODUCT, AR_WEIGHT[size], AR_ORIGIN, MANUFACTURER_AR, FOR_AR]
    count=5 if size=='1kg' else 4
    rows=[];y=start_y
    for cap, arcap, en, ar in list(zip(EN_CAPTIONS, AR_CAPTIONS,value_en,value_ar))[:count]:
        enlines=wrap(en,'Archivo',7.5*scale,width*pt)
        arlines=wrap(ar,'PlexAr',7.8*scale,width*pt,True)
        rows.append((y,cap,arcap,enlines,arlines))
        y += (3.4 + 3.4*(max(len(enlines),len(arlines))-1) + 4.9)*scale
    # Website is below a 14mm window with a 4mm clear gap.
    window_bottom=website_y-4*scale;window_top=window_bottom-14*scale
    text_bottom=y-4.9*scale+1*scale
    if text_bottom>window_top-3*scale:
        raise ValueError(f'UAE {size} block does not fit: text ends {text_bottom:.2f}, window starts {window_top:.2f}')
    c.saveState();c.setFillColor(WHITE)
    for y,cap,arcap,enlines,arlines in rows:
        c.saveState();c.setFillAlpha(.85)
        text(c,cap,inner_l,y,'Mono',6*scale,tracking=.14)
        text(c,shaped(arcap),inner_r,y,'PlexAr',6*scale,'r')
        c.restoreState()
        for j,line in enumerate(enlines):text(c,line,inner_l,y+(3.4+j*3.4)*scale,'Archivo',7.5*scale)
        for j,line in enumerate(arlines):text(c,shaped(line),inner_r,y+(3.4+j*3.4)*scale,'PlexAr',7.8*scale,'r')
    c.setStrokeColor(WHITE);c.setLineWidth(.3);c.setDash([])
    c.roundRect(X(inner_l),Y(window_bottom),79*scale*pt,14*scale*pt,1*scale*pt,stroke=1,fill=0)
    # Two independently composed labels; Arabic is shaped, never raw or tracked.
    for x0,x1,en,ar in [(inner_l+2*scale,(left+right)/2-2*scale,'PRODUCTION DATE',AR_PRODUCTION),
                        ((left+right)/2+2*scale,inner_r-2*scale,'EXPIRY DATE',AR_EXPIRY)]:
        baseline=window_bottom-2*scale
        label=en+' · '
        w=pdfmetrics.stringWidth(label,'Mono',5.5*scale)/pt
        arw=pdfmetrics.stringWidth(shaped(ar),'PlexAr',5.5*scale)/pt
        if w+arw>x1-x0:raise ValueError('Date caption does not fit')
        text(c,label,x0,baseline,'Mono',5.5*scale)
        text(c,shaped(ar),x1,baseline,'PlexAr',5.5*scale,'r')
    text(c,'NOFILTER.AE · NOFILTER.SG',(left+right)/2,website_y,'Archivo',7*scale,'c',tracking=.15)
    c.restoreState()
    print(f'UAE {size}: {count} rows, text bottom {text_bottom:.2f}mm; date window {79*scale:.2f} x {14*scale:.2f}mm at y={window_top:.2f}mm')
