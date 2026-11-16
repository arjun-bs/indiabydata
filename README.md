# IndiaByData auto-poster

Posts 4 India-statistics posters a day to @indiabydata via GitHub Actions (8:00, 13:00, 18:00, 21:00 IST).

Secrets (Settings -> Secrets and variables -> Actions):
- IG_TOKEN   Instagram token (starts with IGAA)
- IMGBB_KEY  imgbb API key (32 characters)
- GH_PAT     (optional) fine-grained token with "Secrets: read and write" - lets the refresh workflow renew IG_TOKEN automatically

Test now: Actions -> "Post to Instagram" -> Run workflow.
