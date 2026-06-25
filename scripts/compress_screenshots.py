#!/usr/bin/env python
"""Compress UI screenshots to WebP to save repository space.

Converts every PNG/JPEG under the target directory (default:
``docs/benutzerhandbuch/img``) to WebP. WebP keeps screenshot text crisp at a
high quality setting while typically shrinking files by 60-85% versus PNG.

Usage:
    python scripts/compress_screenshots.py                 # convert + replace
    python scripts/compress_screenshots.py --keep-original # keep source files
    python scripts/compress_screenshots.py --quality 90    # override quality
    python scripts/compress_screenshots.py path/to/dir     # custom directory
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DIR = REPO_ROOT / "docs" / "benutzerhandbuch" / "img"
SOURCE_SUFFIXES = {".png", ".jpg", ".jpeg"}


def human(num_bytes: int) -> str:
    value = float(num_bytes)
    for unit in ("B", "KB", "MB"):
        if value < 1024 or unit == "MB":
            return f"{value:.1f} {unit}"
        value /= 1024
    return f"{value:.1f} MB"


def convert(path: Path, quality: int, keep_original: bool) -> tuple[int, int]:
    target = path.with_suffix(".webp")
    before = path.stat().st_size
    with Image.open(path) as img:
        # WebP supports RGB/RGBA; normalise palette/other modes.
        if img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGBA" if "A" in img.getbands() else "RGB")
        img.save(target, "WEBP", quality=quality, method=6)
    after = target.stat().st_size
    if not keep_original and path.suffix.lower() != ".webp":
        path.unlink()
    return before, after


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", nargs="?", default=str(DEFAULT_DIR))
    parser.add_argument("--quality", type=int, default=85)
    parser.add_argument("--keep-original", action="store_true")
    args = parser.parse_args(argv)

    base = Path(args.directory)
    if not base.is_absolute():
        base = (REPO_ROOT / base).resolve()
    if not base.is_dir():
        print(f"error: directory not found: {base}", file=sys.stderr)
        return 1

    sources = sorted(
        p for p in base.iterdir() if p.suffix.lower() in SOURCE_SUFFIXES
    )
    if not sources:
        print(f"No PNG/JPEG images to compress in {base}")
        return 0

    total_before = 0
    total_after = 0
    for path in sources:
        before, after = convert(path, args.quality, args.keep_original)
        total_before += before
        total_after += after
        saved = 100 * (1 - after / before) if before else 0
        print(f"{path.name:40s} {human(before):>9} -> {human(after):>9}  (-{saved:.0f}%)")

    saved_total = 100 * (1 - total_after / total_before) if total_before else 0
    print("-" * 72)
    print(
        f"{'TOTAL':40s} {human(total_before):>9} -> {human(total_after):>9}  (-{saved_total:.0f}%)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
