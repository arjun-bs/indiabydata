#!/usr/bin/env python3
"""
IndiaByData — 4 Posts Daily Auto Poster
Posts at peak India Instagram times:
  8:00 AM  — Economy / Finance
  1:00 PM  — Demographics / Social
  6:00 PM  — Tech / Infrastructure
  9:00 PM  — State Spotlight / Special

4 posts x 7 days x 4 weeks = 112 unique posts before any repeat.
Run: python3 post.py [morning|afternoon|evening|night|auto]
"""

import requests, io, os, base64, time
from datetime import datetime
from zoneinfo import ZoneInfo

def now_ist(): return datetime.now(ZoneInfo('Asia/Kolkata'))

import sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import design_library as _dl
import trends
from design_library import GREEN, RED, BLACK, BRAND, hc

def s4_table(name, known, info):
    if geo_slot():
        gdp_pc = round(info['gdp'] * 1e12 / (info['pop'] * 1e6) / 1000)
        return _s9(f"State spotlight: {name}", f"Rs. {info['gdp']}T", known,
                   [(f"{info['pop']}M", "Population"), (f"{info['lit']}%", "Literacy"), (f"Rs. {gdp_pc}K", "GDP per capita")],
                   "Source: Census, State Economic Survey", "tiles")
    if use_swiss():
        gdp_pc = round(info['gdp'] * 1e12 / (info['pop'] * 1e6) / 1000)
        items = [("State GDP (top 5 in India)", f"Rs. {info['gdp']}T"), ("Population", f"{info['pop']}M"),
                 ("Literacy (India avg 77.7%)", f"{info['lit']}%"), ("GDP per capita", f"Rs. {gdp_pc}K"),
                 ("Capital", info["capital"]), ("Known for", known),
                 ("Share of India GDP", f"{round(info['gdp']/160*100, 1)}%")]
        return _mark("S12", _dl.s12_grid(["STATE", name.upper()], "SPOTLIGHT", items, "Source: Census, State Economic Survey", motif="tiles"))
    return _mark("S4", _dl.s4_table(name, known, info))

# Ranking charts must be in descending order (comparison charts keep India first on purpose)
SORTED_CHARTS = ("India's Most Populated States", "India's Urbanisation by State")
def s8_forbes(title, subtitle, bars, unit_label, source, bar_colors=None):
    if title in SORTED_CHARTS:
        bars = sorted(bars, key=lambda x: -x[1])
    if geo_slot() and len(bars) >= 3:
        u = str(unit_label).strip().lstrip("#").strip()
        short = u if len(u) <= 3 else ""                       # long unit labels are descriptions, not suffixes
        top = bars[0]
        return _s9(title, f"{top[1]:g}{short}", f"{top[0]} - {u if not short else subtitle}",
                   [(f"{v:g}{short}", n) for n, v in bars[1:4]], source)
    return _mark("S8", _dl.s8_forbes(title, subtitle, bars, unit_label, source, bar_colors))

def s7_chart(title1, title2, hero, hero_sub, hero_sent, bars, callout, stats2, source, accent="#7B5EA7"):
    if geo_slot() and len(bars) >= 3:
        return _s9(f"{title1} {title2}", hero, hero_sub, [(f"{v:g}", n) for n, v in bars[:3]], source)
    return _mark("S7", _dl.s7_chart(title1, title2, hero, hero_sub, hero_sent, bars, callout, stats2, source, accent))

# ─── SWISS LAYOUT MIX ─────────────────────────────────────
# The same verified data is shown in the original layout (S1/S2/S3/S5/S6)
# or its Swiss counterpart (S9/S13/S12/S11/S10). Swiss is used on alternate
# days; override with env SWISS=1 (always) or SWISS=0 (never).
_SLOT_IDX = {"8AM": 0, "1PM": 1, "6PM": 2, "9PM": 3}
CURRENT_SLOT = 0

def use_swiss():
    """Posts alternate classic/Swiss through the day (8AM, 1PM, 6PM, 9PM); the pattern flips every day."""
    m = os.environ.get("SWISS", "auto")
    if m in ("0", "1"): return m == "1"
    return (CURRENT_SLOT + now_ist().toordinal()) % 2 == 1

def apply_theme(offset=0):
    """Pick today's colour theme. The 4 posts of a day get 4 different colours; the set shifts every day.
    THEME env: 'off' = original colours, a number = force that palette."""
    m = os.environ.get("THEME", "auto")
    if m == "off": return _dl.set_theme(None)
    if m.isdigit(): return _dl.set_theme(int(m), int(m))
    pal, acc = _dl.rotation(now_ist().toordinal() * 4 + CURRENT_SLOT + offset)
    return _dl.set_theme(pal, acc)

LAST_STYLE = ""

def geo_slot():
    """True when this post uses the geometric (S9) look. Guaranteed every day: the first Swiss slot always,
    the second Swiss slot too on even days (so 1 or 2 geometric posts a day). GEO=1/0 forces on/off."""
    m = os.environ.get("GEO", "auto")
    if m in ("0", "1"): return m == "1"
    if not use_swiss(): return False
    o = now_ist().toordinal()
    swiss = [s for s in range(4) if (s + o) % 2 == 1]
    return CURRENT_SLOT == swiss[0] or (o % 2 == 0 and CURRENT_SLOT == swiss[1])

def _s9(label, hero, sub, stats, source, motif=None):
    global LAST_STYLE; LAST_STYLE = "S9"
    return _dl.s9_geometric(str(label).upper(), str(hero), str(sub), GREEN, [(str(v), str(l)) for v, l in list(stats)[:3]], source, motif)

def _mark(name, buf):
    global LAST_STYLE; LAST_STYLE = name; return buf

def s1_white(title, hero, hero_sub, hero_sent, stats, source, accent="#D4A017", kicker="INDIA'S"):
    if use_swiss():
        label = title.upper() if kicker == "INDIA'S" else f"{kicker}: {title}".upper()
        return _s9(label, hero, hero_sub, stats, source)
    return _mark("S1", _dl.s1_white(title, hero, hero_sub, hero_sent, stats, source, accent, kicker))

def s2_bold(headline, number, hero_sent, number_unit, sub, stats3, note, source):
    if geo_slot():
        u = str(number_unit).strip()
        return _s9(headline, str(number) + (u if len(u) <= 3 else ""), sub if len(u) <= 3 else f"{u} - {sub}", stats3, source)
    if use_swiss():
        col = {"green": GREEN, "red": RED}.get(hero_sent, BLACK)
        big = str(number) + (number_unit if len(str(number_unit).strip()) <= 3 else "")
        attached = big != str(number)
        sub_r = sub if attached else f"{number} {str(number_unit).lower()} - {sub}"
        return _mark("S13", _dl.s13_bignum(_dl._th("mid", "#FFC107"), col, big, headline, sub_r,
                              [(l, v) for v, l in stats3][:3],
                              [("Takeaway", note)], source))
    return _mark("S2", _dl.s2_bold(headline, number, hero_sent, number_unit, sub, stats3, note, source))

def s3_vibrant(title_top, title_bot, hero_val, hero_sent, cards3, source):
    if geo_slot():
        return _s9(f"{title_top} {title_bot}", hero_val, "", cards3, source)
    if use_swiss():
        items = [("Headline stat", hero_val)] + [(l, v) for v, l in cards3]
        return _mark("S12", _dl.s12_grid([title_top, title_bot], str(now_ist().year), items[:4], source))
    return _mark("S3", _dl.s3_vibrant(title_top, title_bot, hero_val, hero_sent, cards3, source))

def s5_editorial(title1, title2, hero, hero_sub, hero_sent, cards4, source):
    if geo_slot():
        return _s9(f"{title1} {title2}", hero, hero_sub, cards4, source)
    if use_swiss():
        return _mark("S11", _dl.s11_colorblock(_dl._th("bold", BRAND), title1, title2, f"{hero} - {hero_sub}",
                                  "Data: " + source.replace("Source: ", ""), list(cards4)[:4], source))
    return _mark("S5", _dl.s5_editorial(title1, title2, hero, hero_sub, hero_sent, cards4, source))

def s6_numbers(title1, title2, year, hero_num, hero_unit, hero_label, hero_sent, items3, source, accent=GREEN):
    if geo_slot():
        u = str(hero_unit).strip()
        big = str(hero_num) + (u if u and len(u) <= 3 and not u.isalpha() else "")
        return _s9(f"{title1} {title2} {year}".strip(), big, hero_label, [(f"{n} {uu}".strip(), l) for n, uu, l in items3], source)
    if use_swiss():
        unit = str(hero_unit).strip()
        big = str(hero_num) + (unit if unit and len(unit) <= 3 and not unit.isalpha() else "")
        title_bot = f"{title2.title()} {year}".strip().upper() if False else f"{title2} {year}".strip()
        cards = [(f"{n} {u}".replace("  ", " ").strip(), l) for n, u, l in items3][:3]
        return _mark("S3", _dl.s3_vibrant(title1, title_bot, big, hero_sent, cards, source))
    return _mark("S6", _dl.s6_numbers(title1, title2, year, hero_num, hero_unit, hero_label, hero_sent, items3, source, accent))

import os, sys
def _need(name):
    v = os.environ.get(name)
    if not v:
        sys.exit(f"Missing {name}. In Terminal run:  export {name}=\"your_value\"  then run this script again.")
    return v
