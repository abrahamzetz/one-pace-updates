import re, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

FEED = "https://onepace.net/en/releases/rss.xml"
TOPIC = "one-pace-updates-abrahamzetz"
MIN_CHAPTER = 1013 # everything after Wano 62
SEEN = Path("seen.txt")
NS = {"t": "http://xmlns.ezrss.it/0.1/"}

req = urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0"})
root = ET.fromstring(urllib.request.urlopen(req).read())

first_run = not SEEN.exists()
seen = set(SEEN.read_text().split()) if not first_run else set()

for item in root.iter("item"):
    guid = item.findtext("guid")
    if guid in seen:
        continue
    seen.add(guid)
    if first_run: # seed silently
        continue
    title = item.findtext("title")
    link = item.findtext("link")
    fname = item.findtext("t:fileName", default="", namespaces=NS)
    m = re.search(r"\]\[(\d+)(?:-\d+)?\]", fname)
    if m and int(m.group(1)) >= MIN_CHAPTER:
        urllib.request.urlopen(urllib.request.Request(
            f"https://ntfy.sh/{TOPIC}",
            data=title.encode(),
            headers={"Title": "New One Pace release", "Click": link},
        ))

SEEN.write_text("\n".join(sorted(seen)))
