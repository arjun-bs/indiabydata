# IndiaByData auto-poster

Posts 4 India-statistics posters a day to @indiabydata via GitHub Actions (8:00, 13:00, 18:00, 21:00 IST).

Secrets (Settings -> Secrets and variables -> Actions):
- IG_TOKEN   Instagram token (starts with IGAA)
- IMGBB_KEY  imgbb API key (32 characters)
- GH_PAT     (optional) fine-grained token with "Secrets: read and write" - lets the refresh workflow renew IG_TOKEN automatically

Test now: Actions -> "Post to Instagram" -> Run workflow.

Trend radar (6 PM slot): checks Google Trends India + Wikipedia page views, posts a data story when something qualifies.
Switch with a repository variable TREND_MODE = auto | draft | off.

## Configuration
Edit `config.json` to change which indicators the trend radar compares (World Bank codes), the max carousel slides, one-indicator-per-slide, the summary table and stories on/off.

## Rotation
Colour pair (palette + vibrant accent) comes from `design_library.rotation(n)` with n = day*4 + slot: consecutive posts always differ and all 96 pairs are used before any repeats. Preview the coming days with `python preview_calendar.py 14` (no tokens needed). `THEME=off` restores original colours; `THEME=3` pins one.

## Geometric posts
Every day has 1-2 geometric (S9) posts: the first Swiss slot always, the second on even days (`geo_slot()` in post.py). `GEO=1` forces it, `GEO=0` turns it off. `python preview_calendar.py 30` prints the style of every post and flags any day without one.