ACCESS_TOKEN  = _need("IG_TOKEN")
IMGBB_API_KEY = _need("IMGBB_KEY")
SLOT_MORNING   = "08:00"   # Morning commute — highest reach
SLOT_AFTERNOON = "13:00"   # Lunch break
SLOT_EVENING   = "18:00"   # After work / commute home
SLOT_NIGHT     = "21:00"   # Prime time — highest engagement

# ─── STATES ───────────────────────────────────────────────
STATES = [
    ("Maharashtra","Financial Capital",{"gdp":36.3,"pop":126.4,"lit":82.3,"capital":"Mumbai"}),
    ("Tamil Nadu","Auto & IT Hub",{"gdp":24.9,"pop":77.8,"lit":82.3,"capital":"Chennai"}),
    ("Karnataka","Silicon Valley of India",{"gdp":23.0,"pop":67.6,"lit":77.2,"capital":"Bengaluru"}),
    ("Uttar Pradesh","Most Populous State",{"gdp":22.0,"pop":235.0,"lit":67.7,"capital":"Lucknow"}),
    ("Gujarat","Growth Engine",{"gdp":21.0,"pop":63.9,"lit":82.4,"capital":"Gandhinagar"}),
    ("Rajasthan","Largest by Area",{"gdp":13.5,"pop":81.0,"lit":66.1,"capital":"Jaipur"}),
    ("West Bengal","Cultural Capital",{"gdp":15.6,"pop":99.6,"lit":76.3,"capital":"Kolkata"}),
    ("Telangana","Pharma & IT Hub",{"gdp":13.0,"pop":39.4,"lit":72.8,"capital":"Hyderabad"}),
    ("Kerala","Highest Literacy",{"gdp":10.2,"pop":35.7,"lit":96.2,"capital":"Thiruvananthapuram"}),
    ("Delhi","National Capital",{"gdp":9.5,"pop":32.0,"lit":86.2,"capital":"New Delhi"}),
    ("Punjab","Granary of India",{"gdp":7.2,"pop":30.1,"lit":75.8,"capital":"Chandigarh"}),
    ("Andhra Pradesh","Rice Bowl of India",{"gdp":12.5,"pop":54.0,"lit":67.0,"capital":"Amaravati"}),
    ("Madhya Pradesh","Heart of India",{"gdp":12.0,"pop":85.0,"lit":69.3,"capital":"Bhopal"}),
    ("Haryana","Automobile Hub",{"gdp":9.0,"pop":28.9,"lit":75.6,"capital":"Chandigarh"}),
    ("Bihar","Ancient Civilization",{"gdp":7.5,"pop":128.5,"lit":61.8,"capital":"Patna"}),
    ("Odisha","Mineral Rich State",{"gdp":7.2,"pop":46.4,"lit":72.9,"capital":"Bhubaneswar"}),
    ("Assam","Tea Capital of India",{"gdp":4.5,"pop":35.6,"lit":72.2,"capital":"Dispur"}),
    ("Goa","Tourism Capital",{"gdp":1.0,"pop":1.6,"lit":88.7,"capital":"Panaji"}),
    ("Himachal Pradesh","Dev Bhoomi",{"gdp":2.0,"pop":7.3,"lit":82.8,"capital":"Shimla"}),
    ("Uttarakhand","Land of Gods",{"gdp":3.0,"pop":11.3,"lit":78.8,"capital":"Dehradun"}),
    ("Jharkhand","Mining State",{"gdp":4.2,"pop":38.6,"lit":66.4,"capital":"Ranchi"}),
    ("Chhattisgarh","Rice Bowl Central",{"gdp":4.5,"pop":29.4,"lit":70.3,"capital":"Raipur"}),
    ("Tripura","Gateway to NE India",{"gdp":0.8,"pop":4.2,"lit":87.2,"capital":"Agartala"}),
    ("Manipur","Jewel of India",{"gdp":0.6,"pop":3.2,"lit":76.9,"capital":"Imphal"}),
    ("Meghalaya","Scotland of the East",{"gdp":0.7,"pop":3.4,"lit":74.4,"capital":"Shillong"}),
    ("Mizoram","Highest Literacy NE",{"gdp":0.4,"pop":1.3,"lit":91.3,"capital":"Aizawl"}),
    ("Sikkim","India's Organic State",{"gdp":0.4,"pop":0.7,"lit":81.4,"capital":"Gangtok"}),
    ("Nagaland","Land of Festivals",{"gdp":0.4,"pop":2.2,"lit":79.6,"capital":"Kohima"}),
    ("Arunachal Pradesh","Land of Rising Sun",{"gdp":0.5,"pop":1.6,"lit":65.4,"capital":"Itanagar"}),
    ("J&K","Paradise on Earth",{"gdp":2.2,"pop":14.0,"lit":67.2,"capital":"Srinagar"}),
]
def get_state(offset=0):
    wk=now_ist().isocalendar()[1]
    return STATES[(wk+offset) % len(STATES)]

def wb(ind,fb):
    try:
        v=requests.get(f"https://api.worldbank.org/v2/country/IN/indicator/{ind}?format=json&mrv=1",timeout=10).json()[1][0]["value"]
        return round(v,1) if v else fb
    except: return fb

def fx():
    try:
        r=requests.get("https://open.er-api.com/v6/latest/USD",timeout=8).json()["rates"]
        return round(r["INR"],2),round(r["INR"]/r["EUR"],2),round(r["INR"]/r["GBP"],2)
    except: return 88.0,95.0,112.0

