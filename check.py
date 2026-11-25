import re, urllib.request, xml.etree.ElementTree as ET
from pathlib import Path

FEED = "https://onepace.net/en/releases/rss.xml"
TOPIC = "one-pace-updates-abrahamzetz"
MIN_CHAPTER = 1013  # everything after Wano 62
SEEN = Path("seen.txt")
TORRENT = {"t": "http://xmlns.ezrss.it/0.1/"}

req = urllib.request.Request(FEED, headers={"User-Agent": "Mozilla/5.0"})
root = ET.fromstring(urllib.request.urlopen(req).read())
items = root.findall(".//{*}item")
if not items:
    raise SystemExit("No items parsed from feed - format may have changed")

first_run = not SEEN.exists()
seen = set(SEEN.read_text().split()) if not first_run else set()
print("first_run:", first_run, "| already seen:", len(seen), "| items in feed:", len(items))

for item in items:
    guid = item.findtext("{*}guid")
    if guid in seen:
        continue
    seen.add(guid)
    if first_run:  # seed silently
        continue
    title = item.findtext("{*}title") or ""
    link = item.findtext("{*}link")
    fname = item.findtext("t:fileName", default="", namespaces=TORRENT)
    m = re.search(r"\]\[(\d+)(?:-\d+)?\]", fname + " " + title)
    print("new item:", title[:60], "| start chapter:", m.group(1) if m else None)
    if m and int(m.group(1)) >= MIN_CHAPTER:
        clean = re.sub(r"^\[One Pace\]\[[\d-]+\]\s*", "", title)
        clean = re.sub(r"\s*\[1080p\].*$", "", clean)  # -> "Wano 63"
        urllib.request.urlopen(urllib.request.Request(
            f"https://ntfy.sh/{TOPIC}",
            data=(clean or title).encode(),
            headers={"Title": "New One Pace release", "Click": link},
        ))

SEEN.write_text("\n".join(sorted(seen)))
