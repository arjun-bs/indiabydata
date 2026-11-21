"""
Trend radar for @indiabydata.

Finds what India is searching for today (Google Trends "Trending now", India), checks it against
real Wikipedia page-view data, compares it with its predecessor when there is one
(GTA VI vs GTA V, iPhone 17 vs iPhone 16 ...) and returns the numbers for a poster.

Everything shown on a poster is a measured number with a named source. If nothing qualifies,
find_trend() returns None and the normal scheduled post goes out instead.
"""
import re, math
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from urllib.parse import quote
import requests

UA = {"User-Agent": "IndiaByDataBot/1.0 (https://www.instagram.com/indiabydata/; github actions) python-requests"}
WIKI_VIEWS = "https://wikimedia.org/api/rest_v1/metrics/pageviews"
GTRENDS_RSS = "https://trends.google.com/trending/rss?geo=IN"

# ---- safety: keep the account neutral, positive and factual -------------------------------
BLOCK = re.compile(
    r"\b(dies|died|death|dead|killed|kill|murder\w*|rape\w*|suicide|arrest\w*|accident|crash\w*|blast|bomb\w*|"
    r"attack\w*|terror\w*|shot|shooting|violence|riot\w*|protest\w*|porn\w*|sex\w*|nude|leak\w*|scandal|assault\w*|"
    r"abuse\w*|fraud|scam|cancer|funeral|tragedy|stampede|flood\w*|earthquake|war|warfare|army|military|"
    r"election\w*|vote|voting|bjp|congress|aap|minister|modi|rahul|gandhi|party|poll|polls|verdict|court|"
    r"supreme|police|jail|bail|hospital|covid|virus|outbreak|religio\w*|temple|mosque|church|caste)\b", re.I)
PERSON = re.compile(
    r"\b(actor|actress|singer|politician|footballer|cricketer|player|born|businessman|businesswoman|rapper|"
    r"director|presenter|journalist|comedian|youtuber|influencer|model|athlete|boxer|wrestler|chess|"
    r"musician|composer|writer|author|poet|king|queen|prince|princess|saint|guru)\b", re.I)
ALLOW = re.compile(
    r"(video game|film|web series|television series|tv series|miniseries|television show|animated series|anime|"
    r"album|song|single|company|brand|smartphone|mobile phone|tablet|processor|operating system|software|"
    r"application|mobile app|website|social network|cricket|football|tournament|league|championship|"
    r"world cup|grand prix|festival|cryptocurrency|stock exchange|market index|bank|airline|automobile|"
    r"motorcycle|vehicle|console|streaming|startup|e-commerce|rocket|spacecraft|space mission|satellite|"
    r"franchise|series|artificial intelligence|chatbot|processor|electric car)", re.I)
BAD_PAGES = {"Main Page", "Special:Search", "Wikipedia:Featured pictures", "Portal:Current events"}

ROMAN = [("X", 10), ("IX", 9), ("V", 5), ("IV", 4), ("I", 1)]


def _get(url, **kw):
    kw.setdefault("timeout", 20)
    h = dict(UA); h.update(kw.pop("headers", {}))
    return requests.get(url, headers=h, **kw)


def to_roman(n):
    out = ""
    for sym, val in ROMAN:
        while n >= val:
            out += sym; n -= val
    return out


def from_roman(s):
    total, prev = 0, 0
    vals = {"I": 1, "V": 5, "X": 10}
    for ch in reversed(s):
        v = vals[ch]
        total += v if v >= prev else -v
        prev = max(prev, v)
    return total


def fmt_num(n):
    n = float(n)
    for div, suf in ((1e9, "B"), (1e6, "M"), (1e3, "K")):
        if abs(n) >= div:
            x = n / div
            return f"{x:.1f}".rstrip("0").rstrip(".") + suf
    return f"{n:.0f}"


def parse_traffic(s):
    """'200+' -> 200 ; '2K+' -> 2000 ; '1M+' -> 1_000_000"""
    m = re.match(r"\s*([\d,\.]+)\s*([KkMm]?)", s or "")
    if not m: return 0
    v = float(m.group(1).replace(",", ""))
    return int(v * {"": 1, "k": 1e3, "m": 1e6}[m.group(2).lower()])