# ══════════════════════════════════════════════════════════
# SLOT 1 — MORNING 8AM  (Economy / Finance)
# 28 rotating topics over 4 weeks × 7 days
# ══════════════════════════════════════════════════════════
MORNING_TOPICS = {
    # Week 0
    (0,0): lambda: (s1_white("GDP GROWTH RATE",f"{wb('NY.GDP.MKTP.KD.ZG',7.2)}%","Annual real GDP growth","green" if wb('NY.GDP.MKTP.KD.ZG',7.2)>=6 else "amber",[(f"${round(wb('NY.GDP.MKTP.CD',3.7e12)/1e12,2)}T","NOMINAL GDP"),(f"{wb('FP.CPI.TOTL.ZG',5.1)}%","CPI INFLATION"),(f"Rs.{fx()[0]}","USD / INR")],"Source: World Bank"),"India's GDP — one of the fastest growing major economies.\n\n#IndiaGDP #IndiaEconomy #MoneyMonday #IndiaByData"),
    (0,1): lambda: (s1_white("INFLATION RATE",f"{wb('FP.CPI.TOTL.ZG',5.1)}%","Consumer Price Index annual","amber",[("7.2%","GDP GROWTH RATE"),(f"Rs.{fx()[0]}","USD / INR"),("3.2%","FISCAL DEFICIT/GDP")],"Source: World Bank, RBI"),"India's inflation is moderating. Here's the full picture.\n\n#IndiaInflation #RBI #IndiaEconomy #IndiaByData"),
    (0,2): lambda: (s1_white("FOREX RESERVES","$643B","4th largest globally","green",[("$432B","MERCHANDISE EXPORTS"),(f"Rs.{fx()[0]}","LIVE USD/INR"),("$71B","FDI INFLOWS")],"Source: RBI, World Bank"),"India's forex reserves hit $643B — 4th largest in the world.\n\n#IndiaForex #RBI #IndiaEconomy #IndiaByData"),
    (0,3): lambda: (s1_white("UNION BUDGET","Rs.48.2L Cr","Total Budget 2024-25","green",[("3.2%","FISCAL DEFICIT/GDP"),("Rs.11.1L Cr","CAPEX"),("Rs.10.2L Cr","TAX COLLECTION")],"Source: Ministry of Finance"),"India's Union Budget 2024-25 — Rs.48.2 lakh crore. Where does it go?\n\n#IndiaBudget #UnionBudget #IndiaEconomy #IndiaByData"),
    (0,4): lambda: (s1_white("STOCK MARKET","Rs.400T+","NSE + BSE combined market cap","green",[("5,900+","LISTED COMPANIES"),("Rs.18,500","NIFTY 50"),("#4","GLOBALLY")],"Source: NSE, BSE India"),"India's stock market is the 4th largest in the world.\n\n#IndiaStockMarket #NSE #Nifty #IndiaByData"),
    (0,5): lambda: (s1_white("BANKING SECTOR","Rs.210L Cr","Total bank deposits","green",[("12","PUBLIC SECTOR BANKS"),("156M","JAN DHAN ACCOUNTS"),("Rs.62L Cr","BANK CREDIT")],"Source: RBI"),"India's banking sector — Rs.210 lakh crore in deposits.\n\n#IndiaBanking #RBI #JanDhan #IndiaByData"),
    (0,6): lambda: (s1_white("FDI INFLOWS","$71B","Foreign Direct Investment FY2024","green",[("$16B","SERVICES SECTOR"),("$6.5B","COMPUTER HARDWARE"),("$5.5B","TELECOM")],"Source: DIPP, RBI"),"India attracted $71B in FDI — a record.\n\n#IndiaFDI #ForeignInvestment #IndiaEconomy #IndiaByData"),
    # Week 1
    (1,0): lambda: (s1_white("TRADE EXPORTS","$432B","Total merchandise exports FY2024","green",[("$88B","PETROLEUM"),("$30B","IT SERVICES"),("$17B","GEMS")],"Source: DGFT"),"India's exports crossed $432B in FY2024.\n\n#IndiaExports #IndiaTrade #IndiaByData"),
    (1,1): lambda: (s1_white("GST COLLECTION","Rs.2.1L Cr","Monthly GST revenue (peak)","green",[("Rs.20L Cr","Annual GST total"),("1.4Cr","GST filers"),("3%","Avg growth/month")],"Source: Ministry of Finance"),"India's GST collections hitting record highs month after month.\n\n#IndiaGST #IndiaEconomy #IndiaByData"),
    (1,2): lambda: (s1_white("AGRI EXPORTS","$55B","Total agri exports FY2024","green",[("$11B","RICE - #1 GLOBALLY"),("$5B","SPICES"),("$4.5B","VEGETABLES")],"Source: APEDA"),"India is the world's #1 rice exporter. Total agri exports: $55B.\n\n#IndiaAgriculture #AgriExports #IndiaByData"),
    (1,3): lambda: (s1_white("REMITTANCES","$120B","India receives most globally","green",[("#1","GLOBAL RECIPIENT"),("32M","INDIANS ABROAD"),("110+","COUNTRIES")],"Source: World Bank, MEA"),"India receives $120B in remittances — the world's largest.\n\n#IndianDiaspora #NRI #Remittances #IndiaByData"),
    (1,4): lambda: (s1_white("PHARMA EXPORTS","$27B","India's pharmacy of the world","green",[("60,000+","PHARMA COMPANIES"),("#3","GLOBALLY BY VOLUME"),("200+","COUNTRIES SERVED")],"Source: Pharmexcil"),"India supplies 20% of global generic medicines.\n\n#IndiaPharma #IndiaExports #IndiaByData"),
    (1,5): lambda: (s1_white("MSME SECTOR","33%","MSME contribution to GDP","amber",[("6.3Cr","MSME UNITS"),("11Cr","PEOPLE EMPLOYED"),("Rs.8L Cr","ANNUAL OUTPUT")],"Source: Ministry of MSME"),"India's 63 million MSMEs are the backbone of the economy.\n\n#IndiaMSME #MakeInIndia #IndiaByData"),
    (1,6): lambda: (s1_white("GOLD IMPORTS","$35B","Annual gold imports","amber",[("#2","LARGEST CONSUMER"),("800T","ANNUAL DEMAND"),("Rs.40L Cr","HOUSEHOLD HOLDINGS")],"Source: World Gold Council"),"India holds 25,000 tonnes of gold — one of the largest hoards globally.\n\n#IndiaGold #IndiaEconomy #IndiaByData"),
    # Week 2
    (2,0): lambda: (s1_white("CRUDE OIL","$88B","Annual crude oil imports","red",[("85%","IMPORT DEPENDENT"),("#3","LARGEST IMPORTER"),(f"Rs.{fx()[0]}","USD/INR IMPACT")],"Source: PPAC, IEA"),"India imports 85% of its crude oil. Here's the full picture.\n\n#IndiaCrudeOil #IndiaEnergy #IndiaByData"),
    (2,1): lambda: (s1_white("DEFENCE BUDGET","Rs.6.2L Cr","Union Budget 2024-25","green",[("2.3%","OF GDP"),("Rs.1.7L Cr","CAPITAL OUTLAY"),("$2.5B","DEFENCE EXPORTS")],"Source: Ministry of Defence"),"India's defence budget hits Rs.6.2 lakh crore.\n\n#IndiaDefence #IndiaArmy #IndiaByData"),
    (2,2): lambda: (s1_white("INSURANCE SECTOR","$131B","Total insurance premium","amber",[("4.2%","PENETRATION RATE"),("500M","INSURED PEOPLE"),("Rs.24L Cr","TOTAL ASSETS")],"Source: IRDAI"),"India's insurance sector is one of the fastest growing globally.\n\n#IndiaInsurance #IndiaFinance #IndiaByData"),
    (2,3): lambda: (s1_white("MUTUAL FUNDS","Rs.54L Cr","Total AUM under management","green",[("16Cr","SIP ACCOUNTS"),("Rs.20,000Cr","MONTHLY SIP FLOW"),("43%","EQUITY SHARE")],"Source: AMFI"),"India's mutual fund AUM crossed Rs.54 lakh crore.\n\n#IndiaMutualFunds #SIP #IndiaInvesting #IndiaByData"),
    (2,4): lambda: (s1_white("REAL ESTATE","$300B","Market size 2024","green",[("13%","GDPCONTRIBUTION"),("7Cr","HOMES NEEDED BY 2030"),("20%","YOY GROWTH")],"Source: JLL, CREDAI"),"India's real estate market is booming — $300B and growing.\n\n#IndiaRealEstate #PropertyIndia #IndiaByData"),
    (2,5): lambda: (s1_white("TOURISM REVENUE","$32B","International tourism revenue","green",[("18M","FOREIGN TOURISTS"),("#6","GLOBALLY BY RECEIPTS"),("Rs.2L Cr","DOMESTIC SPEND")],"Source: Ministry of Tourism"),"India earned $32B from tourism in 2024.\n\n#IndiaTourism #IncredibleIndia #IndiaByData"),
    (2,6): lambda: (s1_white("IT SECTOR","$245B","Annual IT & BPM exports","green",[("5.4M","IT PROFESSIONALS"),("20,000+","TECH COMPANIES"),("9.4%","OF GDP")],"Source: NASSCOM"),"India's IT sector — $245B in exports and 5.4 million jobs.\n\n#IndiaIT #TechIndia #NASSCOM #IndiaByData"),
    # Week 3
    (3,0): lambda: (s1_white("EV MARKET","$3.2B","Electric vehicle market size","green",[("1.2M","EVs SOLD IN 2024"),("3x","GROWTH IN 3 YEARS"),("Rs.18,000Cr","GOVT SUBSIDY")],"Source: SMEV, Vahan"),"India's EV revolution is accelerating — 1.2 million EVs sold in 2024.\n\n#IndiaEV #ElectricVehicles #IndiaByData"),
    (3,1): lambda: (s1_white("STARTUP FUNDING","$12B","Total startup funding 2024","amber",[("111","UNICORNS"),("1,12,718","DPIIT STARTUPS"),("#3","GLOBALLY")],"Source: DPIIT, Tracxn"),"India's startup ecosystem continues to grow despite global headwinds.\n\n#StartupIndia #IndiaStartups #IndiaByData"),
    (3,2): lambda: (s1_white("SPACE ECONOMY","$8B","India's space economy size","green",[("#5","GLOBALLY"),("100+","SATELLITES LAUNCHED"),("2%","GLOBAL MARKET SHARE")],"Source: IN-SPACe, ISRO"),"India's space economy targets $40B by 2040.\n\n#IndiaSpace #ISRO #SpaceIndia #IndiaByData"),
    (3,3): lambda: (s1_white("SEMICONDUCTOR","$10B","India semiconductor target","green",[("3","CHIP FABS PLANNED"),("Rs.76,000Cr","GOVT INCENTIVE"),("2026","FIRST CHIP TARGET")],"Source: MeitY"),"India is building its first semiconductor fab. A $10B bet on the future.\n\n#IndiaSemiconductor #MakeInIndia #IndiaByData"),
    (3,4): lambda: (s1_white("GREEN HYDROGEN","$100B","Green hydrogen potential","green",[("500GW","RENEWABLE TARGET"),("Rs.19,744Cr","GOVT MISSION"),("2030","TARGET YEAR")],"Source: Ministry of New Energy"),"India's green hydrogen mission — $100B opportunity by 2030.\n\n#GreenHydrogen #IndiaEnergy #IndiaByData"),
    (3,5): lambda: (s1_white("FISHERIES","$28B","Fish exports from India","green",[("#4","GLOBAL FISH EXPORTER"),("2.8Cr","FISHERMEN"),("Rs.2.48L Cr","SECTOR SIZE")],"Source: MPEDA"),"India is the world's 4th largest fish exporter.\n\n#IndiaFisheries #BlueEconomy #IndiaByData"),
    (3,6): lambda: (s1_white("TEXTILES","$40B","Textile & apparel exports","amber",[("4.5Cr","PEOPLE EMPLOYED"),("#2","GLOBAL EXPORTER"),("Rs.12L Cr","SECTOR SIZE")],"Source: Ministry of Textiles"),"India's textile sector employs 45 million people.\n\n#IndiaTextiles #MadeInIndia #IndiaByData"),
}

