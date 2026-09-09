import pypdf.filters; pypdf.filters.MAX_DECLARED_STREAM_LENGTH=10**10
from pypdf import PdfReader
from pypdf.generic import ContentStream
import sys
r=PdfReader('../NoFilter_1kg_Bag_NATIVEV1.ai')
pg=r.pages[0]
cs=ContentStream(pg.get_contents(), r)
ops=cs.operations
PT=72/25.4
def mul(a,b):
    return [a[0]*b[0]+a[1]*b[2], a[0]*b[1]+a[1]*b[3], a[2]*b[0]+a[3]*b[2], a[2]*b[1]+a[3]*b[3], a[4]*b[0]+a[5]*b[2]+b[4], a[4]*b[1]+a[5]*b[3]+b[5]]
def apply(m,x,y): return (m[0]*x+m[2]*y+m[4], m[1]*x+m[3]*y+m[5])
ctm=[1,0,0,1,0,0]; stack=[]
layer=None
pts=[]; objs=[]
fill=None; stroke=None; lw=1; gs=None; font=None
tm=None; tlm=None; texts=[]
start=0
H=1501.33
def fmt(b):
    x0,y0,x1,y1=b
    return "x %.1f..%.1f  y(top) %.1f..%.1f mm"%(x0/PT,x1/PT,(H-y1)/PT,(H-y0)/PT)
for i,(args,op) in enumerate(ops):
    op=op.decode() if isinstance(op,bytes) else op
    if op=='BDC' and args and args[0]=='/OC': layer=str(args[1]); print('=== LAYER',layer,'at',i)
    elif op=='q': stack.append((ctm,fill,stroke,lw,gs,font))
    elif op=='Q': ctm,fill,stroke,lw,gs,font=stack.pop()
    elif op=='cm': ctm=mul([float(a) for a in args],ctm)
    elif op in ('m','l'):
        if op=='m' and not pts: start=i
        pts.append(apply(ctm,float(args[0]),float(args[1])))
    elif op=='c':
        for k in (0,2,4): pts.append(apply(ctm,float(args[k]),float(args[k+1])))
    elif op in ('v','y'):
        for k in (0,2): pts.append(apply(ctm,float(args[k]),float(args[k+1])))
    elif op=='re':
        if not pts: start=i
        x,y,w,h=[float(a) for a in args]
        for (px,py) in ((x,y),(x+w,y),(x,y+h),(x+w,y+h)): pts.append(apply(ctm,px,py))
    elif op in ('S','s','f','F','f*','B','B*','b','b*','n'):
        if pts:
            xs=[p[0] for p in pts]; ys=[p[1] for p in pts]
            b=(min(xs),min(ys),max(xs),max(ys))
            objs.append(dict(kind='path',op=op,i0=start,i1=i,bbox=b,n=len(pts),fill=fill,stroke=stroke,lw=lw,gs=gs,layer=layer))
            print("%5d-%5d path %-2s n=%4d %s fill=%s stroke=%s lw=%s gs=%s"%(start,i,op,len(pts),fmt(b),fill,stroke,lw,gs))
        pts=[]
    elif op=='W': pass
    elif op in ('k','g','rg','sc','scn'): fill=(op,tuple(str(a) for a in args))
    elif op in ('K','G','RG','SC','SCN'): stroke=(op,tuple(str(a) for a in args))
    elif op=='cs': fill=('cs',str(args[0]))
    elif op=='CS': stroke=('CS',str(args[0]))
    elif op=='w': lw=float(args[0])
    elif op=='gs': gs=str(args[0])
    elif op=='Tf': font=(str(args[0]),float(args[1]))
    elif op=='BT': tm=[1,0,0,1,0,0]; texts=[]; start=i; tpos=[]
    elif op=='Tm': tm=[float(a) for a in args]; tpos.append(apply(ctm,tm[4],tm[5]))
    elif op=='Td': tm=mul([1,0,0,1,float(args[0]),float(args[1])],tm); tpos.append(apply(ctm,tm[4],tm[5]))
    elif op in ('Tj','TJ',"'",'"'):
        s=args[0] if op=='Tj' else b''.join([x for x in args[0] if isinstance(x,bytes)] ) if isinstance(args[0],list) else args[0]
        try:
            if isinstance(s,bytes): s=s.decode('latin1')
            else: s=str(s)
        except Exception: s=repr(s)
        texts.append(s.replace('\n',' '))
    elif op=='ET':
        if tpos:
            xs=[p[0] for p in tpos]; ys=[p[1] for p in tpos]
            b=(min(xs),min(ys),max(xs),max(ys))
        else: b=(0,0,0,0)
        objs.append(dict(kind='text',i0=start,i1=i,bbox=b,font=font,texts=texts,layer=layer))
        print("%5d-%5d TEXT %s font=%s %s"%(start,i,fmt(b),font,(' | '.join(texts))[:90]))
    elif op=='Do':
        print("%5d Do %s ctm=%s"%(i,args[0],[round(v,2) for v in ctm]))
import pickle; pickle.dump(objs,open('objs.pkl','wb'))
