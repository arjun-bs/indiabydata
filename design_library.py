#!/usr/bin/env python3
"""
IndiaByData — Design Library v3.0
13 poster styles — all white/light backgrounds

ORIGINAL 8:
  s1_white      White + grid        Economy, Budget, Markets
  s2_bold       Cream + tricolor    Demographics, Diaspora
  s3_vibrant    White + grid        Digital, UPI, Space
  s4_table      White clean         State Spotlight
  s5_editorial  White + grid        Trade, Forex, FDI
  s6_numbers    Off-white           Infrastructure, Railways
  s7_chart      White clean         HDI, Education, Women
  s8_forbes     Warm cream          Rankings, Comparisons

NEW SWISS 5:
  s9_geometric  Cream + shapes      Big numbers, Economy
  s10_oversized Dark + huge num     Tech, Growth, Milestones
  s11_colorblock Color block bold   Digital India, Sectors
  s12_grid      Saffron grid        Structured data, Budget
  s13_bignum    Saffron + big num   Single hero stat

Usage:
  from design_library import re, *
  buf = s1_white(title, hero, hero_sub, hero_sent, stats, source)
"""

from PIL import Image, ImageDraw, ImageFont
import re
import io, os

W, H  = 1080, 1350
PAD   = 90
GREEN = "#1A8C3A"
RED   = "#D93025"
AMBER = "#D4860A"
BLACK = "#111111"
HERO_INK = BLACK   # the big hero numbers are always black; colour meaning lives in shapes, bars and accents
GRAY  = "#888888"
LGRAY = "#AAAAAA"
BRAND = "#FF6B35"

BOLD_PATH    = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
REGULAR_PATH = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

def get_font(size, bold=True):
    mac=[("/System/Library/Fonts/Helvetica.ttc", 1 if bold else 0),
         ("/Library/Fonts/Arial Bold.ttf", 0)]
    for path,idx in mac:
        if os.path.exists(path):
            try: return ImageFont.truetype(path, size, index=idx)
            except: continue
    try: return ImageFont.truetype(BOLD_PATH if bold else REGULAR_PATH, size, index=0)
    except: return ImageFont.load_default()

def fit(draw, text, size, max_w, bold=True, min_size=18):
    """Largest font <= size whose rendered width fits max_w."""
    while size > min_size:
        f = get_font(size, bold)
        if draw.textbbox((0,0), str(text), font=f)[2] <= max_w: return f
        size -= 2
    return get_font(min_size, bold)

# ── Colour themes: tinted full-colour looks, rotated daily from post.py ───────────────
# name: (tint = light page colour, mid = medium pastel, bold = saturated block colour)
PALETTES = [("sand",     "#F2EDE4", "#FFE08A", "#FFC107"),
            ("mint",     "#D5ECDC", "#A8DDB5", "#8BC34A"),
            ("peach",    "#FFE3D3", "#FFC4A3", "#FF6B35"),
            ("sky",      "#D8E8FF", "#A9CDFA", "#2196F3"),
            ("lavender", "#E8DEF7", "#CDB8F0", "#9C6ADE"),
            ("rose",     "#FBDDE5", "#F6B0C4", "#E91E63"),
            ("sage",     "#DCE8E2", "#A6D1C4", "#26A69A"),
            ("lemon",    "#F7F0D2", "#F2DE86", "#FFB300")]
_TH = {}

def _mix(a, b, t):
    a = [int(a[i:i + 2], 16) for i in (1, 3, 5)]; b = [int(b[i:i + 2], 16) for i in (1, 3, 5)]
    return "#%02X%02X%02X" % tuple(round(x + (y - x) * t) for x, y in zip(a, b))

# Vibrant accents for shapes (S9 geometry etc.). Never tied to meaning, so the feed is not all green.
VIBRANT = ["#FF6B35", "#2196F3", "#E91E63", "#9C6ADE", "#00A896", "#FF3D00",
           "#FFB300", "#00B8D4", "#D500F9", "#3F51B5", "#F50057", "#43A047"]

def rotation(n):
    """Colour pair (palette, accent) for post number n = day_ordinal*4 + slot. Consecutive posts always differ in
    both, and all 96 pairs (8 palettes x 12 accents) are used once before any pair comes back (then it re-shifts)."""
    c, i = divmod(n, 96); q, r = divmod(i, 8)
    return (3 * i + c) % 8, (q + 5 * r + c) % len(VIBRANT)

def set_theme(index=None, accent=None):
    """Select palette number `index` (wraps) and vibrant accent number `accent`. None = original colours."""
    _TH.clear()
    if index is None: return None
    name, tint, mid, bold = PALETTES[index % len(PALETTES)]
    _TH.update(name=name, tint=tint, mid=mid, bold=bold,
               panel=_mix(tint, "#FFFFFF", 0.6), rule=_mix(tint, "#000000", 0.18))
    if accent is not None: _TH["accent"] = VIBRANT[accent % len(VIBRANT)]
    return name

def _th(key, default):
    return _TH.get(key, default)

def hc(sent):
    return {"green":GREEN,"red":RED,"amber":AMBER}.get(sent, GREEN)

def logo(draw, x=PAD, y=55, dark=False):
    bw=12; gap=5; tc="#222222" if not dark else "#FFFFFF"
    for i,(bh,c) in enumerate(zip([22,36,28],[BRAND,"#CCCCCC",GREEN])):
        bx=x+i*(bw+gap); draw.rectangle([bx,y+40-bh,bx+bw,y+40],fill=c)
    draw.text((x+3*(bw+gap)+14,y+8),"IndiaByData",font=get_font(30),fill=tc)

def grid(draw, col="#EBEBEA"):
    for i in range(0,W,40): draw.line([(i,0),(i,H)],fill=col,width=1)
    for i in range(0,H,40): draw.line([(0,i),(W,i)],fill=col,width=1)

def wrap(draw, text, font, max_w):
    words=text.split(); lines,line=[],""
    for w in words:
        t=(line+" "+w).strip()
        if draw.textbbox((0,0),t,font=font)[2]>max_w: lines.append(line);line=w
        else: line=t
    lines.append(line); return [l for l in lines if l]

