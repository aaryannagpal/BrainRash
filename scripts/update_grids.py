import json
import re
import sys
import urllib.parse
import urllib.request
from pathlib import Path

FEED_URL = "https://brainrash.substack.com/feed"
RSS2JSON_URL = "https://api.rss2json.com/v1/api.json?rss_url=" + urllib.parse.quote(FEED_URL)
THREADS_DIR = Path("threads")
GRID_START = "<!-- GRID:START -->"
GRID_END = "<!-- GRID:END -->"


def fetch_items():
    req = urllib.request.Request(RSS2JSON_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    if data.get("status") != "ok":
        raise RuntimeError(f"rss2json returned: {data}")
    return data["items"]


def extract_prefix_and_index(title):
    match = re.match(r"^(.{5})[\s_-]+(\d+)", title.strip())
    if not match:
        return None, None
    return match.group(1).lower(), int(match.group(2))


def extract_image(item):
    candidates = []
    enclosure = item.get("enclosure") or {}
    if enclosure.get("link", "").startswith("http") and "image" in enclosure.get("type", ""):
        candidates.append(enclosure["link"])
    if item.get("thumbnail"):
        candidates.append(item["thumbnail"])
    html = item.get("content") or item.get("description") or ""
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


def update_readme(path, body_md):
    text = path.read_text(encoding="utf-8")
    if GRID_START not in text or GRID_END not in text:
        print(f"skip {path}: markers not found")
        return
    pattern = re.compile(re.escape(GRID_START) + r".*?" + re.escape(GRID_END), re.DOTALL)
    path.write_text(pattern.sub(f"{GRID_START}\n{body_md}\n{GRID_END}", text), encoding="utf-8")


def main():
    try:
        items = fetch_items()
    except Exception as e:
        print(f"warning: could not fetch feed ({e}), leaving READMEs untouched")
        sys.exit(0)

    raw_posts = []
    for item in items:
        prefix, index = extract_prefix_and_index(item["title"])
        if prefix is None:
            continue
        raw_posts.append({
            "prefix": prefix, "title": item["title"], "link": item["link"],
            "index": index, "image": extract_image(item),
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