# ---- 1. what is India searching for ---------------------------------------------------------
def fetch_trending_india():
    r = _get(GTRENDS_RSS)
    r.raise_for_status()
    root = ET.fromstring(r.content)
    items = []
    for it in root.iter("item"):
        d = {"title": "", "traffic": "", "news": []}
        for ch in it:
            tag = ch.tag.split("}")[-1]
            if tag == "title": d["title"] = (ch.text or "").strip()
            elif tag == "approx_traffic": d["traffic"] = (ch.text or "").strip()
            elif tag == "news_item":
                for sub in ch:
                    if sub.tag.split("}")[-1] == "news_item_title":
                        d["news"].append((sub.text or "").strip())
        if d["title"]:
            d["traffic_min"] = parse_traffic(d["traffic"])
            items.append(d)
    items.sort(key=lambda x: -x["traffic_min"])
    return items


def fetch_top_wikipedia(days_back=1):
    """Fallback source: most-read English Wikipedia articles (global)."""
    day = datetime.now(timezone.utc) - timedelta(days=days_back)
    r = _get(f"{WIKI_VIEWS}/top/en.wikipedia/all-access/{day:%Y/%m/%d}")
    r.raise_for_status()
    arts = r.json()["items"][0]["articles"]
    out = []
    for a in arts[:60]:
        t = a["article"].replace("_", " ")
        if t in BAD_PAGES or ":" in t: continue
        out.append({"title": t, "traffic": "", "traffic_min": 0, "news": []})
    return out


# ---- 2. is it a safe, quantifiable topic? ----------------------------------------------------
def resolve_wikipedia(term):
    """Return {'title','description','extract'} for the best matching, non-person article, else None."""
    r = _get("https://en.wikipedia.org/w/api.php",
             params={"action": "query", "list": "search", "srsearch": term, "srlimit": 1, "format": "json"})
    hits = r.json().get("query", {}).get("search", [])
    if not hits: return None
    title = hits[0]["title"]
    return wiki_summary(title)


def wiki_summary(title):
    r = _get(f"https://en.wikipedia.org/api/rest_v1/page/summary/{quote(title.replace(' ', '_'), safe='')}")
    if r.status_code != 200: return None
    j = r.json()
    if j.get("type") != "standard": return None
    return {"title": j.get("title", title), "description": j.get("description", "") or "",
            "extract": j.get("extract", "") or ""}


def is_safe_topic(term, news, wiki):
    blob = " ".join([term, wiki["title"], wiki["description"]] + news)
    if BLOCK.search(blob): return False
    if PERSON.search(wiki["description"]) or re.search(r"\(born |\bdied\b", wiki["extract"][:300]): return False
    if not ALLOW.search(wiki["description"]): return False
    return True


def title_matches(term, wiki_title):
    a = set(re.findall(r"[a-z0-9]+", term.lower())); b = set(re.findall(r"[a-z0-9]+", wiki_title.lower()))
    if not a: return False
    # allow common abbreviations such as "gta 6" -> "Grand Theft Auto VI": accept if the search engine
    # returned it at rank 1 and at least one token overlaps OR the term is short (<=2 words)
    return bool(a & b) or len(a) <= 2


# ---- 3. the numbers --------------------------------------------------------------------------
def daily_views(title, days=100):
    end = datetime.now(timezone.utc) - timedelta(days=1)
    start = end - timedelta(days=days - 1)
    art = quote(title.replace(" ", "_"), safe="")
    r = _get(f"{WIKI_VIEWS}/per-article/en.wikipedia/all-access/user/{art}/daily/{start:%Y%m%d}/{end:%Y%m%d}")
    if r.status_code != 200: return []
    return [(i["timestamp"][:8], i["views"]) for i in r.json().get("items", [])]


def monthly_peak(title):
    art = quote(title.replace(" ", "_"), safe="")
    end = datetime.now(timezone.utc).replace(day=1) - timedelta(days=1)  # last full month
    r = _get(f"{WIKI_VIEWS}/per-article/en.wikipedia/all-access/user/{art}/monthly/2015070100/{end:%Y%m}0100")
    if r.status_code != 200: return None
    items = r.json().get("items", [])
    if not items: return None
    best = max(items, key=lambda i: i["views"])
    ts = best["timestamp"]
    return {"views": best["views"], "label": datetime.strptime(ts[:6], "%Y%m").strftime("%b %Y")}


