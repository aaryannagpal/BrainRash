import re
import sys
import urllib.request
from pathlib import Path

import feedparser

FEED_URL = "https://brainrash.substack.com/feed"
THREADS_DIR = Path("threads")
GRID_START = "<!-- GRID:START -->"
GRID_END = "<!-- GRID:END -->"
COLUMNS = 3

def fetch_feed():
    req = urllib.request.Request(FEED_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return feedparser.parse(resp.read())

def extract_prefix_and_index(title):
    match = re.match(r"^(.{5})[\s_-]+(\d+)", title.strip())
    if not match:
        return None, None
    return match.group(1).lower(), int(match.group(2))

def extract_image(entry):
    candidates = []
    if entry.get("media_thumbnail"):
        candidates.append(entry["media_thumbnail"][0].get("url"))
    if entry.get("enclosures"):
        for enc in entry["enclosures"]:
            if enc.get("type", "").startswith("image"):
                candidates.append(enc.get("href") or enc.get("url"))
    if entry.get("media_content"):
        candidates.append(entry["media_content"][0].get("url"))
    html = entry.get("content", [{}])[0].get("value", "") or entry.get("summary", "")
    img_match = re.search(r'<img[^>]+src="([^"]+)"', html)
    if img_match:
        candidates.append(img_match.group(1))
    for c in candidates:
        if c and "subscribe-card" not in c:
            return c
    return None

def build_collage(posts):
    posts = [p for p in posts if p["image"]]
    if not posts:
        return None
    posts = sorted(posts, key=lambda p: p["index"])
    items = []
    for p in posts:
        items.append(
            f'<a href="{p["link"]}" title="{p["title"]}">'
            f'<img src="{p["image"]}" width="200" '
            f'style="border-radius:10px;margin:6px;">'
            f'</a>'
        )
    return " ".join(items)

def update_readme(path, grid_md):
    text = path.read_text(encoding="utf-8")
    if GRID_START not in text or GRID_END not in text:
        print(f"skip {path}: markers not found")
        return
    pattern = re.compile(re.escape(GRID_START) + r".*?" + re.escape(GRID_END), re.DOTALL)
    path.write_text(pattern.sub(f"{GRID_START}\n{grid_md}\n{GRID_END}", text), encoding="utf-8")


def main():
    feed = fetch_feed()
    raw_posts = []
    for entry in feed.entries:
        prefix, index = extract_prefix_and_index(entry.title)
        if prefix is None:
            continue
        raw_posts.append({
            "prefix": prefix, "title": entry.title, "link": entry.link,
            "index": index, "image": extract_image(entry),
        })

    image_counts = {}
    for p in raw_posts:
        if p["image"]:
            image_counts[p["image"]] = image_counts.get(p["image"], 0) + 1

    by_prefix = {}
    for p in raw_posts:
        if p["image"] and image_counts[p["image"]] > 1:
            p["image"] = None
        by_prefix.setdefault(p["prefix"], []).append(p)

    if not THREADS_DIR.exists():
        print(f"no {THREADS_DIR} directory found")
        sys.exit(0)

    for thread_dir in THREADS_DIR.iterdir():
        readme = thread_dir / "README.md"
        if not thread_dir.is_dir() or not readme.exists():
            continue
        posts = by_prefix.get(thread_dir.name.lower(), [])
        collage_md = build_collage(posts)
        update_readme(readme, collage_md or "_No posts with images yet._")

if __name__ == "__main__":
    main()