def save_buf(img):
    buf=io.BytesIO(); img.save(buf,format="PNG",quality=95); buf.seek(0); return buf

# ══════════════════════════════════════════════════════════
# STYLE 1 — White Editorial + Grid
# ══════════════════════════════════════════════════════════
def s1_white(title, hero, hero_sub, hero_sent, stats, source, accent="#D4A017", kicker="INDIA'S"):
    """S1 redesign (half-colour): bold colour top block with the title, tint page below, hero number, ruled stat rows."""
    P=PAD; bold=_th("bold","#FFC107")
    img=Image.new("RGB",(W,H),_th("tint","#F5F4F0")); draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,W,470],fill=bold)
    logo(draw,P,60)
    draw.text((P,190),kicker.upper(),font=fit(draw,kicker.upper(),40,W-2*P),fill=BLACK)
    ty=246; lines=wrap(draw,title.upper(),get_font(92),W-2*P)[:2]
    sz=min(fit(draw,l,92,W-2*P).size for l in lines)
    for l in lines: draw.text((P,ty),l,font=get_font(sz),fill=BLACK); ty+=sz+8
    hf=fit(draw,hero,250,W-2*P+10); hb=draw.textbbox((0,0),hero,font=hf)
    draw.text((P-6,520-hb[1]),hero,font=hf,fill=HERO_INK)
    draw.text((P,520+(hb[3]-hb[1])+26),hero_sub,font=fit(draw,hero_sub,32,W-2*P,False),fill="#333333")
    rows=list(stats)[:3]; ry=900; rh=(H-ry-110)//max(1,len(rows))
    for i,(val,lbl) in enumerate(rows):
        y=ry+i*rh
        draw.line([(P,y),(W-P,y)],fill=BLACK,width=3 if i==0 else 1)
        draw.text((P,y+rh//2-16),lbl.upper(),font=fit(draw,lbl.upper(),24,W//2-P-20,False),fill="#333333")
        vf=fit(draw,val,72,W//2); vb=draw.textbbox((0,0),val,font=vf)
        draw.text((W-P-vb[2],y+rh//2-(vb[3]-vb[1])//2-vb[1]),val,font=vf,fill=BLACK)
    draw.line([(P,ry+len(rows)*rh),(W-P,ry+len(rows)*rh)],fill=BLACK,width=1)
    draw.text((P,H-70),source,font=fit(draw,source,20,W-2*P,False,min_size=12),fill="#555555")
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 2 — Bold Statement + Tricolor
# ══════════════════════════════════════════════════════════
def s2_bold(headline, number, hero_sent, number_unit, sub, stats3, note, source):
    """S2 redesign: headline, one big colour card holding the hero number, three stat tiles, takeaway band."""
    P=PAD; bold=_th("bold",BRAND); mid=_th("mid","#F2E9D8"); panel=_th("panel","#FFFFFF")
    img=Image.new("RGB",(W,H),_th("tint","#FAF9F7")); draw=ImageDraw.Draw(img)
    logo(draw,P,60)
    chip="DATA POINT"; cf=get_font(22); cw_=draw.textbbox((0,0),chip,font=cf)[2]
    draw.rounded_rectangle([W-P-cw_-36,70,W-P,116],radius=23,fill=bold); draw.text((W-P-cw_-18,81),chip,font=cf,fill=BLACK)
    hl=wrap(draw,headline,get_font(64),W-2*P)[:2]
    for j,l in enumerate(hl): draw.text((P,170+j*76),l,font=fit(draw,l,64,W-2*P),fill=BLACK)
    cy=170+len(hl)*76+30; ch=430
    draw.rounded_rectangle([P,cy,W-P,cy+ch],radius=28,fill=mid)
    draw.rounded_rectangle([P,cy,P+14,cy+ch],radius=7,fill=bold)
    unit=str(number_unit).strip()
    uf=get_font(54); uw=draw.textbbox((0,0),unit,font=uf)[2] if unit else 0
    nf=fit(draw,number,350,W-2*P-70-(uw+20 if unit else 0))
    nb=draw.textbbox((0,0),number,font=nf)
    draw.text((P+44,cy+34-nb[1]),number,font=nf,fill=HERO_INK)
    if unit: draw.text((P+44+nb[2]+18,cy+34-nb[1]+(nb[3]-nb[1])-uf.size+8),unit,font=uf,fill=BLACK)
    draw.text((P+44,cy+ch-86),sub,font=fit(draw,sub,42,W-2*P-88),fill=BLACK)
    ty=cy+ch+36; n=max(1,len(stats3)); gap=20; tw=(W-2*P-gap*(n-1))//n
    for i,(v,l) in enumerate(stats3):
        x=P+i*(tw+gap)
        draw.rounded_rectangle([x,ty,x+tw,ty+190],radius=18,fill=panel)
        draw.rectangle([x+20,ty,x+tw-20,ty+7],fill=bold)
        draw.text((x+20,ty+34),v,font=fit(draw,v,66,tw-40),fill=BLACK)
        draw.text((x+20,ty+128),l,font=fit(draw,l.upper(),22,tw-40,False),fill="#555555")
    by=ty+190+36; bh=H-by-110
    draw.rounded_rectangle([P,by,W-P,by+bh],radius=22,fill=bold)
    nl=wrap(draw,note,get_font(40),W-2*P-60)[:3]
    ny=by+(bh-len(nl)*50)//2
    for j,l in enumerate(nl): draw.text((P+30,ny+j*50),l,font=get_font(40),fill=BLACK)
    draw.text((P,H-70),source,font=fit(draw,source,20,W-2*P,False,min_size=12),fill="#555555")
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 3 — Vibrant (full-colour poster: whole page in the day's bold colour, giant black number)
# ══════════════════════════════════════════════════════════
def s3_vibrant(title_top, title_bot, hero_val, hero_sent, cards3, source):
    """Swiss full-colour poster: one bold colour, black type, strict left grid, hairline rules only."""
    P=PAD; bold=_th("bold",BRAND)
    img=Image.new("RGB",(W,H),bold); draw=ImageDraw.Draw(img)
    logo(draw,P,60)
    draw.text((P,200),title_top.upper(),font=fit(draw,title_top.upper(),44,W-2*P),fill=BLACK)
    draw.text((P,262),title_bot.upper(),font=fit(draw,title_bot.upper(),120,W-2*P),fill=BLACK)
    draw.line([(P,430),(W-P,430)],fill=BLACK,width=3)
    hf=fit(draw,hero_val,430,W-2*P+10); hb=draw.textbbox((0,0),hero_val,font=hf)
    draw.text((P-8,490-hb[1]),hero_val,font=hf,fill=HERO_INK)
    rows=list(cards3)[:4]; n=max(1,len(rows)); cw=(W-2*P)//n
    ry=1040
    draw.line([(P,ry),(W-P,ry)],fill=BLACK,width=3)
    vsz=min(fit(draw,v,70,cw-24).size for v,_l in rows)   # one value size across the row
    lsz=min(fit(draw,l.upper(),22,cw-24,False).size for _v,l in rows)
    for i,(val,lbl) in enumerate(rows):
        x=P+i*cw
        draw.text((x,ry+26),lbl.upper(),font=get_font(lsz,False),fill=BLACK)
        draw.text((x,ry+66),val,font=get_font(vsz),fill=BLACK)
    draw.text((P,H-70),source,font=fit(draw,source,20,W-2*P,False,min_size=12),fill=BLACK)
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 4 — Data Table Clean
# ══════════════════════════════════════════════════════════
def s4_table(name, known, info):
    """S4 in the geometric vibe: tint page, tile band, black state name, ruled table, accent 'did you know' block."""
    P=80; BG=_th("tint","#F2EDE4"); accent=_TH.get("accent",BRAND)
    img=Image.new("RGB",(W,H),BG); draw=ImageDraw.Draw(img)
    _draw_motif(draw,"tiles",accent,BG,"",P,(P,W-P,60,300))
    draw.text((P,330),"STATE SPOTLIGHT",font=get_font(24),fill="#444444")
    draw.text((P,368),name.upper(),font=fit(draw,name.upper(),112,W-2*P),fill=BLACK)
    draw.text((P,500),known,font=fit(draw,known,34,W-2*P,False),fill="#333333")
    gdp_pc=round(info['gdp']*1e12/(info['pop']*1e6)/1000)
    rows=[("State GDP",f"Rs. {info['gdp']}T","Top 5 in India"),("Population",f"{info['pop']}M","Census data"),
          ("Literacy rate",f"{info['lit']}%","Natl avg 77.7%"),("GDP per capita",f"Rs. {gdp_pc}K","Annual"),("Capital",info["capital"],"Admin HQ")]
    c2=P+360; c3=P+700; ry=560; rh=86
    draw.line([(P,ry),(W-P,ry)],fill=BLACK,width=3)
    for i,(m,v,r) in enumerate(rows):
        y=ry+i*rh
        draw.text((P,y+30),m.upper(),font=fit(draw,m.upper(),22,c2-P-20,False),fill="#444444")
        draw.text((c2,y+18),v,font=fit(draw,v,46,c3-c2-20),fill=BLACK)
        draw.text((c3,y+32),r,font=fit(draw,r,22,W-P-c3,False),fill="#555555")
        draw.line([(P,y+rh),(W-P,y+rh)],fill=_mix(BG,"#000000",0.25),width=1)
    by=ry+len(rows)*rh+30; pct=round(info['gdp']/160*100,1)
    draw.rectangle([P,by,W-P,H-112],fill=accent)
    draw.text((P+30,by+22),"DID YOU KNOW?",font=get_font(22),fill=BLACK)
    draw.text((P+30,by+58),f"{name} contributes",font=fit(draw,f"{name} contributes",32,W-2*P-60,False),fill=BLACK)
    draw.text((P+30,by+100),f"{pct}% of India's GDP",font=fit(draw,f"{pct}% of India's GDP",76,W-2*P-60),fill=BLACK)
    logo(draw,P,H-88)
    draw.text((P,H-38),"Source: Census, State Economic Survey",font=get_font(18,False),fill="#555555")
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 5 — Editorial White + Grid
# ══════════════════════════════════════════════════════════
def s5_editorial(title1, title2, hero, hero_sub, hero_sent, cards4, source):
    """S5 redesign: stacked title, giant black number, then a sharp 2x2 block of colour tiles."""
    P=PAD; bold=_th("bold","#FFC107"); mid=_th("mid","#F2E9D8")
    img=Image.new("RGB",(W,H),_th("tint","#F5F4F0")); draw=ImageDraw.Draw(img)
    logo(draw,P,60)
    draw.text((P,170),title1.upper(),font=fit(draw,title1.upper(),44,W-2*P),fill=BLACK)
    draw.text((P,228),title2.upper(),font=fit(draw,title2.upper(),104,W-2*P),fill=BLACK)
    hf=fit(draw,hero,270,W-2*P+10); hb=draw.textbbox((0,0),hero,font=hf)
    draw.text((P-6,410-hb[1]),hero,font=hf,fill=HERO_INK)
    draw.text((P,410+(hb[3]-hb[1])+24),hero_sub,font=fit(draw,hero_sub,30,W-2*P,False),fill="#333333")
    gy=760; g=0; tw=(W-2*P)//2; th_=(H-gy-110)//2
    cols=[bold,mid,mid,bold]
    for i,(val,lbl) in enumerate(list(cards4)[:4]):
        x=P+(i%2)*tw; y=gy+(i//2)*th_
        draw.rectangle([x,y,x+tw,y+th_],fill=cols[i])
        draw.text((x+28,y+26),lbl.upper(),font=fit(draw,lbl.upper(),22,tw-56,False),fill=BLACK)
        draw.text((x+28,y+th_-110),val,font=fit(draw,val,80,tw-56),fill=BLACK)
    draw.text((P,H-70),source,font=fit(draw,source,20,W-2*P,False,min_size=12),fill="#555555")
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 6 — Large Numbers
# ══════════════════════════════════════════════════════════
def s6_numbers(title1, title2, year, hero_num, hero_unit, hero_label, hero_sent, items3, source, accent=GREEN):
    """S6 redesign: pastel full page with a bold colour edge bar, giant number with unit, three ruled number rows."""
    P=PAD; bold=_th("bold","#FFC107")
    img=Image.new("RGB",(W,H),_th("mid","#F2E9D8")); draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,36,H],fill=bold)
    logo(draw,P+10,60)
    head=f"{title1} {title2}".strip().upper()
    draw.text((P+10,180),head,font=fit(draw,head,56,W-2*P-10),fill=BLACK)
    if year: draw.text((P+10,250),str(year),font=get_font(34,False),fill="#333333")
    unit=str(hero_unit).strip(); uf=get_font(48)
    uw=draw.textbbox((0,0),unit,font=uf)[2] if unit else 0
    nf=fit(draw,hero_num,330,W-2*P-10-(uw+24 if unit else 0)); nb=draw.textbbox((0,0),hero_num,font=nf)
    draw.text((P,360-nb[1]),hero_num,font=nf,fill=HERO_INK)
    if unit: draw.text((P+nb[2]+22,360-nb[1]+(nb[3]-nb[1])-uf.size+6),unit.upper(),font=uf,fill=BLACK)
    ly=360+(nb[3]-nb[1])+26
    draw.text((P+10,ly),hero_label,font=fit(draw,hero_label,34,W-2*P-10,False),fill="#333333")
    items=list(items3)[:3]; ry=860; rh=(H-ry-110)//max(1,len(items))
    for i,(n,u,l) in enumerate(items):
        y=ry+i*rh
        draw.line([(P+10,y),(W-P,y)],fill=BLACK,width=3 if i==0 else 1)
        txt=f"{n} {u}".strip()
        draw.text((P+10,y+rh//2-34),txt,font=fit(draw,txt,70,W//2),fill=BLACK)
        lf=fit(draw,str(l).upper(),24,W//2-P-20,False); lb=draw.textbbox((0,0),str(l).upper(),font=lf)
        draw.text((W-P-lb[2],y+rh//2-12),str(l).upper(),font=lf,fill="#333333")
    draw.line([(P+10,ry+len(items)*rh),(W-P,ry+len(items)*rh)],fill=BLACK,width=1)
    draw.text((P+10,H-70),source,font=fit(draw,source,20,W-2*P-10,False,min_size=12),fill="#555555")
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 7 — Bar Chart
# ══════════════════════════════════════════════════════════
def s7_chart(title1, title2, hero, hero_sub, hero_sent, bars, callout, stats2, source, accent="#7B5EA7"):
    P=PAD; img=Image.new("RGB",(W,H),_th("tint","#FFFFFF")); draw=ImageDraw.Draw(img)
    logo(draw,P,58)
    draw.text((P,158),title1,font=get_font(60),fill=BLACK)
    draw.text((P,238),title2,font=get_font(60),fill=accent)
    draw.line([(P,322),(W-P,322)],fill="#EEEEEE",width=2)
    draw.text((P,342),hero,font=fit(draw,hero,200,W-2*P),fill=HERO_INK)
    draw.text((P,560),hero_sub,font=get_font(32,bold=False),fill=GRAY)
    draw.line([(P,628),(W-P,628)],fill="#EEEEEE",width=2)
    max_v=max(v for _,v in bars)
    for i,(label,val) in enumerate(bars):
        y=658+i*92; bw=int((val/max_v)*(W-P*2-120))
        draw.rounded_rectangle([P,y,P+bw,y+56],radius=6,fill=accent)
        draw.text((P,y+60),label,font=get_font(20,bold=False),fill="#999999")
        draw.text((P+bw+14,y+12),f"{val}%",font=get_font(32),fill=BLACK)
    draw.line([(P,1025),(W-P,1025)],fill="#EEEEEE",width=1)
    draw.text((P,1045),callout,font=fit(draw,callout,52,W-2*P),fill=accent)
    draw.text((P,1112),stats2[0],font=fit(draw,stats2[0],26,W-2*P,False),fill="#666666")
    draw.text((P,1152),stats2[1],font=fit(draw,stats2[1],26,W-2*P,False),fill="#666666")
    draw.text((P,H-75),source,font=get_font(20,bold=False),fill=LGRAY)
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 8 — Swiss/Forbes Bar Chart
# ══════════════════════════════════════════════════════════
def s8_forbes(title, subtitle, bars, unit_label, source, bar_colors=None):
    source = re.sub(r"^\s*Source:\s*", "", source)
    P=70; CHART_H=400; MARGIN=65
    default_colors=["#D94F3D","#E8853D","#E8C23D","#2D6A2D","#1A3A8C","#7B4FA6","#8C4A2D","#4A8C2D"]
    colors=bar_colors or default_colors
    img=Image.new("RGB",(W,H),_th("tint","#F7F6F2")); draw=ImageDraw.Draw(img)
    dummy=Image.new("RGB",(W,H)); d=ImageDraw.Draw(dummy)
    title_lines=wrap(d,title,get_font(80),W-P*2); title_h=len(title_lines)*88
    sub_lines=wrap(d,subtitle,get_font(32,bold=False),W-P*2); sub_h=len(sub_lines)*44
    content_h=title_h+2+sub_h+30+32+CHART_H+36+28+50
    gap=max(12,(H-MARGIN*2-content_h)//8); ty=MARGIN
    for l in title_lines: draw.text((P,ty),l,font=get_font(80),fill=BLACK); ty+=88
    ty+=gap; draw.line([(P,ty),(W-P,ty)],fill="#CCCCCC",width=1); ty+=gap
    for l in sub_lines: draw.text((P,ty),l,font=get_font(32,bold=False),fill="#444444"); ty+=44
    ty+=gap; lx=P
    for i,(label,_) in enumerate(bars):
        col=colors[i%len(colors)]; draw.rectangle([lx,ty+3,lx+18,ty+21],fill=col)
        draw.text((lx+24,ty),label,font=get_font(22,bold=False),fill="#333333")
        tw=draw.textbbox((0,0),label,font=get_font(22,bold=False))[2]; lx+=tw+42
        if lx>W-160: ty+=30;lx=P
    ty+=gap; draw.text((P,ty),"# "+unit_label,font=get_font(24),fill=BLACK); ty+=32+gap
    chart_top=ty; chart_bottom=chart_top+CHART_H; chart_h=CHART_H
    chart_left=P+70; chart_right=W-P; chart_w=chart_right-chart_left
    max_val=max(v for _,v in bars); n=len(bars)
    bar_w=int(chart_w/n*0.70); gap_w=int(chart_w/n*0.30)
    for gi in range(5):
        gy=chart_bottom-int(gi/4*chart_h); gv=round(gi/4*max_val,1)
        draw.line([(chart_left,gy),(chart_right,gy)],fill="#DDDDDD",width=1)
        draw.text((P,gy-12),f"{gv:,}",font=get_font(20,bold=False),fill=LGRAY)
    for i,(label,val) in enumerate(bars):
        bh=int((val/max_val)*chart_h); bx=chart_left+i*(bar_w+gap_w); by=chart_bottom-bh
        col=colors[i%len(colors)]; draw.rectangle([bx,by,bx+bar_w,chart_bottom],fill=col)
        vs=f"{val:,}"; vb=draw.textbbox((0,0),vs,font=get_font(22)); vw=vb[2]-vb[0]
        draw.text((bx+(bar_w-vw)//2,by-30),vs,font=get_font(22),fill=BLACK)
        lb=draw.textbbox((0,0),label,font=get_font(22,bold=False)); lw=lb[2]-lb[0]
        draw.text((bx+(bar_w-lw)//2,chart_bottom+10),label,font=get_font(22,bold=False),fill="#555555")
    draw.line([(chart_left,chart_bottom),(chart_right,chart_bottom)],fill="#888888",width=2)
    ty=chart_bottom+36+gap
    draw.text((P,ty),f"Source: {source}",font=get_font(22,bold=False),fill=LGRAY); ty+=28+gap
    bw=12; gp=5
    for i,(bh,c) in enumerate(zip([22,36,28],[BRAND,"#CCCCCC",GREEN])):
        bx=P+i*(bw+gp); draw.rectangle([bx,ty+40-bh,bx+bw,ty+40],fill=c)
    draw.text((P+3*(bw+gp)+14,ty+8),"IndiaByData",font=get_font(30),fill="#222222")
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 9 — Geometric Swiss  (ref: bold shapes + big type)
# ══════════════════════════════════════════════════════════
# ── Content-driven geometry for S9: the shapes say something about the poster ───────
_KW = [("rays",   r"electric|power|energy|solar|renewable|coal|grid|battery|fuel"),
       ("plus",   r"health|hospital|doctor|medical|disease|vaccin|mortality|infant|nutrition|cancer"),
       ("arc",    r"life expectancy|lifespan|\bage\b"),
       ("stripes",r"rail|road|metro|highway|airport|transport|vehicle|\bev\b|\bevs\b|logistic|port\b|flight|travel"),
       ("bars",   r"gdp|econom|fund|revenue|trade|income|salary|wage|invest|export|import|sales|market|budget|tax|\$|rs\.|usd|inr|crore|loan|bank|startup"),
       ("crowd",  r"popul|people|users|students|workers|farmers|households|citizens|million|billion|lakh|youth|women|men\b|children|births")]

def motif_for(label, hero, sub=""):
    """Pick the shape that matches the poster: ratios -> steps, % -> 100 dots, life/time -> rings, etc."""
    t=f"{label} {sub}".lower(); h=str(hero).strip().lower()
    def has(k): return re.search(dict(_KW)[k], t)
    if has("rays"): return "rays"
    if re.fullmatch(r"[+\-]?[\d.,]+\s*x",h): return "steps"
    if re.search(r"life expectancy|lifespan|\bage\b",t) or re.search(r"\byrs?\b|years",h): return "arc"
    if has("stripes"): return "stripes"
    if has("plus"): return "plus"
    if has("bars") or re.search(r"\$|rs\.",h): return "bars"
    if h.endswith("%"): return "share"
    if has("crowd") or re.search(r"\d\s*[mbk]$",h): return "crowd"
    return "classic"

def _num(txt, default=50.0):
    m=re.search(r"[\d.]+",str(txt).replace(",",""))
    return float(m.group(0)) if m else default

def _draw_motif(draw, kind, color, BG, hero_val, P=80, box=None):
    """Draw the content shape inside box=(x0,x1,y0,y1). Default box is the tall S9 area; shapes scale with its height."""
    import math
    x0,x1,y0,y1=box or (P,W-P,60,620)
    k=(y1-y0)/560.0; soft=_mix(color,BG,0.62)
    if kind=="share":                      # 100 dots, N of them filled
        pct=max(0,min(100,round(_num(hero_val)))); gap=max(3,int(6*k)); cell=(y1-y0-9*gap)//10
        for i in range(100):
            row,col=divmod(i,10); x=x0+col*(cell+gap); y=y0+row*(cell+gap)
            draw.ellipse([x,y,x+cell,y+cell],fill=color if i<pct else _mix(BG,"#000000",0.10))
        tx=x0+10*(cell+gap)+40
        draw.text((tx,y1-int(170*k)),"EACH DOT",font=get_font(max(18,int(26*k)),False),fill="#555555")
        draw.text((tx,y1-int(135*k)),"= 1 IN 100",font=get_font(max(22,int(34*k))),fill=BLACK)
    elif kind=="bars":                     # rising bars
        n=6; bw=118; gap=(x1-x0-n*bw)//(n-1)
        for i in range(n):
            h=int((120+i*86)*k); x=x0+i*(bw+gap)
            draw.rectangle([x,y1-h,x+bw,y1],fill=color if i==n-1 else _mix(color,BG,0.45+0.06*(n-1-i)*0.5))
    elif kind=="crowd":                    # a crowd of dots, a few highlighted
        cols=15 if k>0.7 else 24; pitch=(x1-x0)//cols; r=pitch//2-max(2,int(5*k)); rows=max(1,(y1-y0)//pitch); n=0
        for rw in range(rows):
            for c in range(cols):
                cx=x0+c*pitch+pitch//2; cy=y1-rw*pitch-pitch//2
                draw.ellipse([cx-r,cy-r,cx+r,cy+r],fill=color if (n%9!=4) else soft); n+=1
    elif kind=="steps":                    # then vs now, areas in true proportion
        ratio=max(1.2,min(9.0,_num(hero_val,2.0))); s0=int(150*k); s1=min(y1-y0,int(s0*math.sqrt(ratio)))
        draw.rectangle([x0,y1-s0,x0+s0,y1],fill=soft); draw.rectangle([x0+s0+40,y1-s1,x0+s0+40+s1,y1],fill=color)
        draw.text((x0+s0+40+s1+24,y1-50),"THEN",font=get_font(max(18,int(24*k)),False),fill="#555555")
    elif kind=="arc":                      # concentric half rings
        cx=(x0+x1)//2
        for i,rad in enumerate((460,380,300,220,140)):
            rr=int(rad*k); draw.pieslice([cx-rr,y1-rr,cx+rr,y1+rr],180,360,fill=color if i%2==0 else soft)
        rr=int(70*k); draw.pieslice([cx-rr,y1-rr,cx+rr,y1+rr],180,360,fill=BG)
    elif kind=="rays":                     # sun / energy
        cx,cy=(x0+x1)//2,(y0+y1)//2
        draw.ellipse([cx-int(120*k),cy-int(120*k),cx+int(120*k),cy+int(120*k)],fill=color)
        for a_ in range(0,360,30):
            dx,dy=math.cos(math.radians(a_)),math.sin(math.radians(a_))
            draw.line([(cx+dx*165*k,cy+dy*165*k),(cx+dx*265*k,cy+dy*265*k)],fill=color,width=max(10,int(30*k)))
    elif kind=="plus":                     # health cross, large + small
        def plus(cx,cy,arm,th,col):
            draw.rectangle([cx-th//2,cy-arm,cx+th//2,cy+arm],fill=col); draw.rectangle([cx-arm,cy-th//2,cx+arm,cy+th//2],fill=col)
        plus(x0+int(300*k)+20,(y0+y1)//2+4,int(270*k),int(170*k),color)
        plus(x1-int(170*k)-40,y0+int(150*k),int(110*k),int(70*k),soft); plus(x1-int(120*k)-30,y1-int(110*k),int(70*k),int(44*k),color)
    elif kind=="stripes":                  # road / rail lanes
        n=7; w=70; gap=44; off=int(170*k)
        for i in range(n):
            xa=x0+i*(w+gap)
            draw.polygon([(xa+off,y0),(xa+off+w,y0),(xa+w,y1),(xa,y1)],fill=color if i%2==0 else soft)
    elif kind=="tiles":                    # Swiss tile row: half circles, quarter circles, squares
        n=6; gap=14; t=(x1-x0-gap*(n-1))//n; t=min(t,y1-y0)
        for i in range(n):
            x=x0+i*(t+gap); y=y1-t; v=i%4
            if v==0: draw.pieslice([x,y,x+2*t,y+2*t],180,270,fill=color)
            elif v==1: draw.ellipse([x,y,x+t,y+t],fill=color)
            elif v==2: draw.rectangle([x,y,x+t,y+t],fill=soft)
            else: draw.pieslice([x-t,y-t,x+t,y+t],0,90,fill=color)
    else:
        return False
    return True

def s9_geometric(stat_label, hero_val, stat_sub, color=BRAND, stats3=[], source="", motif=None):
    P=80; BG=_th("tint","#F2EDE4")
    img=Image.new("RGB",(W,H),BG); draw=ImageDraw.Draw(img)
    color = _TH.get("accent", color)          # vibrant accent of the day (falls back to the colour passed in)
    kind = motif or motif_for(stat_label, hero_val, stat_sub)
    if kind == "classic" or not _draw_motif(draw, kind, color, BG, hero_val, P): _classic_shapes(draw, color, BG, P)
    return _s9_finish(img, draw, P, stat_label, hero_val, stat_sub, color, stats3, source)

def _classic_shapes(draw, color, BG, P):
    # Row 1 shapes
    r1=220
    draw.ellipse([P,60,P+r1*2,60+r1*2],fill=color)
    draw.rectangle([P,60,P+r1*2,60+r1],fill=BG)
    r2=150; x2=W//2+20
    draw.ellipse([x2,80,x2+r2*2,80+r2*2],fill=color)
    draw.rectangle([x2+r2,80,x2+r2*2,80+r2*2],fill=BG)
    r3=110; x3=W-P-r3*2
    draw.ellipse([x3,100,x3+r3*2,100+r3*2],fill=color)
    draw.rectangle([x3,100,x3+r3*2,100+r3],fill=BG)
    # Row 2 shapes
    r4=200
    draw.ellipse([P,380,P+r4*2,380+r4*2],fill=color)
    draw.rectangle([P,380+r4,P+r4*2,380+r4*2],fill=BG)
    r5=130; x5=W//2+40
    draw.ellipse([x5,400,x5+r5*2,400+r5*2],fill=color)
    draw.rectangle([x5,400+r5,x5+r5*2,400+r5*2],fill=BG)
    draw.rectangle([x5+r5,400,x5+r5*2,400+r5],fill=BG)

def _s9_finish(img, draw, P, stat_label, hero_val, stat_sub, color, stats3, source):
    # Divider + text grid
    draw.line([(P,660),(W-P,660)],fill="#BBAA99",width=1)
    if stats3:
        cw=(W-P*2)//3
        for i,(v,l) in enumerate(stats3):
            x=P+i*cw
            draw.text((x,686),l.upper(),font=fit(draw,l.upper(),20,cw-30,False),fill="#444444")
            draw.text((x,715),v,font=fit(draw,v,50,cw-30),fill=BLACK)
    draw.text((P,810),stat_label,font=fit(draw,stat_label,26,W-2*P,False),fill="#555555")
    draw.text((P,845),stat_sub,font=fit(draw,stat_sub,26,W-2*P,False),fill="#555555")
    draw.text((P-10,940),hero_val,font=fit(draw,hero_val,280,W-2*P+10),fill=HERO_INK)
    logo(draw,P,H-88)
    draw.text((P,H-38),source,font=get_font(18,bold=False),fill="#AAAAAA")
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 10 — Oversized Dark  (ref: huge number, dots, dark)
# ══════════════════════════════════════════════════════════
def s10_oversized(big_num, content_blocks, dot_colors=["#D93025","#2196F3","#8BC34A"], source=""):
    P=80
    img=Image.new("RGB",(W,H),"#242424"); draw=ImageDraw.Draw(img)
    for y in range(0,H,H//4): draw.line([(0,y),(W,y)],fill="#2E2E2E",width=1)
    draw.line([(W//2,0),(W//2,H)],fill="#2E2E2E",width=1)
    # Big number on one line
    draw.text((10,40),big_num,font=fit(draw,big_num,320,W-70),fill="#333333")
    # Colored dots row below number
    dot_y=382; dot_r=45
    for i,(dx,col) in enumerate(zip([P+30,P+160,P+290],dot_colors)):
        draw.ellipse([dx,dot_y,dx+dot_r*2,dot_y+dot_r*2],fill=col)
    draw.line([(P,480),(W-P,480)],fill="#444444",width=1)
    for i,(title,body) in enumerate(content_blocks[:2]):
        cy=520+i*320; draw.text((P,cy),title,font=fit(draw,title,52,W-2*P),fill="#FFFFFF")
        for j,line in enumerate(wrap(draw,body,get_font(28,bold=False),W-P*2)):
            draw.text((P,cy+68+j*38),line,font=get_font(28,bold=False),fill="#AAAAAA")
    draw.line([(P,H-140),(W-P,H-140)],fill="#444444",width=1)
    logo(draw,P,H-120,dark=True)
    draw.text((P,H-62),source,font=get_font(18,bold=False),fill="#555555")
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 11 — Color Block Bold  (ref: bold color top + grid)
# ══════════════════════════════════════════════════════════
def s11_colorblock(block_color, line1, line2, body_l, body_r, stats4=[], source=""):
    P=80
    img=Image.new("RGB",(W,H),_th("tint","#EFEFEF")); draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,W,560],fill=block_color)
    draw.text((P,70),line1,font=fit(draw,line1,120,W-2*P),fill=BLACK)
    draw.text((P,200),line2,font=fit(draw,line2,120,W-2*P),fill=BLACK)
    logo(draw,P,470)
    cw=(W-P*2-40)//2
    draw.text((P,620),"INDIA BY DATA",font=get_font(20,bold=False),fill="#999999")
    draw.line([(P,655),(W-P,655)],fill="#CCCCCC",width=1)
    for j,line in enumerate(wrap(draw,body_l,get_font(40,bold=False),cw)[:6]):
        draw.text((P,690+j*54),line,font=get_font(40,bold=False),fill=BLACK)
    for j,line in enumerate(wrap(draw,body_r,get_font(40,bold=False),cw)[:6]):
        draw.text((P+cw+40,690+j*54),line,font=get_font(40,bold=False),fill=BLACK)
    if stats4:
        draw.line([(P,1140),(W-P,1140)],fill="#CCCCCC",width=1)
        sw=(W-P*2)//len(stats4)
        for i,(v,l) in enumerate(stats4):
            x=P+i*sw; draw.text((x,1158),v,font=fit(draw,v,52,sw-16),fill=HERO_INK); draw.text((x,1220),l,font=fit(draw,l,20,sw-16,False),fill="#999999")
    draw.text((P,H-60),source,font=get_font(18,bold=False),fill=LGRAY)
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 12 — Yellow Grid  (ref: saffron bg, bold stacked)
# ══════════════════════════════════════════════════════════
def s12_grid(stacked_words, tag, grid_items, source="", bg=None, motif=None):
    """S12 in the geometric vibe: tint page, content shape band on top, black title, hairline grid of facts."""
    P=80; BG=_th("tint","#F2EDE4"); accent=_TH.get("accent",GREEN)
    img=Image.new("RGB",(W,H),BG); draw=ImageDraw.Draw(img)
    words=" ".join(stacked_words); first=grid_items[0][1] if grid_items else ""
    kind=motif_for(words+" "+" ".join(l for l,_v in grid_items), first)
    if kind in ("classic","share","crowd") or not first: kind="tiles" if kind=="classic" else kind
    if motif: kind=motif
    extra=max(0,4-max(1,(len(grid_items)+1)//2))*90      # fewer facts -> taller shape band
    box=(P,W-P,60,330+extra)
    _draw_motif(draw,kind,accent,BG,first,P,box)
    draw.text((W-P-draw.textbbox((0,0),tag,font=get_font(24))[2],352+extra),tag,font=get_font(24),fill="#444444")
    ty=392+extra
    for w in stacked_words:
        f=fit(draw,w,104,W-2*P); draw.text((P,ty),w,font=f,fill=BLACK); ty+=f.size+10
    ty+=14; draw.line([(P,ty),(W-P,ty)],fill=BLACK,width=3); ty+=34
    cw=(W-P*2-40)//2; n=len(grid_items)
    nrows=max(1,(n+1)//2); pitch=min(180,(H-150-ty)//nrows)
    vsz=min(fit(draw,v,54,cw-10).size for _l,v in grid_items) if grid_items else 50
    for i,(label,value) in enumerate(grid_items):
        x=P if i%2==0 else P+cw+40; row_y=ty+(i//2)*pitch
        draw.text((x,row_y),label.upper(),font=fit(draw,label.upper(),21,cw-10,False),fill="#444444")
        draw.text((x,row_y+34),value,font=get_font(vsz),fill=BLACK)
        draw.line([(x,row_y+pitch-30),(x+cw-10,row_y+pitch-30)],fill=_mix(BG,"#000000",0.25),width=1)
    logo(draw,P,H-88)
    draw.text((P,H-38),source,font=fit(draw,source,18,W-2*P,False,min_size=12),fill="#555555")
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 13 — Big Number  (ref: saffron bg, massive number)
# ══════════════════════════════════════════════════════════
def s13_bignum(bg, num_color, big_num, title_r, sub_r, grid_l, grid_r, source=""):
    P=70
    img=Image.new("RGB",(W,H),bg); draw=ImageDraw.Draw(img)
    # Logo top left — fixed position, no overlap
    logo(draw,P,P)
    for j,line in enumerate(wrap(draw,title_r,get_font(48),W//2-2*P)):
        draw.text((W//2+P,P+j*58),line,font=get_font(48),fill=BLACK)
    draw.line([(P,185),(W-P,185)],fill="#33333333",width=1)
    draw.line([(W//2,P),(W//2,185)],fill="#33333333",width=1)
    draw.text((P,200),sub_r,font=fit(draw,sub_r,24,W-2*P,False),fill="#555555")
    # Massive number
    draw.text((P-15,270),big_num,font=fit(draw,big_num,520,W-2*P+15),fill=HERO_INK)
    draw.line([(P,990),(W-P,990)],fill="#33333355",width=2)
    for i,(l,v) in enumerate(grid_l):
        y=1002+i*88; draw.text((P,y),l,font=get_font(20,bold=False),fill="#555555"); draw.text((P,y+26),v,font=fit(draw,v,40,W//2-P-20),fill=BLACK)
    for i,(l,v) in enumerate(grid_r):
        y=1002+i*88; draw.text((W//2+P,y),l,font=get_font(20,bold=False),fill="#555555"); draw.text((W//2+P,y+26),v,font=fit(draw,v,40,W//2-2*P),fill=BLACK)
    draw.line([(P,H-70),(W-P,H-70)],fill="#33333322",width=1)
    draw.text((P,H-52),source,font=get_font(18,bold=False),fill="#55555588")
    return save_buf(img)


# ─── QUICK TEST — renders all 13 to Desktop ───────────────
if __name__ == "__main__":
    out = os.path.expanduser("~/Desktop/design_library/")
    os.makedirs(out, exist_ok=True)

    tests = [
        ("s1_white",    s1_white("GDP GROWTH RATE","7.2%","Annual real GDP growth","green",
                            [("Rs.3.9T","NOMINAL GDP"),("5.0%","CPI INFLATION"),("Rs.83","USD / INR")],"Source: World Bank")),
        ("s2_bold",     s2_bold("INDIA'S POPULATION","1.44","green","BILLION","People call India home.",
                            [("77.7%","Literacy"),("70yr","Life Exp."),("36%","Urban")],"Young. Vast. Unstoppable.","Source: World Bank")),
        ("s3_vibrant",  s3_vibrant("DIGITAL","INDIA","111 Unicorns","green",
                            [("18.4B/mo","UPI TRANSACTIONS"),("Rs.245B","IT EXPORTS"),("52%","INTERNET")],"Source: DPIIT, NPCI")),
        ("s4_table",    s4_table("Kerala","Highest Literacy",{"gdp":10.2,"pop":35.7,"lit":96.2,"capital":"Thiruvananthapuram"})),
        ("s5_editorial",s5_editorial("TRADE &","FOREX SNAPSHOT","Rs.643B","4th largest globally","green",
                            [("Rs.432B","EXPORTS"),("Rs.83","USD/INR"),("Rs.90","EUR/INR"),("Rs.71B","FDI")],"Source: RBI, World Bank")),
        ("s6_numbers",  s6_numbers("ROAD &","HIGHWAY NETWORK","2025","63.7L","km","Total road network","green",
                            [("1.46L","km","National highways"),("3,052","km","Expressways"),("43%","","Paved")],"Source: MoRTH")),
        ("s7_chart",    s7_chart("HUMAN","DEVELOPMENT INDEX","0.644","Global Rank #132","amber",
                            [("2011-12",27.1),("2015-16",14.2),("2022-23",5.3),("2025",1.0)],
                            "~270M lifted out of poverty.",["Health: Rs.73/yr","Infant: 26/1000"],"Source: UNDP")),
        ("s8_forbes",   s8_forbes("India's Richest States",
                            "Maharashtra leads with Rs.36T. Top 5 states contribute 45%+ of India's GDP.",
                            [("MH",36.3),("TN",24.9),("KA",23.0),("UP",22.0),("GJ",21.0),("WB",15.6),("RJ",13.5),("TG",13.0)],
                            "State GDP (Rs. Trillion)","Source: State Reports, RBI")),
        ("s9_geometric",s9_geometric("GDP GROWTH RATE","7.2%","Annual real GDP growth — FY2024",BRAND,
                            [("Rs.3.9T","Nominal GDP"),("5.0%","Inflation"),("Rs.83","USD/INR")],"Source: World Bank")),
        ("s10_oversized",s10_oversized("7.2",
                            [("GDP Growth","India grew at 7.2% — fastest among major economies in 2024."),
                             ("Market Cap","Stock market crossed Rs.400T — 4th largest globally.")],
                            ["#D93025","#2196F3","#8BC34A"],"Source: World Bank, NSE")),
        ("s11_colorblock",s11_colorblock("#FF6B35","DIGITAL","INDIA",
                            "India has 111 unicorns and processes 18.4B UPI transactions every month.",
                            "With Rs.245B in IT exports, India is the world's largest digital services provider.",
                            [("111","Unicorns"),("18.4B","UPI/mo"),("Rs.245B","IT Exports"),("52%","Internet")],"Source: DPIIT, NPCI")),
        ("s12_grid",    s12_grid(["India","GDP","Data"],"FY 2024",
                            [("GDP Growth Rate","7.2% annual"),("Nominal GDP","Rs. 3.9 Trillion"),
                             ("Inflation CPI","5.0% annual"),("USD / INR","Rs. 83.5"),
                             ("Fiscal Deficit","3.2% of GDP"),("FDI Inflows","Rs. 71 Billion"),
                             ("Stock Market","Rs. 400 Trillion"),("Forex Reserves","Rs. 643 Billion")],"Source: World Bank, RBI")),
        ("s13_bignum",  s13_bignum("#FFC107","#D93025","7","India's GDP Growth Rate","2024  INDIA  ECONOMY",
                            [("GDP Growth","7.2% annual"),("Nominal GDP","Rs. 3.9T"),("Inflation","5.0%")],
                            [("USD/INR","Rs. 83.5"),("FDI","Rs. 71B"),("Forex","Rs. 643B")],"Source: World Bank, RBI")),
    ]

    for name,buf in tests:
        with open(f"{out}{name}.png","wb") as f: f.write(buf.read())
        print(f"  ✅ {name}")

    print(f"\n13 styles saved to {out}")