def surge(series):
    """Last 7 days vs the 90 days before that."""
    if len(series) < 40: return None
    vals = [v for _, v in series]
    last7 = sum(vals[-7:]) / 7
    base_vals = vals[-97:-7]
    base = sum(base_vals) / len(base_vals)
    peak_day, peak_views = max(series, key=lambda x: x[1])
    return {"avg7": last7, "base90": base, "growth": (last7 / base - 1) * 100 if base > 0 else None,
            "last30": sum(vals[-30:]), "peak_day": datetime.strptime(peak_day, "%Y%m%d").strftime("%d %b"),
            "peak_views": peak_views}


def predecessor_title(title):
    """'Grand Theft Auto VI' -> 'Grand Theft Auto V' ; 'iPhone 17' -> 'iPhone 16' ; 'Pushpa 2' -> 'Pushpa'."""
    m = re.match(r"^(.*?)[\s:]+([IVX]{1,6}|\d{1,2})$", title.strip())
    if not m: return None
    base, num = m.group(1).strip(" :"), m.group(2)
    roman = num.isalpha()
    try:
        n = from_roman(num) if roman else int(num)
    except KeyError:
        return None
    if n < 2: return None
    prev = n - 1
    if prev == 1: return base
    return f"{base} {to_roman(prev) if roman else prev}"


# ---- 3b. India then vs now (World Bank) -------------------------------------------------------
WB_IN = "https://api.worldbank.org/v2/country/IN/indicator/{}"
import json, os
_DEFAULT_CFG = {
    "trend": {"min_year_gap": 2, "min_growth_percent": 60, "min_avg_daily_views": 1500, "min_indicators_needed": 5},
    "carousel": {"max_slides": 10, "one_indicator_per_slide": True, "summary_table": True, "summary_max_rows": 8},
    "stories": {"enabled": True},
    "indicators": [
        {"key": "gdp", "code": "NY.GDP.MKTP.CD", "sector": "ECONOMY", "label": "GDP", "kind": "usd", "better": "up"},
        {"key": "gdppc", "code": "NY.GDP.PCAP.CD", "sector": "INCOME", "label": "GDP per person", "kind": "usd", "better": "up"},
        {"key": "pop", "code": "SP.POP.TOTL", "sector": "POPULATION", "label": "Population", "kind": "pop", "better": "neutral"},
        {"key": "net", "code": "IT.NET.USER.ZS", "sector": "DIGITAL", "label": "Internet users", "kind": "pct", "better": "up"},
        {"key": "life", "code": "SP.DYN.LE00.IN", "sector": "HEALTH", "label": "Life expectancy", "kind": "yrs", "better": "up"}]}


def load_config():
    """config.json next to this file; falls back to built-in defaults if missing or broken."""
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")) as f:
            cfg = json.load(f)
        for k, v in _DEFAULT_CFG.items():
            cfg.setdefault(k, v)
        return cfg
    except Exception as e:
        print("  config.json not usable, using defaults:", e)
        return _DEFAULT_CFG


CFG = load_config()
INDICATORS = CFG["indicators"]


def release_year(w):
    m = re.search(r"\b(19[89]\d|20[0-4]\d)\b", w.get("description", ""))
    if m: return int(m.group(1))
    m = re.search(r"released[^.]{0,40}?((?:19|20)\d{2})", w.get("extract", "")[:400])
    return int(m.group(1)) if m else None


def wb_series(code):
    r = _get(WB_IN.format(code), params={"format": "json", "per_page": 100, "date": "1990:2030"})
    rows = r.json()[1] or []
    return {int(d["date"]): d["value"] for d in rows if d.get("value") is not None}


def _pick(series, year):
    """Latest data point at or before `year`."""
    ys = [y for y in series if y <= year]
    return (max(ys), series[max(ys)]) if ys else None


def fmt_value(kind, v):
    if kind == "usd":
        if v >= 1e12: return f"${v / 1e12:.2f}T"
        return "$" + (fmt_num(v) if v >= 10000 else f"{v:,.0f}")
    if kind == "pop": return f"{v / 1e9:.2f}B" if v >= 1e9 else fmt_num(v)
    if kind == "pct": return f"{v:.0f}%"
    if kind == "yrs": return f"{v:.1f} yrs"
    return f"{v:.0f}"