# ══════════════════════════════════════════════════════════
# SLOT 2 — AFTERNOON 1PM  (Demographics / Social)
# ══════════════════════════════════════════════════════════
AFTERNOON_TOPICS = {
    (0,0): lambda: (s2_bold("INDIA'S POPULATION",f"{round(wb('SP.POP.TOTL',1.44e9)/1e9,2)}","green","BILLION","People call India home.",[(f"{wb('SE.ADT.LITR.ZS',77.7)}%","Literacy"),(f"{wb('SP.DYN.LE00.IN',70.2)}yr","Life Exp."),(f"{wb('SP.URB.TOTL.IN.ZS',36.0)}%","Urban")],"Young. Vast. Unstoppable.","Source: World Bank"),"1.4 billion Indians. The world's most populous nation.\n\n#IndiaPopulation #Demographics #IndiaByData"),
    (0,1): lambda: (s7_chart("INDIA'S","EDUCATION STATS","77.7%","Adult literacy rate","amber",[("Primary Enrollment",92.8),("Secondary School",74.2),("Higher Education",27.1),("Female Literacy",70.3)],"12M engineers since 2000.",["Enrollment: 74.2% secondary","IITs in global top 200"],"Source: UNESCO, MoE"),"India's education revolution: 77.7% literacy, 12M engineers.\n\n#IndiaEducation #Literacy #IndiaByData"),
    (0,2): lambda: (s2_bold("INDIA'S YOUTH","65","green","%","of India is below 35 years.",[("28 yrs","Median Age"),("600M+","Working Age"),("12M","Join workforce/yr")],"The youngest large economy on Earth.","Source: Census, ILO"),"65% of India is below 35. The demographic dividend is just beginning.\n\n#IndiaYouth #DemographicDividend #IndiaByData"),
    (0,3): lambda: (s7_chart("HUMAN","DEVELOPMENT INDEX","0.644","Global Rank #132","amber",[("2011-12",27.1),("2015-16",14.2),("2022-23",5.3),("2025 est.",1.0)],"~270M lifted out of poverty.",["Health: Rs.73/person/year","Infant mortality: 26/1000"],"Source: UNDP, World Bank"),"From 27% poverty in 2011 to under 5% today.\n\n#IndiaHDI #PovertyReduction #IndiaByData"),
    (0,4): lambda: (s2_bold("INDIAN DIASPORA","32","green","MILLION","Indians live outside India.",[("$120B","Remittances"),("#1","Global Remit."),("110+","Countries")],"India receives most remittances globally.","Source: World Bank, MEA"),"32 million Indians abroad sending $120B home.\n\n#IndianDiaspora #NRI #IndiaByData"),
    (0,5): lambda: (s7_chart("INDIA'S","HEALTHCARE","70.2 yrs","Life expectancy at birth","green",[("Infant Mortality",26.0),("Maternal Mortality",9.7),("Malnutrition",15.3),("Stunting",35.5)],"India spends 3.8% of GDP on healthcare.",["Rs.73/person health spend","Down from 80 infant mortality in 1990"],"Source: WHO, World Bank"),"Life expectancy rose from 42 years in 1960 to 70.2 today.\n\n#IndiaHealth #Healthcare #IndiaByData"),
    (0,6): lambda: (s7_chart("WOMEN IN","INDIA — BY NUMBERS","48.4%","Share of female population","green",[("Workforce",23.0),("Literacy",70.3),("MPs",15.2),("STEM Grads",43.0)],"Women-led SHGs: 12 crore.",["STEM grads (women): 43% — world's highest","Maternal mortality fell 83% since 1990"],"Source: Census, ILO, WCD","#E8472A"),"India has 43% women in STEM — higher than US or UK.\n\n#WomenInIndia #GenderEquality #IndiaByData"),
    (1,0): lambda: (s2_bold("INDIA'S CITIES",str(round(wb('SP.URB.TOTL.IN.ZS',36.0))),"amber","%","of India lives in cities.",[("500+","Cities"),("8","Megacities"),("2050","Urban future")],"India urbanises 1 person every 2 seconds.","Source: Census, World Bank"),"India is urbanising faster than any nation in history.\n\n#IndiaUrban #SmartCities #IndiaByData"),
    (1,1): lambda: (s7_chart("INDIA'S","NUTRITION STATS","15.3%","Share of undernourished","red",[("Child Stunting",35.5),("Anaemia (Women)",57.0),("Wasting (Child)",19.3),("Obesity",3.9)],"Midday meals reach 12Cr children.",["POSHAN 2.0 budget: Rs.20,000Cr","India #107 in Global Hunger Index"],"Source: NFHS-5, FAO"),"India's nutrition challenge — and the progress being made.\n\n#IndiaNutrition #IndiaHealth #IndiaByData"),
    (1,2): lambda: (s2_bold("INDIA'S SENIORS","10.1","amber","%","of India is 60+ years old.",[("14Cr","Senior Citizens"),("2050","20% will be 60+"),("Rs.44K Cr","Pension budget")],"India's silver economy is rising.","Source: Census, HelpAge India"),"India's ageing population — a new challenge for the world's youngest nation.\n\n#SeniorIndia #AgingIndia #IndiaByData"),
    (1,3): lambda: (s7_chart("INDIA'S","MENTAL HEALTH","197M","People with mental disorders","red",[("Depression",45.7),("Anxiety",44.9),("Bipolar",1.2),("Schizophrenia",0.9)],"Only 0.07 psychiatrists per 1,00,000.",["Mental health budget: 0.05% of total health","National Mental Health Programme reaches 28 states"],"Source: Lancet, NIMHANS"),"India has 197 million people affected by mental health conditions.\n\n#MentalHealthIndia #IndiaByData"),
    (1,4): lambda: (s2_bold("CHILD LITERACY","92.8","green","%","Primary school enrollment.",[("26Cr","Children in school"),("12M","Out of school"),("Rs.1.1L Cr","Education budget")],"Free education for all under 14.","Source: ASER, Ministry of Education"),"92.8% primary school enrollment — India's education story.\n\n#IndiaEducation #RightToEducation #IndiaByData"),
    (1,5): lambda: (s7_chart("INDIA'S","SANITATION","99.9%","ODF coverage achieved (rural)","green",[("Pre-2014 ODF",38.0),("2019 ODF",98.0),("Tap Water Access",55.0),("Toilet Access",99.0)],"12Cr toilets built in 5 years.",["Jal Jeevan Mission: 14Cr tap connections","Swachh Bharat: Rs.1.4L Cr spent"],"Source: Ministry of Jal Shakti"),"From 38% to 99.9% open defecation free. India's sanitation miracle.\n\n#SwachhBharat #IndiaSanitation #IndiaByData"),
    (1,6): lambda: (s2_bold("INDIA'S MARRIAGE","21.2","amber","yrs","Average age of marriage (women).",[("18 yrs","Legal minimum"),("2.0","Fertility rate"),("56%","Married under 25")],"Median marriage age rising every decade.","Source: NFHS-5"),"India's changing social fabric — marriage age, fertility, and family.\n\n#IndiaDemographics #IndiaByData"),
    (2,0): lambda: (s2_bold("RURAL INDIA","65","amber","%","of India lives in villages.",[("8.68L","Villages"),("86Cr","Rural population"),("47%","Agriculture income")],"India is still a nation of villages.","Source: Census"),"65% of India lives in villages. The rural story.\n\n#RuralIndia #IndiaByData"),
    (2,1): lambda: (s7_chart("INDIA'S","LANGUAGE MAP","22","Scheduled languages","green",[("Hindi speakers",43.6),("Bengali speakers",8.0),("Telugu speakers",7.2),("Tamil speakers",5.9)],"India has 19,500 dialects.",["Hindi is spoken by 43% of Indians","English is official in 7 states"],"Source: Census 2011"),"India has 22 scheduled languages and 19,500 dialects.\n\n#IndiaLanguages #IndiaCulture #IndiaByData"),
    (2,2): lambda: (s2_bold("INDIA'S RELIGION","79.8","green","%","of India is Hindu.",[("14.2%","Muslim"),("2.3%","Christian"),("1.7%","Sikh")],"World's most diverse religious nation.","Source: Census 2011"),"India's religious diversity — the world's most diverse democracy.\n\n#IndiaDiversity #IncredibleIndia #IndiaByData"),
    (2,3): lambda: (s7_chart("INDIA'S","VOTER STATS","96.8Cr","Registered voters in 2024","green",[("2024 Turnout",66.0),("Women Voters",48.5),("First-time Voters",18.0),("Youth Voters",22.0)],"World's largest democratic exercise.",["Lok Sabha has 543 seats","2024 election cost Rs.1.35L Cr"],"Source: ECI"),"96.8 crore voters — the world's largest democratic exercise.\n\n#IndiaElection #LokSabha #IndiaByData"),
    (2,4): lambda: (s2_bold("INDIA'S TRIBES","8.6","amber","%","of India is Scheduled Tribe.",[("700+","Tribal groups"),("10.4Cr","Tribal population"),("705","Scheduled Tribes")],"India's tribal heritage is unparalleled.","Source: Census"),"India has 705 Scheduled Tribes and 700+ tribal communities.\n\n#TribalIndia #IndiaByData"),
    (2,5): lambda: (s7_chart("CRIME IN","INDIA — STATS","52L+","IPC crimes registered 2022","red",[("Cybercrime",25.0),("Women crimes",18.0),("Theft",20.0),("Road accidents",37.0)],"Road accidents kill 1.7L people/year.",["Cybercrime up 24% year on year","NCRB tracks all reported crimes"],"Source: NCRB 2022"),"India's crime statistics — what the data really says.\n\n#IndiaCrime #IndiaStats #IndiaByData"),
    (2,6): lambda: (s2_bold("INDIA'S DOCTORS","1:834","red","Ratio","Doctor to patient ratio.",[("13L","Registered Doctors"),("5.65L","Hospital Beds"),("0.9","Nurses per 1000")],"WHO recommends 1:1000 ratio.","Source: NMC, WHO"),"India faces a severe doctor shortage — 1 doctor per 834 people.\n\n#IndiaHealth #IndiaHospitals #IndiaByData"),
    (3,0): lambda: (s2_bold("INDIA'S FARMERS","58","amber","%","of Indians depend on farming.",[("14.6Cr","Farm households"),("Rs.10,218","Monthly income"),("86%","Small & marginal")],"Agriculture feeds 1.4 billion Indians.","Source: NSSO, Census"),"58% of India depends on farming. The numbers behind Indian agriculture.\n\n#IndiaFarmers #IndiaAgriculture #IndiaByData"),
    (3,1): lambda: (s7_chart("INDIA'S","PRISON STATS","5.7L","Prisoners in India","red",[("Undertrial",76.0),("Convicted",22.0),("Women",4.3),("Foreign",0.8)],"India's prisons are 118% overcapacity.",["76% are undertrials — not convicted","Tihar is Asia's largest prison complex"],"Source: NCRB Prison Statistics"),"76% of India's prisoners are yet to be convicted.\n\n#IndiaPrisons #IndiaJustice #IndiaByData"),
    (3,2): lambda: (s2_bold("INDIA'S MIGRANTS","45Cr","amber","People","migrate within India.",[("9Cr","Seasonal migrants"),("Rs.2L Cr","Remittances sent"),("UP & Bihar","Top sending states")],"India's internal migration is massive.","Source: Economic Survey"),"450 million Indians migrate internally for work and opportunity.\n\n#IndiaMigration #IndiaByData"),
    (3,3): lambda: (s7_chart("INDIA'S","DISABILITY STATS","2.68Cr","People with disabilities","amber",[("Locomotor",20.3),("Visual",18.8),("Hearing",18.9),("Mental",5.6)],"Only 36% of disabled are employed.",["Govt schemes reach 80L beneficiaries","RPwD Act 2016 covers 21 disabilities"],"Source: Census 2011, DEPwD"),"2.68 crore Indians with disabilities. Here's the full picture.\n\n#DisabilityIndia #InclusiveIndia #IndiaByData"),
    (3,4): lambda: (s2_bold("INDIA'S INTERNET","52.4","green","%","of India uses internet.",[("80Cr","Internet users"),("Rs.4/GB","Cheapest data globally"),("#2","GLOBALLY BY USERS")],"India added 30Cr users in 5 years.","Source: World Bank, TRAI"),"India has 800 million internet users — and the cheapest data globally.\n\n#DigitalIndia #InternetIndia #IndiaByData"),
    (3,5): lambda: (s7_chart("INDIA'S","HAPPINESS INDEX","126th","Global Happiness Rank","red",[("Work-life balance",42.0),("Financial security",38.0),("Health",55.0),("Social support",61.0)],"India ranks below global average.",["Nordic nations top the index every year","India scores 4.0 on 10-point happiness scale"],"Source: World Happiness Report 2024"),"India ranks 126th in the World Happiness Index. What's holding us back?\n\n#IndiaHappiness #IndiaByData"),
    (3,6): lambda: (s2_bold("INDIA'S ATHLETES","1.4Bn","green","People","One sporting nation.",[("28","Olympic medals ever"),("Rs.3,000Cr","Sports budget 2024"),("120Cr","Cricket fans")],"Sports is India's emerging superpower.","Source: SAI, IOA"),"India's sporting revolution — from 1 to 28 Olympic medals.\n\n#IndiaSports #IndiaOlympics #IndiaByData"),
}

