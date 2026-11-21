"""Render the next N days of IndiaByData posters (4 a day) into previews/calendar/ + one contact sheet,
so you can see the upcoming rotation of layouts, colours and shapes. Nothing is posted.

    python preview_calendar.py            # next 7 days
    python preview_calendar.py 14 2026-12-01   # 14 days starting 1 Dec 2026
Needs no tokens (dummy values are used)."""
import os, sys, io
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
os.environ.setdefault("IG_TOKEN", "x"); os.environ.setdefault("IMGBB_KEY", "y"); os.environ["DRY_RUN"] = "1"
import post
from PIL import Image, ImageDraw

days = int(sys.argv[1]) if len(sys.argv) > 1 else 7
start = (datetime.strptime(sys.argv[2], "%Y-%m-%d") if len(sys.argv) > 2 else datetime.now()).replace(tzinfo=ZoneInfo("Asia/Kolkata"))
HOURS = {"morning": 8, "afternoon": 13, "evening": 18, "night": 21}
os.makedirs("previews/calendar", exist_ok=True)
tiles, used, per_day = [], [], {}
for d in range(days):
    for slot, (topics, label) in post.SLOTS.items():
        day = start + timedelta(days=d)
        post.now_ist = lambda day=day, h=HOURS[slot]: day.replace(hour=h, minute=0, second=0, microsecond=0)
        try:
            buf, caption = post.get_post(topics, label)
        except Exception as e:
            print("  skipped", day.date(), slot, e); continue
        pal = post._dl._TH.get("name"); acc = post._dl._TH.get("accent")
        used.append((pal, acc)); per_day.setdefault(str(day.date()), []).append(post.LAST_STYLE)
        name = f"previews/calendar/{day.date()}_{slot}_{post.LAST_STYLE}_{pal}.png"
        buf.seek(0); open(name, "wb").write(buf.read()); buf.seek(0)
        tiles.append((Image.open(buf).convert("RGB").resize((216, 270)), f"{day.strftime('%a %d %b')} {HOURS[slot]}:00 {post.LAST_STYLE}"))
cols = 4
rows = (len(tiles) + cols - 1) // cols
sheet = Image.new("RGB", (cols * 226 + 10, rows * 296 + 10), "#777777"); dr = ImageDraw.Draw(sheet)
for i, (im, lbl) in enumerate(tiles):
    x, y = 10 + (i % cols) * 226, 10 + (i // cols) * 296
    sheet.paste(im, (x, y + 20)); dr.text((x, y + 3), lbl, fill="white")
sheet.save("previews/calendar/_sheet.png")
geo_days = {d: v.count("S9") for d, v in per_day.items()}
for d, v in per_day.items(): print(f"  {d}: {' '.join(v)}   (S9 x{geo_days[d]})")
print(f"Days with no geometric post: {[d for d, n in geo_days.items() if n == 0] or 'none'}")
print(f"{len(tiles)} posters, {len(set(used))} different colour/accent pairs. Sheet: previews/calendar/_sheet.png")