def india_then_now(y_then, y_now, log=print):
    rows = []
    for ind in INDICATORS:
        try:
            s = wb_series(ind["code"])
            a, b = _pick(s, y_then), _pick(s, y_now)
            if a and b and b[0] > a[0]:
                rows.append({**ind, "then_year": a[0], "now_year": b[0], "then": a[1], "now": b[1],
                             "then_s": fmt_value(ind["kind"], a[1]), "now_s": fmt_value(ind["kind"], b[1]),
                             "ratio": (b[1] / a[1]) if a[1] else None})
        except Exception as e:
            log(f"  India then/now: {ind['key']} unavailable ({e})")
    return rows if len(rows) >= CFG["trend"]["min_indicators_needed"] else None


MIN_AVG_VIEWS = CFG["trend"]["min_avg_daily_views"]   # ignore topics nobody reads
MIN_GROWTH = float(CFG["trend"]["min_growth_percent"])  # % growth, last 7 days vs previous 90-day average


def find_trend(recent_captions=(), max_candidates=15, log=print):
    """Return a dict describing the best qualifying trend, or None."""
    candidates, src = [], "Google Trends (India)"
    try:
        candidates = fetch_trending_india()
    except Exception as e:
        log(f"  Trend radar: Google Trends unavailable ({e})")
    if not candidates:
        try:
            candidates, src = fetch_top_wikipedia(), "Wikipedia most-read"
        except Exception as e:
            log(f"  Trend radar: no trend source reachable ({e})"); return None
    recent = " ".join(recent_captions).lower()
    for c in candidates[:max_candidates]:
        term = c["title"]
        try:
            if BLOCK.search(term + " " + " ".join(c["news"])): continue
            wiki = resolve_wikipedia(term) if src.startswith("Google") else wiki_summary(term)
            if not wiki or not title_matches(term, wiki["title"]): continue
            if not is_safe_topic(term, c["news"], wiki): continue
            if wiki["title"].lower() in recent or term.lower() in recent: continue
            s = surge(daily_views(wiki["title"]))
            if not s or s["growth"] is None or s["avg7"] < MIN_AVG_VIEWS or s["growth"] < MIN_GROWTH: continue
            out = {"term": term, "title": wiki["title"], "description": wiki["description"], "source": src,
                   "traffic": c["traffic"], "traffic_min": c["traffic_min"], "surge": s, "pred": None}
            pt = predecessor_title(wiki["title"])
            if pt:
                pw = wiki_summary(pt)
                kind = lambda w: (ALLOW.search(w["description"]) or [None])[0] and ALLOW.search(w["description"]).group(0).lower()
                if pw and kind(pw) == kind(wiki):
                    ps = surge(daily_views(pw["title"])); pk = monthly_peak(pw["title"])
                    if ps and pk:
                        out["pred"] = {"title": pw["title"], "surge": ps, "peak": pk,
                                       "ratio": s["last30"] / pk["views"] if pk["views"] else None,
                                       "year": release_year(pw)}
                        y_then = out["pred"]["year"]
                        y_now = release_year(wiki) or datetime.now(timezone.utc).year
                        if y_then and y_now - y_then >= CFG["trend"]["min_year_gap"]:
                            out["india"] = {"y_then": y_then, "y_now": y_now,
                                            "rows": india_then_now(y_then, y_now, log)}
            log(f"  Trend radar: picked '{wiki['title']}' ({s['growth']:+.0f}% vs 90-day avg)")
            return out
        except Exception as e:
            log(f"  Trend radar: skipped '{term}' ({e})")
    log("  Trend radar: nothing qualified today")
    return None


def short_title(t, n=26):
    t = re.sub(r"\s*\(.*?\)", "", t)
    return t if len(t) <= n else t[: n - 1].rstrip() + "."