# ══════════════════════════════════════════════════════════
# SLOT 3 — EVENING 6PM  (Tech / Infrastructure)
# ══════════════════════════════════════════════════════════
EVENING_TOPICS = {
    (0,0): lambda: (s3_vibrant("DIGITAL","INDIA","111 Unicorns","green",[("18.4B/mo","UPI TRANSACTIONS"),("$245B","ANNUAL IT EXPORTS"),(f"{wb('IT.NET.USER.ZS',52.4)}%","INTERNET USERS")],"Source: DPIIT, NPCI, NASSCOM"),"India's digital revolution — 111 unicorns, 18.4B UPI transactions/month.\n\n#DigitalIndia #UPI #TechIndia #IndiaByData"),
    (0,1): lambda: (s6_numbers("ROAD &","HIGHWAY NETWORK","2025","63.7L","km","Total road network","green",[("1.46L","km","National highways"),("3,052","km","Expressways"),("43%","","Paved coverage")],"Source: MoRTH"),"India has the 2nd largest road network — 63.7 lakh km.\n\n#IndiaRoads #IndiaHighways #IndiaInfra #IndiaByData"),
    (0,2): lambda: (s3_vibrant("UPI","REVOLUTION","18.4B / month","green",[("Rs.20L Cr","MONTHLY VALUE"),("350M+","ACTIVE USERS"),("#1","GLOBALLY RT PAYMENTS")],"Source: NPCI, RBI"),"India's UPI processes more payments than the rest of the world combined.\n\n#UPI #FinTech #IndiaByData"),
    (0,3): lambda: (s6_numbers("POWER &","ENERGY SECTOR","2025","942","GW","Total installed power capacity","green",[("43%","","Renewable energy share"),("200","GW","Solar capacity"),("47","GW","Wind capacity")],"Source: Ministry of Power, MNRE"),"India's power sector: 942 GW installed, 43% renewable.\n\n#IndiaEnergy #SolarIndia #IndiaByData"),
    (0,4): lambda: (s3_vibrant("STARTUP","INDIA","1,12,718 Startups","green",[("111","UNICORNS"),("$140B","TOTAL FUNDING"),("#3","GLOBALLY UNICORNS")],"Source: DPIIT, Invest India"),"India: 3rd largest startup ecosystem in the world.\n\n#StartupIndia #Unicorns #IndiaByData"),
    (0,5): lambda: (s6_numbers("INDIAN","RAILWAYS","2025","23M","passengers","Carried every single day","green",[("68,000","km","Total route length"),("13,000+","trains","Operated daily"),("1,473","km","Longest line")],"Source: Indian Railways","#E8472A"),"Indian Railways — 23 million passengers daily.\n\n#IndianRailways #IndiaInfra #IndiaByData"),
    (0,6): lambda: (s3_vibrant("SPACE &","DEFENCE","Chandrayaan-3","green",[("100+","ISRO SATELLITES"),("$2.5B","DEFENCE EXPORTS"),("#5","GLOBAL SPACE ECONOMY")],"Source: ISRO, Ministry of Defence"),"India: first to land on Moon's south pole.\n\n#ISRO #IndiaSpace #Chandrayaan #IndiaByData"),
    (1,0): lambda: (s6_numbers("AVIATION &","PORTS","2025","200M","passengers","Annual air traffic","green",[("148","airports","Operational"),("3rd","","Largest aviation market"),("13","major","Ports + 200 minor")],"Source: AAI, Ministry of Ports","#E8472A"),"India: 3rd largest aviation market, 148 airports.\n\n#IndiaAviation #IndiaByData"),
    (1,1): lambda: (s3_vibrant("5G IN","INDIA","6L+ 5G towers","green",[("13Cr","5G SUBSCRIBERS"),("50+","CITIES COVERED"),("Rs.26,316Cr","SPECTRUM COST")],"Source: TRAI, DoT"),"India's 5G rollout — fastest in the world for 5G adoption.\n\n#India5G #DigitalIndia #IndiaByData"),
    (1,2): lambda: (s6_numbers("WATER &","SANITATION","2025","14Cr","tap connections","Jal Jeevan Mission","green",[("55%","","Rural tap coverage"),("99%","","ODF achieved"),("Rs.3.6L Cr","","Mission budget")],"Source: Ministry of Jal Shakti"),"Jal Jeevan Mission connected 14 crore homes to tap water.\n\n#JalJeevanMission #IndiaWater #IndiaByData"),
    (1,3): lambda: (s3_vibrant("AI IN","INDIA","$6B market","green",[("420+","AI STARTUPS"),("Rs.10,372Cr","GOVT INVESTMENT"),("#3","AI TALENT GLOBALLY")],"Source: NASSCOM, MeitY"),"India is emerging as a global AI powerhouse.\n\n#IndiaAI #TechIndia #IndiaByData"),
    (1,4): lambda: (s6_numbers("METRO","RAIL NETWORK","2025","945","km","Operational metro network","green",[("20","cities","Metro cities"),("42Cr","passengers","Annual ridership"),("1,000","km","Under construction")],"Source: Ministry of Housing, UMTA"),"India has 945 km of metro rail operational across 20 cities.\n\n#IndiaMetro #UrbanMobility #IndiaByData"),
    (1,5): lambda: (s3_vibrant("SOLAR","POWER","200 GW installed","green",[("2030 TARGET","500 GW"),("Rs.2.5","COST PER UNIT"),("#3","GLOBALLY SOLAR")],"Source: MNRE, IEA"),"India is the world's 3rd largest solar power producer.\n\n#IndiaSolar #RenewableIndia #IndiaByData"),
    (1,6): lambda: (s6_numbers("BROADBAND &","INTERNET","2025","80Cr","users","Total internet users","green",[("36.5Cr","subscribers","Broadband subs"),("Rs.4/GB","","Cheapest globally"),("1.2Bn","SIMs","Mobile connections")],"Source: TRAI, World Bank"),"India has 800 million internet users and the world's cheapest data.\n\n#DigitalIndia #InternetIndia #IndiaByData"),
    (2,0): lambda: (s3_vibrant("ELECTRIC","VEHICLES","12L EVs sold 2024","green",[("3x","GROWTH IN 3 YEARS"),("90%","2-WHEELER SHARE"),("Rs.18,000Cr","FAME SUBSIDY")],"Source: SMEV, Vahan, MHI"),"India sold 1.2 million EVs in 2024 — 3x growth in 3 years.\n\n#IndiaEV #ElectricVehicles #IndiaByData"),
    (2,1): lambda: (s6_numbers("NATIONAL","HIGHWAY NETWORK","2025","1.46L","km","National highways in India","green",[("27","km/day","Built in 2024"),("Rs.10L Cr","budget","5-year NHDP"),("45","expressways","Under construction")],"Source: NHAI, MoRTH"),"India is building 27 km of national highway every day.\n\n#NationalHighways #NHAI #IndiaByData"),
    (2,2): lambda: (s3_vibrant("SEMICONDUCTOR","MISSION","3 Fabs planned","green",[("Rs.76,000Cr","GOVT INCENTIVE"),("2026","FIRST CHIP TARGET"),("Rs.1.5L Cr","TOTAL INVESTMENT")],"Source: MeitY, India Semiconductor Mission"),"India's semiconductor mission — building the chips of tomorrow.\n\n#IndiaSemiconductor #IndiaByData"),
    (2,3): lambda: (s6_numbers("SMART","CITIES MISSION","2025","100","cities","Smart city projects","green",[("Rs.2.05L Cr","invested","Total investment"),("7,900+","projects","Completed"),("Rs.1.64L Cr","allocated","Central funds")],"Source: Ministry of Housing"),"100 Smart Cities — India's urban transformation story.\n\n#SmartCities #IndiaUrban #IndiaByData"),
    (2,4): lambda: (s3_vibrant("FINTECH","INDIA","$31B market","green",[("87%","FINTECH ADOPTION"),("2,100+","FINTECH STARTUPS"),("#3","GLOBALLY")],"Source: EY, NASSCOM"),"India has 87% fintech adoption — 3rd largest fintech hub globally.\n\n#IndiaFintech #DigitalPayments #IndiaByData"),
    (2,5): lambda: (s6_numbers("WATERWAYS &","SHIPPING","2025","20,000","km","Navigable waterways","green",[("111","NW","National waterways"),("Rs.25,000Cr","invested","Sagarmala program"),("13","major","Major seaports")],"Source: Ministry of Ports, IWAI"),"India has 20,000 km of navigable waterways — largely untapped.\n\n#IndiaPorts #Waterways #IndiaByData"),
    (2,6): lambda: (s3_vibrant("DRONE","INDIA","Rs.12,000Cr market","green",[("2030 TARGET","Rs.1.5L Cr"),("20,000+","JOBS CREATED"),("#1","DRONE POLICY RANK")],"Source: DGCA, FICCI"),"India aims to be the world's drone hub by 2030.\n\n#IndiaDrones #MakeInIndia #IndiaByData"),
    (3,0): lambda: (s6_numbers("RURAL","ELECTRIFICATION","2025","100%","villages","Electrified under Saubhagya","green",[("2.86Cr","homes","Connected post-2017"),("Rs.16,320Cr","spent","Saubhagya scheme"),("24x7","hours","Power goal")],"Source: Ministry of Power"),"India achieved 100% village electrification under the Saubhagya scheme.\n\n#IndiaElectrification #PowerForAll #IndiaByData"),
    (3,1): lambda: (s3_vibrant("CLOUD","COMPUTING","$6.2B market","green",[("35%","ANNUAL GROWTH"),("3","HYPERSCALER REGIONS"),("Rs.1.2L Cr","GOVT CLOUD PLAN")],"Source: Nasscom, IDC"),"India's cloud computing market is one of the world's fastest growing.\n\n#IndiaCloud #TechIndia #IndiaByData"),
    (3,2): lambda: (s6_numbers("DEFENCE","MANUFACTURING","2025","Rs.1.09L Cr","value","Defence production in India","green",[("Rs.21,083Cr","exports","Defence exports 2024"),("16,000+","companies","Defence industrial base"),("2028","target","Rs.3L Cr production")],"Source: Ministry of Defence, SIPRI"),"India's defence manufacturing crossed Rs.1 lakh crore.\n\n#IndiaDefence #MakeInIndia #IndiaByData"),
    (3,3): lambda: (s3_vibrant("CYBERSECURITY","INDIA","$2.5B market","amber",[("4,44,553","CYBER CRIMES 2023"),("Rs.10,000Cr","CERT-IN BUDGET"),("#10","GLOBALLY CYBER POWER")],"Source: CERT-In, NCRB"),"India's cybersecurity market is growing as threats rise.\n\n#IndiaCyber #CyberSecurity #IndiaByData"),
    (3,4): lambda: (s6_numbers("WASTE","MANAGEMENT","2025","62M","tonnes","Solid waste generated yearly","red",[("30%","processed","Waste processed"),("4,000+","ULBs","Urban local bodies"),("Rs.1.4L Cr","gap","Investment needed")],"Source: CPCB, MoHUA"),"India generates 62 million tonnes of solid waste annually.\n\n#IndiaWaste #CleanIndia #IndiaByData"),
    (3,5): lambda: (s3_vibrant("COLD CHAIN","LOGISTICS","$23B market","green",[("8,000+","COLD STORAGE UNITS"),("35Cr MT","CAPACITY"),("Rs.10,000Cr","GOVT INVESTMENT")],"Source: NHB, NCI"),"India's cold chain revolution — cutting food waste, feeding more.\n\n#IndiaColdChain #FoodIndia #IndiaByData"),
    (3,6): lambda: (s6_numbers("HEALTH","INFRASTRUCTURE","2025","1.6L","hospitals","Total hospitals in India","amber",[("18.9L","beds","Hospital beds"),("5.65L","MBBS","Registered doctors"),("Rs.3,200Cr","PMJAY","Ayushman Bharat budget")],"Source: NHA, NMC"),"India has 1.6 lakh hospitals — but needs 3x more by 2030.\n\n#IndiaHealth #Hospitals #IndiaByData"),
}

