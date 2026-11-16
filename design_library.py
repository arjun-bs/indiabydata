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
def s1_white(title, hero, hero_sub, hero_sent, stats, source, accent="#D4A017"):
    P=PAD; img=Image.new("RGB",(W,H),"#F5F4F0"); draw=ImageDraw.Draw(img)
    grid(draw); logo(draw,P,55)
    draw.text((P,160),"INDIA'S",font=get_font(60),fill=BLACK)
    ty=238
    for l in wrap(draw,title.upper(),get_font(60),W-P*2):
        draw.text((P,ty),l,font=get_font(60),fill=accent); ty+=75
    d1=460; draw.line([(P,d1),(W-P,d1)],fill="#CCCCCC",width=2)
    draw.text((P,d1+30),hero,font=fit(draw,hero,200,W-2*P),fill=hc(hero_sent))
    draw.text((P,d1+248),hero_sub,font=get_font(32,bold=False),fill=GRAY)
    d2=d1+322; draw.line([(P,d2),(W-P,d2)],fill="#CCCCCC",width=2)
    sy=d2+50
    for val,lbl in stats:
        vb=draw.textbbox((0,0),val,font=get_font(80))
        draw.text((P,sy),val,font=get_font(80),fill=BLACK)
        draw.text((P+vb[2]+18,sy+14),lbl,font=fit(draw,lbl,48,W-P-(P+vb[2]+18)),fill="#444444"); sy+=130
    draw.text((P,H-75),source,font=get_font(20,bold=False),fill=LGRAY)
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 2 — Bold Statement + Tricolor
# ══════════════════════════════════════════════════════════
def s2_bold(headline, number, hero_sent, number_unit, sub, stats3, note, source):
    P=PAD; img=Image.new("RGB",(W,H),"#FAF9F7"); draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,W,16],fill=BRAND); draw.rectangle([0,16,W,32],fill="#EEEEEE"); draw.rectangle([0,32,W,48],fill=GREEN)
    logo(draw,P,75)
    draw.text((P,188),headline,font=fit(draw,headline,60,W-2*P),fill=BLACK)
    draw.text((P,272),number,font=get_font(160),fill=hc(hero_sent))
    nw=draw.textbbox((0,0),number,font=get_font(160))[2]
    draw.text((P+nw+16,365),number_unit,font=get_font(60),fill=BRAND)
    draw.text((P,452),sub,font=fit(draw,sub,52,W-2*P),fill=BLACK)
    draw.line([(P,548),(W-P,548)],fill="#DDDDDD",width=1)
    cw=(W-P*2)//3
    for i,(v,l) in enumerate(stats3):
        x=P+i*cw; draw.text((x,578),v,font=fit(draw,v,80,cw-24),fill=BLACK); draw.text((x,678),l,font=get_font(24,bold=False),fill=GRAY)
    draw.line([(P,758),(W-P,758)],fill="#DDDDDD",width=1)
    draw.rectangle([P,778,W-P,798],fill=BRAND); draw.rectangle([P,798,W-P,818],fill="#EEEEEE"); draw.rectangle([P,818,W-P,838],fill=GREEN)
    draw.text((P,858),note,font=fit(draw,note,48,W-2*P),fill="#222222")
    draw.text((P,H-75),source,font=get_font(20,bold=False),fill=LGRAY)
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 3 — Vibrant White + Grid
# ══════════════════════════════════════════════════════════
def s3_vibrant(title_top, title_bot, hero_val, hero_sent, cards3, source):
    P=PAD; img=Image.new("RGB",(W,H),"#F5F4F0"); draw=ImageDraw.Draw(img)
    grid(draw); draw.rectangle([0,0,W,10],fill=BRAND); logo(draw,P,58)
    draw.text((P,165),title_top,font=fit(draw,title_top,130,W-2*P),fill=BRAND)
    draw.text((P,315),title_bot,font=fit(draw,title_bot,130,W-2*P),fill=BLACK)
    draw.line([(P,475),(W-P,475)],fill="#CCCCCC",width=2)
    draw.rounded_rectangle([P,500,W-P,690],radius=12,fill="#FFFFFF")
    draw.rounded_rectangle([P,500,P+6,690],radius=3,fill=hc(hero_sent))
    draw.text((P+24,518),"HEADLINE STAT",font=get_font(22,bold=False),fill=GRAY)
    draw.text((P+24,552),hero_val,font=fit(draw,hero_val,110,W-2*P-48),fill=hc(hero_sent))
    cw=(W-P*2-20)//2
    for i,(val,lbl) in enumerate(cards3):
        x=P if i%2==0 else P+cw+20; y=715+(i//2)*230
        draw.rounded_rectangle([x,y,x+cw,y+200],radius=12,fill="#FFFFFF")
        draw.rounded_rectangle([x,y,x+cw,y+6],radius=3,fill=hc(hero_sent))
        draw.text((x+22,y+22),lbl,font=get_font(22,bold=False),fill=GRAY)
        draw.text((x+22,y+58),val,font=fit(draw,val,72,cw-44),fill=BLACK)
    draw.text((P,H-75),source,font=get_font(20,bold=False),fill=LGRAY)
    draw.rectangle([0,H-10,W,H],fill=BRAND)
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 4 — Data Table Clean
# ══════════════════════════════════════════════════════════
def s4_table(name, known, info):
    P=PAD; img=Image.new("RGB",(W,H),"#FFFFFF"); draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,16,H],fill=BRAND); logo(draw,P,58)
    draw.text((P,155),"STATE SPOTLIGHT",font=get_font(24,bold=False),fill="#999999")
    draw.text((P,192),name.upper(),font=fit(draw,name.upper(),120,W-2*P),fill=BLACK)
    draw.text((P,338),known,font=get_font(32),fill=BRAND)
    draw.line([(P,400),(W-P,400)],fill="#EEEEEE",width=2)
    c1=P; c2=P+380; c3=P+680
    for x,c in zip([c1,c2,c3],["METRIC","VALUE","INSIGHT"]):
        draw.rectangle([x,410,x+360,452],fill="#F5F5F5"); draw.text((x+10,422),c,font=get_font(20,bold=False),fill="#999999")
    gdp_pc=round(info['gdp']*1e12/(info['pop']*1e6)/1000)
    rows=[("State GDP",f"Rs. {info['gdp']}T","Top 5 in India"),("Population",f"{info['pop']}M","Census data"),
          ("Literacy Rate",f"{info['lit']}%","Natl avg 77.7%"),("GDP Per Capita",f"Rs. {gdp_pc}K","Annual"),("Capital City",info["capital"],"Admin HQ")]
    for i,(m,v,r) in enumerate(rows):
        y=462+i*112; draw.rectangle([P,y,W-P,y+102],fill="#FAFAFA" if i%2==0 else "#FFFFFF")
        draw.line([(P,y+102),(W-P,y+102)],fill="#EEEEEE",width=1)
        draw.text((c1+8,y+32),m,font=get_font(28),fill="#333333")
        draw.text((c2+8,y+32),v,font=get_font(28),fill=BLACK)
        draw.text((c3+8,y+32),r,font=get_font(24,bold=False),fill=GRAY)
    draw.rounded_rectangle([P,1038,W-P,1225],radius=8,fill="#FFF8F0")
    pct=round(info['gdp']/160*100,1)
    draw.text((P+18,1062),"DID YOU KNOW?",font=get_font(20,bold=False),fill=BRAND)
    draw.text((P+18,1096),f"{name} contributes",font=get_font(32),fill=BLACK)
    draw.text((P+18,1142),f"{pct}% of India's total GDP",font=get_font(72),fill=GREEN)
    draw.text((P,H-75),f"Source: Census, State Economic Survey",font=get_font(20,bold=False),fill=LGRAY)
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 5 — Editorial White + Grid
# ══════════════════════════════════════════════════════════
def s5_editorial(title1, title2, hero, hero_sub, hero_sent, cards4, source):
    P=PAD; gold="#D4A017"
    img=Image.new("RGB",(W,H),"#F5F4F0"); draw=ImageDraw.Draw(img)
    grid(draw); draw.rectangle([0,0,8,H],fill=gold); logo(draw,P,55)
    draw.text((P,158),title1,font=get_font(60),fill=BLACK)
    draw.text((P,238),title2,font=get_font(60),fill=gold)
    draw.line([(P,322),(W-P,322)],fill="#CCCCCC",width=2)
    draw.text((P,348),hero,font=get_font(160),fill=hc(hero_sent))
    draw.text((P,532),hero_sub,font=get_font(26,bold=False),fill=GRAY)
    draw.line([(P,608),(W-P,608)],fill="#CCCCCC",width=2)
    cw=(W-P*2-20)//2
    for i,(val,lbl) in enumerate(cards4):
        x=P if i%2==0 else P+cw+20; y=635+(i//2)*235
        draw.rounded_rectangle([x,y,x+cw,y+205],radius=12,fill="#FFFFFF")
        draw.rounded_rectangle([x,y,x+cw,y+6],radius=3,fill=gold)
        draw.text((x+22,y+22),lbl,font=get_font(20,bold=False),fill=GRAY)
        draw.text((x+22,y+58),val,font=fit(draw,val,72,cw-44),fill=BLACK)
    draw.text((P,H-75),source,font=get_font(20,bold=False),fill=LGRAY)
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 6 — Large Numbers
# ══════════════════════════════════════════════════════════
def s6_numbers(title1, title2, year, hero_num, hero_unit, hero_label, hero_sent, items3, source, accent=GREEN):
    P=PAD; img=Image.new("RGB",(W,H),"#F8F8F6"); draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,W,10],fill=accent); logo(draw,P,58)
    draw.text((P,158),title1,font=get_font(60),fill=BLACK)
    draw.text((P,238),title2,font=get_font(60),fill=accent)
    draw.text((P,315),year,font=get_font(60),fill=BLACK)
    draw.line([(P,395),(W-P,395)],fill="#DDDDDD",width=2)
    nw=draw.textbbox((0,0),hero_num,font=get_font(120))[2]
    draw.text((P,415),hero_num,font=get_font(120),fill=hc(hero_sent))
    if hero_unit: draw.text((P+nw+12,462),hero_unit,font=get_font(56),fill=GRAY)
    draw.text((P,558),hero_label,font=get_font(30),fill=GRAY)
    draw.line([(P,618),(W-P,618)],fill="#EEEEEE",width=1)
    for i,(num,unit,label) in enumerate(items3):
        y=645+i*205; draw.line([(P,y+195),(W-P,y+195)],fill="#EEEEEE",width=1)
        nw2=draw.textbbox((0,0),num,font=get_font(120))[2]
        draw.text((P,y+12),num,font=get_font(120),fill=BLACK)
        if unit: draw.text((P+nw2+12,y+58),unit,font=get_font(56),fill=GRAY)
        draw.text((P,y+145),label,font=get_font(30),fill=GRAY)
    draw.text((P,H-75),source,font=get_font(20,bold=False),fill=LGRAY)
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 7 — Bar Chart
# ══════════════════════════════════════════════════════════
def s7_chart(title1, title2, hero, hero_sub, hero_sent, bars, callout, stats2, source, accent="#7B5EA7"):
    P=PAD; img=Image.new("RGB",(W,H),"#FFFFFF"); draw=ImageDraw.Draw(img)
    logo(draw,P,58)
    draw.text((P,158),title1,font=get_font(60),fill=BLACK)
    draw.text((P,238),title2,font=get_font(60),fill=accent)
    draw.line([(P,322),(W-P,322)],fill="#EEEEEE",width=2)
    draw.text((P,342),hero,font=fit(draw,hero,200,W-2*P),fill=hc(hero_sent))
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
    img=Image.new("RGB",(W,H),"#F7F6F2"); draw=ImageDraw.Draw(img)
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
def s9_geometric(stat_label, hero_val, stat_sub, color=BRAND, stats3=[], source=""):
    P=80; BG="#F2EDE4"
    img=Image.new("RGB",(W,H),BG); draw=ImageDraw.Draw(img)
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
    # Divider + text grid
    draw.line([(P,660),(W-P,660)],fill="#BBAA99",width=1)
    if stats3:
        cw=(W-P*2)//3
        for i,(v,l) in enumerate(stats3):
            x=P+i*cw
            if i>0: draw.line([(x,680),(x,780)],fill="#BBAA99",width=1)
            draw.text((x+(15 if i>0 else 0),686),l.upper(),font=fit(draw,l.upper(),20,cw-30,False),fill="#888888")
            draw.text((x+(15 if i>0 else 0),715),v,font=fit(draw,v,50,cw-30),fill=BLACK)
    draw.text((P,810),stat_label,font=fit(draw,stat_label,26,W-2*P,False),fill="#999999")
    draw.text((P,845),stat_sub,font=fit(draw,stat_sub,26,W-2*P,False),fill="#999999")
    draw.text((P-10,940),hero_val,font=fit(draw,hero_val,280,W-2*P+10),fill=color)
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
    img=Image.new("RGB",(W,H),"#EFEFEF"); draw=ImageDraw.Draw(img)
    draw.rectangle([0,0,W,560],fill=block_color)
    draw.text((P,70),line1,font=fit(draw,line1,120,W-2*P),fill=BLACK)
    draw.text((P,200),line2,font=fit(draw,line2,120,W-2*P),fill=BLACK)
    logo(draw,P,470)
    cw=(W-P*2-40)//2
    draw.text((P,620),"INDIA BY DATA",font=get_font(20,bold=False),fill="#999999")
    draw.line([(P,655),(W-P,655)],fill="#CCCCCC",width=1)
    for j,line in enumerate(wrap(draw,body_l,get_font(30,bold=False),cw)):
        draw.text((P,670+j*42),line,font=get_font(30,bold=False),fill=BLACK)
    for j,line in enumerate(wrap(draw,body_r,get_font(30,bold=False),cw)):
        draw.text((P+cw+40,670+j*42),line,font=get_font(30,bold=False),fill=BLACK)
    if stats4:
        draw.line([(P,1140),(W-P,1140)],fill="#CCCCCC",width=1)
        sw=(W-P*2)//len(stats4)
        for i,(v,l) in enumerate(stats4):
            x=P+i*sw; draw.text((x,1158),v,font=fit(draw,v,52,sw-16),fill=block_color); draw.text((x,1220),l,font=fit(draw,l,20,sw-16,False),fill="#999999")
    draw.text((P,H-60),source,font=get_font(18,bold=False),fill=LGRAY)
    return save_buf(img)

