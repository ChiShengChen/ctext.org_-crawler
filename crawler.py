import argparse
import json
import time
from pathlib import Path
from urllib import error, request

BASE_URL = "https://ctext.org/tools/api"


def _sanitize(name: str) -> str:
    """Return a filesystem-friendly representation of *name*.

    Keeps alphanumeric characters, spaces, dashes and underscores and
    strips anything else. The result is also trimmed.
    """
    return "".join(c for c in name if c.isalnum() or c in " -_").strip()


def fetch_node(node: str, language: str) -> dict:
    """Fetch *node* from the ctext API and return the parsed JSON."""
    url = f"{BASE_URL}/{language}/{node.lstrip('/')}"
    req = request.Request(url, headers={"User-Agent": "ctext-crawler"})
    with request.urlopen(req) as resp:
        return json.load(resp)


def crawl(root: str = "zhs", out_dir: Path = Path("texts"), delay: float = 1.0) -> None:
    """Recursively crawl the ctext API starting from *root*.

    ``root`` is the starting node (usually ``"zhs"`` for Chinese texts).
    ``out_dir`` is the directory where downloaded texts are stored.
    ``delay`` specifies the delay (in seconds) between requests.
    """
    stack = [(root, out_dir)]
    visited = set()

    while stack:
        node, path = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        try:
            data = fetch_node(node, "zhs")
        except (error.HTTPError, error.URLError) as e:
            print(f"Failed to fetch {node}: {e}")
            continue
        title = data.get("title") or node
        content = data.get("text") or data.get("content")
        if content:
            filename = _sanitize(title) or f"{node}.txt"
            target = path / f"{filename}.txt"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
        children = (
            data.get("children")
            or data.get("sub")
            or data.get("sections")
            or []
        )
        for child in children:
            child_id = child.get("id") or child.get("path") or child.get("uri")
            child_title = child.get("title", str(child_id))
            stack.append((child_id, path / _sanitize(child_title)))
        time.sleep(delay)


def main() -> None:
    parser = argparse.ArgumentParser(description="Crawl texts from ctext.org")
    parser.add_argument("--output", default="texts", help="Output directory")
    parser.add_argument("--delay", type=float, default=1.0, help="Delay between requests")
    parser.add_argument("--root", default="zhs", help="Root node to start crawling")
    args = parser.parse_args()
    crawl(root=args.root, out_dir=Path(args.output), delay=args.delay)


if __name__ == "__main__":
    main()