# ══════════════════════════════════════════════════════════
# SLOT 4 — NIGHT 9PM  (State Spotlight / Forbes Charts)
# ══════════════════════════════════════════════════════════
NIGHT_TOPICS = {
    # State spotlights — rotate through all states
    (0,0): lambda: (s4_table(*get_state(0)), f"State Spotlight: {get_state(0)[0]}\n\n#{get_state(0)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (0,1): lambda: (s4_table(*get_state(1)), f"State Spotlight: {get_state(1)[0]}\n\n#{get_state(1)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (0,2): lambda: (s4_table(*get_state(2)), f"State Spotlight: {get_state(2)[0]}\n\n#{get_state(2)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (0,3): lambda: (s4_table(*get_state(3)), f"State Spotlight: {get_state(3)[0]}\n\n#{get_state(3)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (0,4): lambda: (s4_table(*get_state(4)), f"State Spotlight: {get_state(4)[0]}\n\n#{get_state(4)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (0,5): lambda: (s4_table(*get_state(5)), f"State Spotlight: {get_state(5)[0]}\n\n#{get_state(5)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (0,6): lambda: (s4_table(*get_state(6)), f"State Spotlight: {get_state(6)[0]}\n\n#{get_state(6)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    # Forbes charts — comparative data
    (1,0): lambda: (s8_forbes("India's Richest States","Maharashtra leads with Rs.36T. Top 5 states contribute over 45% of India's GDP.",[("MH",36.3),("TN",24.9),("KA",23.0),("UP",22.0),("GJ",21.0),("WB",15.6),("RJ",13.5),("TG",13.0)],"State GDP (Rs. Trillion)","Source: State Economic Reports, RBI"),"India's richest states by GDP — the data behind the rankings.\n\n#IndiaGDP #IndiaStates #IndiaByData"),
    (1,1): lambda: (s8_forbes("India's Most Literate States","Kerala tops India's literacy chart at 96.2%. The gap between states tells a story.",[("KL",96.2),("MZ",91.3),("GOA",88.7),("HP",82.8),("TN",82.3),("MH",82.3),("WB",76.3),("PB",75.8)],"Literacy Rate (%)","Source: Census 2011"),"India's literacy map — which state leads and which lags?\n\n#IndiaLiteracy #IndiaEducation #IndiaByData"),
    (1,2): lambda: (s8_forbes("Fastest Growing States","Telangana and Gujarat lead India's economic growth race.",[("TS",18.0),("GJ",15.2),("KA",14.8),("MH",13.1),("UP",12.4),("RJ",11.8),("HR",11.2),("TN",10.9)],"State GDP Growth Rate (%)","Source: MOSPI, State Reports"),"Which Indian state grew the fastest? The numbers reveal all.\n\n#IndiaGrowth #IndiaStates #IndiaByData"),
    (1,3): lambda: (s8_forbes("India's Most Populated States","Uttar Pradesh alone has more people than Brazil.",[("UP",235.0),("MH",126.4),("BR",128.5),("WB",99.6),("MP",85.0),("RJ",81.0),("TN",77.8),("KA",67.6)],"Population (Millions)","Source: Census 2011 + Projections"),"India's most populated states — a story of scale.\n\n#IndiaPopulation #IndiaStates #IndiaByData"),
    (1,4): lambda: (s8_forbes("India's Urbanisation by State","Goa is India's most urban state. Bihar is least urbanised.",[("GOA",62.2),("MH",45.2),("TN",48.4),("GJ",42.6),("KA",38.6),("PB",37.5),("HR",34.8),("UP",22.3)],"Urban Population (%)","Source: Census 2011"),"India's urbanisation story — state by state.\n\n#IndiaUrban #IndiaStates #IndiaByData"),
    (1,5): lambda: (s8_forbes("India's Richest & Poorest","Per capita income tells the real story of inequality.",[("GOA",540),("SIK",361),("KA",298),("MH",272),("TS",267),("BR",42),("JH",65),("UP",72)],"Per Capita Income (Rs. Thousand)","Source: MOSPI, State Reports"),"The gap between India's richest and poorest states.\n\n#IndiaInequality #IndiaStates #IndiaByData"),
    (1,6): lambda: (s8_forbes("Crime Rate by State","Which states are safest? The NCRB data decoded.",[("KL",1200),("DL",1150),("CG",480),("MH",430),("MP",390),("TN",320),("GJ",210),("WB",180)],"IPC Crimes per Lakh Population","Source: NCRB 2022"),"India's safest and most dangerous states by crime rate.\n\n#IndiaCrime #IndiaStates #IndiaByData"),
    (2,0): lambda: (s4_table(*get_state(7)), f"State Spotlight: {get_state(7)[0]}\n\n#{get_state(7)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (2,1): lambda: (s4_table(*get_state(8)), f"State Spotlight: {get_state(8)[0]}\n\n#{get_state(8)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (2,2): lambda: (s4_table(*get_state(9)), f"State Spotlight: {get_state(9)[0]}\n\n#{get_state(9)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (2,3): lambda: (s4_table(*get_state(10)), f"State Spotlight: {get_state(10)[0]}\n\n#{get_state(10)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (2,4): lambda: (s8_forbes("India vs World GDP","How India compares to the world's top economies.",[("USA",27.7),("CHN",17.7),("GER",4.4),("JPN",4.2),("IND",3.7),("UK",3.1),("FRA",2.8),("BRZ",2.2)],"GDP (USD Trillion)","Source: IMF World Economic Outlook 2024"),"India vs the world — GDP comparison.\n\n#IndiaGDP #IndiaVsWorld #IndiaByData"),
    (2,5): lambda: (s8_forbes("India's Defence vs Neighbours","India's defence spending in regional context.",[("IND",83),("CHN",225),("PAK",10),("BGD",4),("SRL",1),("NPL",0.6),("MLD",0.3),("BUT",0.1)],"Defence Budget (Billion USD)","Source: SIPRI 2024"),"India's defence spending compared to its neighbours.\n\n#IndiaDefence #SouthAsia #IndiaByData"),
    (2,6): lambda: (s8_forbes("India's IT Exports vs World","India's tech dominance in global IT exports.",[("IND",245),("USA",400),("IRE",130),("UK",120),("CHN",100),("GER",80),("FRA",60),("SNG",55)],"IT Exports (Billion USD)","Source: NASSCOM, WTO 2024"),"India supplies 15% of the world's IT services.\n\n#IndiaIT #TechIndia #IndiaByData"),
    (3,0): lambda: (s4_table(*get_state(11)), f"State Spotlight: {get_state(11)[0]}\n\n#{get_state(11)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (3,1): lambda: (s4_table(*get_state(12)), f"State Spotlight: {get_state(12)[0]}\n\n#{get_state(12)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (3,2): lambda: (s4_table(*get_state(13)), f"State Spotlight: {get_state(13)[0]}\n\n#{get_state(13)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (3,3): lambda: (s4_table(*get_state(14)), f"State Spotlight: {get_state(14)[0]}\n\n#{get_state(14)[0].replace(' ','')} #IndiaStates #StateSpotlight #IndiaByData"),
    (3,4): lambda: (s8_forbes("India's Renewable Energy","State-wise solar & wind capacity.",[("RJ",29.9),("GJ",17.0),("KA",15.0),("TN",14.8),("MH",10.6),("MP",8.0),("AP",7.2),("TG",5.8)],"Installed Renewable Capacity (GW)","Source: MNRE 2024"),"India's green energy leaders — state by state.\n\n#IndiaRenewable #SolarIndia #IndiaByData"),
    (3,5): lambda: (s8_forbes("India's Top Cities by GDP","Mumbai leads India's urban economy.",[("MUM",310),("DEL",293),("BLR",110),("CHN",78),("KOL",75),("HYD",74),("PUN",69),("AHM",68)],"City GDP (Billion USD)","Source: Oxford Economics, 2024"),"India's richest cities by GDP — where the money is made.\n\n#IndiaCities #IndiaGDP #IndiaByData"),
    (3,6): lambda: (s8_forbes("India's Air Quality","Cities with worst & best AQI.",[("DEL",220),("PAT",180),("LKW",165),("AHM",145),("KOL",130),("MUM",110),("BLR",65),("CHN",55)],"Average AQI 2024 (Higher = Worse)","Source: CPCB, IQAir 2024"),"India's air quality crisis — and which cities breathe clean.\n\n#IndiaAQI #AirQuality #IndiaByData"),
}

# ─── POST DISPATCHER ──────────────────────────────────────
def get_post(slot_dict, label):
    wk  = now_ist().isocalendar()[1] % 4
    day = now_ist().weekday()
    key = (wk, day)
    if key not in slot_dict:
        key = (0, day % 7)
    global CURRENT_SLOT
    CURRENT_SLOT = _SLOT_IDX.get(label[:3], 0)
    print(f"  {label} | Week {wk} | Day {day} | layout: {'Swiss' if use_swiss() else 'classic'} | colour: {apply_theme()}")
    return slot_dict[key]()

# ─── INSTAGRAM ────────────────────────────────────────────
def get_user_id():
    d=requests.get(f"https://graph.instagram.com/v21.0/me?fields=id,username&access_token={ACCESS_TOKEN}").json()
    if "error" in d: print("  Error:",d["error"]["message"]); return None
    print(f"  Connected: @{d.get('username')}"); return d.get("id")

def upload_image(buf, tries=3):
    raw = buf.read()
    b64 = base64.b64encode(raw).decode("utf-8")
    for attempt in range(1, tries + 1):
        try:
            res = requests.post("https://api.imgbb.com/1/upload", data={"key": IMGBB_API_KEY, "image": b64}, timeout=45).json()
            if res.get("success"):
                url = res["data"].get("image", {}).get("url") or res["data"].get("display_url") or res["data"].get("url")
                print("  Uploaded:", url); return url
            print(f"  imgbb failed (attempt {attempt}/{tries}):", res.get("error", res))
            if res.get("status_code") in (400, 403) and "key" in str(res).lower():
                print("  -> The IMGBB_KEY secret looks invalid. Check it at api.imgbb.com."); return None
        except Exception as e:
            print(f"  imgbb error (attempt {attempt}/{tries}):", e)
        if attempt < tries: time.sleep(5 * attempt)
    return None

def _api_error(d):
    e = d.get("error", {}); msg = e.get("message", d)
    print("  Error:", msg)
    if e.get("code") == 190 or "access token" in str(msg).lower():
        print("  -> The Instagram token is invalid or expired. Generate a new one and update the IG_TOKEN secret.")

BASE = "https://graph.instagram.com/v21.0"

def _create_container(uid, data):
    """Create a media container (image, carousel item, carousel or story). Safe to retry: nothing is public yet."""
    for attempt in range(1, 4):
        try:
            c = requests.post(f"{BASE}/{uid}/media", data={**data, "access_token": ACCESS_TOKEN}, timeout=45).json()
            if "error" in c:
                _api_error(c)
                if c["error"].get("code") == 190: return None
            else:
                return c.get("id")
        except Exception as e:
            print(f"  container error (attempt {attempt}/3):", e)
        time.sleep(5 * attempt)
    return None

def _wait_ready(cid, tries=12):
    for _ in range(tries):
        try:
            st = requests.get(f"{BASE}/{cid}", params={"fields": "status_code", "access_token": ACCESS_TOKEN}, timeout=20).json().get("status_code")
        except Exception:
            st = None
        if st == "FINISHED": return True
        if st in ("ERROR", "EXPIRED"):
            print("  Instagram could not process the media:", st); return False
        time.sleep(5)
    return True   # not confirmed - try anyway

def _publish(uid, cid, body=None):
    """Publish a container. If the reply is lost, check the feed before retrying so we never double-post."""
    for attempt in range(1, 3):
        try:
            res = requests.post(f"{BASE}/{uid}/media_publish", data={"creation_id": cid, "access_token": ACCESS_TOKEN}, timeout=60).json()
            if "error" in res:
                _api_error(res)
                if res["error"].get("code") == 190: return None
            else:
                print("  Posted! ID:", res.get("id")); return res.get("id")
        except Exception as e:
            print(f"  publish error (attempt {attempt}/2):", e)
        time.sleep(10)
        if body and already_posted(uid, body):
            print("  The post is live (confirmed in feed)."); return "confirmed"
    return None

def post_to_instagram(uid, url, caption, body=None):
    cid = _create_container(uid, {"image_url": url, "caption": caption, "media_type": "IMAGE"})
    if not cid or not _wait_ready(cid): return False
    return bool(_publish(uid, cid, body))

def post_carousel(uid, urls, caption, body=None):
    kids = []
    for u in urls:
        k = _create_container(uid, {"image_url": u, "is_carousel_item": "true"})
        if not k: return False
        kids.append(k)
    if not all(_wait_ready(k) for k in kids): return False
    cid = _create_container(uid, {"media_type": "CAROUSEL", "children": ",".join(kids), "caption": caption})
    if not cid or not _wait_ready(cid): return False
    return bool(_publish(uid, cid, body))

def post_story(uid, url):
    cid = _create_container(uid, {"image_url": url, "media_type": "STORIES"})
    if not cid or not _wait_ready(cid): return False
    return bool(_publish(uid, cid))

def jpeg(buf, q=92):
    """Carousel items and stories are sent as JPEG (the format the API officially accepts)."""
    from PIL import Image
    buf.seek(0); out = io.BytesIO()
    Image.open(buf).convert("RGB").save(out, format="JPEG", quality=q); out.seek(0); return out

# Looks cycled across the slides of one carousel so no two neighbours match (style AND colour).
# (colours come from design_library.PALETTES via apply_theme)

def varied_slide(kw, i):
    """One indicator slide from trends.india_args kwargs. Look number i rotates layout AND colour theme."""
    (then_v, then_l), (now_v, now_l), (chg_v, _c) = kw["stats"]
    sector = kw["hero_sub"].split(",")[0].upper()
    src = kw["source"]; label = kw["title"]
    apply_theme(offset=i * 7) if os.environ.get("THEME", "auto") != "off" else _dl.set_theme(None)
    k = (i + now_ist().toordinal()) % 4          # starting layout also shifts each day
    if k == 0:
        return _dl.s9_geometric(f"{kw['kicker']}: {label}".upper(), kw["hero"], kw["hero_sub"], hc(kw["hero_sent"]), kw["stats"], src)
    if k == 1:
        return _dl.s11_colorblock(_dl._th("bold", BRAND), sector, now_v,
                                  f"{label}. {then_l.title()}: {then_v}.", f"{now_l.title()}: {now_v}. Change: {chg_v}.",
                                  [(then_v, then_l), (now_v, now_l), (chg_v, "CHANGE")], src)
    if k == 2:
        return _dl.s13_bignum(_dl._th("mid", "#FFC107"), hc(kw["hero_sent"]), now_v, sector, label,
                              [(then_l, then_v), ("CHANGE", chg_v)], [(now_l, now_v)], src)
    return _dl.s1_white(kw["title"], kw["hero"], kw["hero_sub"], kw["hero_sent"], kw["stats"], src, kicker=kw["kicker"])

def story_image(buf):
    """9:16 story: the poster centred on a canvas in the poster's own background colour (inside Instagram's safe zones)."""
    from PIL import Image, ImageDraw
    buf.seek(0); poster = Image.open(buf).convert("RGB")
    W, H = poster.size
    bg = poster.getpixel((W - 8, H // 2))
    canvas = Image.new("RGB", (1080, 1920), bg)
    canvas.paste(poster, ((1080 - W) // 2, (1920 - H) // 2))
    lum = 0.299 * bg[0] + 0.587 * bg[1] + 0.114 * bg[2]
    d = ImageDraw.Draw(canvas)
    d.text((90, 1730), "NEW POST ON THE FEED", font=_dl.get_font(30), fill=(20, 20, 20) if lum > 140 else (235, 235, 235))
    d.text((90, 1775), "@indiabydata", font=_dl.get_font(26, bold=False), fill=(90, 90, 90) if lum > 140 else (170, 170, 170))
    out = io.BytesIO(); canvas.save(out, format="JPEG", quality=92); out.seek(0); return out

def already_posted(uid, body):
    """True if an identical post (same caption) went out in the last 20 hours."""
    try:
        r = requests.get(f"https://graph.instagram.com/v21.0/{uid}/media",
                         params={"fields": "caption,timestamp", "limit": 25, "access_token": ACCESS_TOKEN},
                         timeout=15).json()
        norm = lambda c: (c or "").split(" — ", 1)[-1].strip()
        from datetime import timezone, timedelta
        cutoff = datetime.now(timezone.utc) - timedelta(hours=20)
        for m in r.get("data", []):
            ts = datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
            if ts >= cutoff and norm(m.get("caption")) == body.strip():
                return True
    except Exception as e:
        print("  (duplicate check skipped:", e, ")")
    return False

def recent_captions(uid, n=25):
    try:
        r = requests.get(f"https://graph.instagram.com/v21.0/{uid}/media",
                         params={"fields": "caption", "limit": n, "access_token": ACCESS_TOKEN}, timeout=15).json()
        return [m.get("caption") or "" for m in r.get("data", [])]
    except Exception:
        return []

def trend_post(uid):
    """Trend-radar post for the 6 PM slot. Returns ([poster buffers], caption) or None.
    One poster, or a 3-slide carousel when there is an India then-vs-now story to tell.
    TREND_MODE: auto (default) = post it | draft = render a preview only | off = disabled."""
    global CURRENT_SLOT
    mode = os.environ.get("TREND_MODE", "auto")
    if mode == "off": return None
    try:
        t = trends.find_trend(recent_captions(uid) if uid else [])
        if not t: return None
        title, hero, hero_sub, stats, source, caption = trends.poster_args(t)
        CURRENT_SLOT = 2
        apply_theme()
        bufs = [s1_white(title, hero, hero_sub, "green", stats, source, kicker="TRENDING IN INDIA")]
        extra = trends.india_args(t)
        if extra:
            slides, table, text = extra
            for n, kw in enumerate(slides, 1):
                bufs.append(varied_slide(kw, n))
            if table:
                bufs.append(_dl.s12_grid(table["words"], table["tag"], table["items"], table["source"]))
            body, tags = caption.rsplit("\n\n", 1)
            caption = body + "\n\n" + text + "\n\n" + tags
        os.makedirs("previews", exist_ok=True)
        for n, b in enumerate(bufs, 1):
            b.seek(0); open(f"previews/trend_slide{n}.png", "wb").write(b.read()); b.seek(0)
        open("previews/trend_caption.txt", "w").write(caption)
        if mode == "draft":
            print("  TREND_MODE=draft: trend post saved to previews/, not posted. Caption:\n" + caption)
            return None
        return bufs, caption
    except Exception as e:
        print("  Trend radar error (falling back to the normal post):", e)
        return None

def run_post(slot_dict, label):
    print(f"\n{'='*55}\n  IndiaByData — {label}\n  {now_ist().strftime('%A, %d %b %Y %H:%M IST')}\n{'='*55}")
    dry = os.environ.get("DRY_RUN") == "1"
    uid = None if dry else get_user_id()
    if not dry and not uid: return False
    tp = trend_post(uid) if label.startswith("6PM") else None
    if tp:
        bufs, caption = tp
    else:
        b, caption = get_post(slot_dict, label); bufs = [b]
    os.makedirs("previews", exist_ok=True)
    stories_on = os.environ.get("STORIES", "on" if trends.CFG["stories"].get("enabled", True) else "off") != "off"
    for n, b in enumerate(bufs, 1):
        b.seek(0); open(f"previews/preview_{label.replace(' ','_')}_{n}.png", "wb").write(b.read()); b.seek(0)
    if dry:
        if stories_on: open("previews/story_preview.jpg", "wb").write(story_image(bufs[0]).read())
        kind = f"carousel of {len(bufs)}" if len(bufs) > 1 else "single image"
        print(f"  DRY RUN - nothing posted ({kind}). Previews saved in previews/\n  Caption:\n{caption}"); return True
    if os.environ.get("FORCE") != "1" and already_posted(uid, caption):
        print("  Already posted in the last 20 hours - skipping to avoid a duplicate."); return True
    full_caption = f"{now_ist().strftime('%d %b %Y')} — {caption}"
    ok = False
    if len(bufs) > 1:
        urls = [upload_image(jpeg(b)) for b in bufs]
        if all(urls):
            ok = post_carousel(uid, urls, full_caption, body=caption)
        else:
            print("  Carousel upload failed - posting the cover image alone.")
            u = upload_image(bufs[0]); ok = bool(u) and post_to_instagram(uid, u, full_caption, body=caption)
    else:
        u = upload_image(bufs[0]); ok = bool(u) and post_to_instagram(uid, u, full_caption, body=caption)
    if ok and stories_on:
        try:
            time.sleep(5)
            su = upload_image(story_image(bufs[0]))
            print("  Story posted." if su and post_story(uid, su) else "  (Story could not be posted - the feed post is live.)")
        except Exception as e:
            print("  (Story skipped:", e, ")")
    return ok

# ─── ENTRY POINT (GitHub Actions calls this) ──────────────
SLOTS = {
    "morning":   (MORNING_TOPICS,   "8AM Economy"),
    "afternoon": (AFTERNOON_TOPICS, "1PM Demographics"),
    "evening":   (EVENING_TOPICS,   "6PM Tech & Infra"),
    "night":     (NIGHT_TOPICS,     "9PM State Spotlight"),
}

def pick_slot():
    h = now_ist().hour + now_ist().minute / 60
    if h < 11:   return "morning"
    if h < 16:   return "afternoon"
    if h < 19.5: return "evening"
    return "night"

if __name__ == "__main__":
    arg = sys.argv[1] if len(sys.argv) > 1 else "auto"
    slot = pick_slot() if arg == "auto" else arg
    if slot not in SLOTS: sys.exit(f"Unknown slot '{arg}'. Use morning|afternoon|evening|night|auto")
    ok = run_post(*SLOTS[slot])
    sys.exit(0 if ok else 1)