def poster_args(t):
    """Arguments for the s1_white poster + the Instagram caption."""
    s, p = t["surge"], t["pred"]
    name = short_title(t["title"])
    hero = f"{s['growth']:+.0f}%" if abs(s["growth"]) < 10000 else f"{s['growth'] / 100:.0f}x"
    hero_sub = "Wikipedia page views, last 7 days vs 90-day average"
    stats = [(fmt_num(s["avg7"]), "VIEWS PER DAY NOW")]
    if t["traffic_min"]:
        stats.append((t["traffic"], "GOOGLE SEARCHES, INDIA"))
    else:
        stats.append((fmt_num(s["peak_views"]), f"PEAK DAY ({s['peak_day']})"))
    if p and p["ratio"]:
        pn = short_title(p["title"], 16)
        stats.append((f"{p['ratio'] * 100:.0f}%", f"OF {pn.upper()} PEAK MONTH" if len(pn) <= 16 and not pn.endswith(".") else "OF PREVIOUS PEAK MONTH"))
    else:
        stats.append((fmt_num(s["peak_views"]), f"PEAK DAY ({s['peak_day']})"))
    source = "Source: Wikimedia page views (global), Google Trends India"
    title = name.upper()
    lines = [f"{t['title']} is trending in India right now.", "",
             f"Wikipedia page views are up {s['growth']:+.0f}% in the last 7 days versus the 90 days before "
             f"({fmt_num(s['avg7'])} views a day, up from {fmt_num(s['base90'])}).",
             f"Peak day in the last 100 days: {s['peak_day']} with {fmt_num(s['peak_views'])} views."]
    if t["traffic_min"]:
        lines.append(f"Google searches in India: {t['traffic']}.")
    if p and p["ratio"]:
        lines += ["", f"Compared with {p['title']}: its best month since 2015 was {p['peak']['label']} "
                      f"({fmt_num(p['peak']['views'])} views). {t['title']} drew {fmt_num(s['last30'])} in the last 30 days, "
                      f"that is {p['ratio'] * 100:.0f}% of that peak."]
    lines += ["", "Page views are global English Wikipedia counts and show attention, not sales or audience size."]
    tag = re.sub(r"[^A-Za-z0-9]", "", short_title(t["title"], 30))
    tags = f"#Trending #TrendingInIndia #{tag} #DataStory #IndiaByData"
    return title, hero, hero_sub, stats, source, "\n".join(lines) + "\n\n" + tags


def change_text(r):
    """Plain-words change: a multiple for big amounts, a difference for percentages and rates."""
    if r["kind"] in ("usd", "pop"):
        return f"{r['ratio']:.1f}x" if r["ratio"] else "n/a"
    d = r["now"] - r["then"]
    unit = {"pct": " pts", "yrs": " yrs"}.get(r["kind"], "")
    return f"{d:+.1f}{unit}" if r["kind"] == "yrs" else f"{d:+.0f}{unit}"


def sentiment(r):
    d = r["now"] - r["then"]
    if r.get("better") == "neutral" or abs(d) < 1e-9: return "amber"
    return "green" if (d > 0) == (r["better"] == "up") else "red"


def india_args(t):
    """Carousel pieces for the then-vs-now story: (list of s1_white kwargs per indicator, s12 kwargs for the summary table
    or None, caption text). None when there is no usable comparison. Layout comes from config.json."""
    ind, p = t.get("india"), t.get("pred")
    if not ind or not ind.get("rows") or not p: return None
    cc = CFG["carousel"]
    y0, y1 = ind["y_then"], ind["y_now"]
    pn = short_title(p["title"], 22)
    rows = ind["rows"]
    room = max(1, cc["max_slides"] - 1 - (1 if cc["summary_table"] else 0))   # 1 slot for the trend cover
    shown = rows[:room] if cc["one_indicator_per_slide"] else []
    slides = []
    for r in shown:
        slides.append(dict(
            title=r["label"], hero=r["now_s"],
            hero_sub=f"{r['sector'].title()}, {r['now_year']}",
            hero_sent=sentiment(r),
            stats=[(r["then_s"], f"THEN ({r['then_year']})"), (r["now_s"], f"NOW ({r['now_year']})"),
                   (change_text(r), "CHANGE")],
            source="Source: World Bank, latest year available", kicker=f"INDIA SINCE {pn}".upper()))
    table = None
    if cc["summary_table"]:
        items = [(f"{r['label']} ({r['then_year']} to {r['now_year']})", f"{r['then_s']} to {r['now_s']}")
                 for r in rows][:cc["summary_max_rows"]]
        table = dict(words=["INDIA", "THEN VS NOW"], tag=f"{y0}-{y1}", items=items,
                     source="Source: World Bank (latest year available per indicator)")
    lines = [f"India then vs now: {p['title']} ({y0}) to {t['title']} ({y1}), World Bank data:"]
    lines += [f"- {r['label'] if r['sector'].lower() == r['label'].lower() else r['sector'].title() + ', ' + r['label']}: {r['then_s']} ({r['then_year']}) to {r['now_s']} ({r['now_year']})"
              for r in rows]
    return slides, table, "\n".join(lines)
