#!/usr/bin/env python
"""Remove handbook screenshots that are blank/spinner-only (image heuristic).

Usage:
  python scripts/prune_handbuch_spinner_screenshots.py
  python scripts/prune_handbuch_spinner_screenshots.py --dry-run
"""

from __future__ import annotations

import argparse
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

REPO = Path(__file__).resolve().parents[1]
IMG_DIR = REPO / "docs" / "benutzerhandbuch" / "img"
SOURCE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def is_spinner_like_image(path: Path) -> tuple[bool, str]:
    """Heuristic: main pane mostly uniform with almost no UI chrome/text."""
    with Image.open(path) as img:
        rgb = img.convert("RGB")
        w, h = rgb.size
        left = int(w * 0.22)
        top = int(h * 0.12)
        bottom = h - max(60, int(h * 0.08))
        crop = rgb.crop((left, top, w - 16, bottom))
        pixels = list(crop.getdata())
        if not pixels:
            return True, "empty crop"

        buckets = [(r // 16 * 16, g // 16 * 16, b // 16 * 16) for r, g, b in pixels]
        (bg, bg_count) = Counter(buckets).most_common(1)[0]
        bg_ratio = bg_count / len(pixels)

        def dist(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
            return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

        non_bg = [p for p in buckets if dist(p, bg) > 36]
        non_bg_ratio = len(non_bg) / len(pixels)

        # Spinner / page loader: >92% one background tone, <1.5% other pixels
        if bg_ratio >= 0.92 and non_bg_ratio <= 0.015:
            return True, f"uniform main ({bg_ratio:.0%} bg, {non_bg_ratio:.2%} detail)"

        # Nearly empty loader with tiny center cluster
        if bg_ratio >= 0.88 and non_bg_ratio <= 0.008:
            return True, f"minimal detail ({non_bg_ratio:.2%})"

        return False, f"ok ({bg_ratio:.0%} bg, {non_bg_ratio:.1%} detail)"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args(argv)

    if not IMG_DIR.is_dir():
        print(f"error: missing {IMG_DIR}", file=sys.stderr)
        return 1

    removed = 0
    kept = 0
    for path in sorted(IMG_DIR.iterdir()):
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        drop, reason = is_spinner_like_image(path)
        webp = path.with_suffix(".webp")
        if drop:
            removed += 1
            print(f"REMOVE {path.name} — {reason}")
            if not args.dry_run:
                path.unlink(missing_ok=True)
                webp.unlink(missing_ok=True)
        else:
            kept += 1

    print("-" * 60)
    print(f"kept={kept} removed={removed}" + (" (dry-run)" if args.dry_run else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