# ══════════════════════════════════════════════════════════
# STYLE 12 — Yellow Grid  (ref: saffron bg, bold stacked)
# ══════════════════════════════════════════════════════════
def s12_grid(stacked_words, tag, grid_items, source=""):
    P=70; SAFFRON="#FFC107"
    img=Image.new("RGB",(W,H),SAFFRON); draw=ImageDraw.Draw(img)
    draw.text((W-P-200,P),tag,font=get_font(24),fill=BLACK)
    ty=115
    for w in stacked_words:
        draw.text((P,ty),w,font=fit(draw,w,130,W-2*P),fill=BLACK); ty+=138
    draw.line([(P,ty+10),(W-P,ty+10)],fill="#333333",width=2); ty+=40
    draw.text((P,ty),"IndiaByData  •  Data Journalism",font=get_font(22,bold=False),fill="#555555"); ty+=44
    draw.line([(P,ty),(W-P,ty)],fill="#33333355",width=1); ty+=30
    cw=(W-P*2-40)//2
    for i,(label,value) in enumerate(grid_items):
        x=P if i%2==0 else P+cw+40; row_y=ty+(i//2)*148
        draw.text((x,row_y),label,font=fit(draw,label,22,cw-10,False),fill="#333333")
        draw.text((x,row_y+32),value,font=fit(draw,value,42,cw-10),fill=BLACK)
        draw.line([(x,row_y+92),(x+cw-10,row_y+92)],fill="#33333333",width=1)
    logo(draw,P,H-90); draw.text((P+240,H-75),source,font=get_font(18,bold=False),fill="#555555")
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
    draw.text((P-15,270),big_num,font=fit(draw,big_num,520,W-2*P+15),fill=num_color)
    draw.line([(P,990),(W-P,990)],fill="#33333355",width=2)
    for i,(l,v) in enumerate(grid_l):
        y=1010+i*100; draw.text((P,y),l,font=get_font(20,bold=False),fill="#555555"); draw.text((P,y+26),v,font=fit(draw,v,40,W//2-P-20),fill=BLACK)
    for i,(l,v) in enumerate(grid_r):
        y=1010+i*100; draw.text((W//2+P,y),l,font=get_font(20,bold=False),fill="#555555"); draw.text((W//2+P,y+26),v,font=fit(draw,v,40,W//2-2*P),fill=BLACK)
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
