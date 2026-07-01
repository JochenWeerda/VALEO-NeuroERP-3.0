#!/usr/bin/env python
"""Handbuch-Screenshot QC: trimmen, validieren, freigeben, Review-HTML.

Workflow:
  1. Playwright: tests/e2e/handbuch-screenshots.spec.ts
  2. python scripts/handbuch_screenshot_qc.py process      # trim + Bild-QC
  3. python scripts/handbuch_screenshot_qc.py review-html  # Sichtkontrolle
  4. python scripts/handbuch_screenshot_qc.py approve --slug einkauf__bestellungen
  5. python scripts/compress_screenshots.py
  6. python scripts/generate_benutzerhandbuch_full.py

Nur Screenshots mit approval=approved werden ins Handbuch eingebunden.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from PIL import Image, ImageChops

REPO = Path(__file__).resolve().parents[1]
IMG_DIR = REPO / "docs" / "benutzerhandbuch" / "img"
MANIFEST_PATH = REPO / "docs" / "benutzerhandbuch" / "screenshot-manifest.json"
REVIEW_HTML = REPO / "docs" / "benutzerhandbuch" / "screenshot-review.html"
SOURCE_SUFFIXES = {".png", ".jpg", ".jpeg"}
MIN_W, MIN_H = 280, 140
MIN_H_AFTER_TRIM = 150


def load_manifest() -> dict:
    if not MANIFEST_PATH.is_file():
        return {"entries": [], "routeCount": 0}
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def save_manifest(data: dict) -> None:
    data["updatedAt"] = datetime.now(timezone.utc).isoformat()
    MANIFEST_PATH.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def trim_whitespace(path: Path, tolerance: int = 18) -> tuple[Path, tuple[int, int, int, int] | None]:
    """Crop uniform borders; returns bbox or None if unchanged."""
    with Image.open(path) as img:
        rgb = img.convert("RGB")
        bg = Image.new("RGB", rgb.size, rgb.getpixel((0, 0)))
        diff = ImageChops.difference(rgb, bg)
        diff = diff.convert("L")
        bbox = diff.point(lambda p: 255 if p > tolerance else 0).getbbox()
        if not bbox:
            return path, None
        if bbox == (0, 0, rgb.width, rgb.height):
            return path, None
        cropped = rgb.crop(bbox)
        if cropped.height < MIN_H_AFTER_TRIM:
            return path, None
        cropped.save(path)
        return path, bbox


def image_qc(path: Path, slug: str = "") -> tuple[bool, str, dict]:
    with Image.open(path) as img:
        rgb = img.convert("RGB")
        w, h = rgb.size
        if w < MIN_W or h < MIN_H:
            return False, f"zu klein ({w}×{h})", {"width": w, "height": h}

        pixels = list(rgb.getdata())
        buckets = [(r // 16 * 16, g // 16 * 16, b // 16 * 16) for r, g, b in pixels]
        (bg, bg_count) = Counter(buckets).most_common(1)[0]
        bg_ratio = bg_count / len(pixels)

        def dist(a: tuple[int, int, int], b: tuple[int, int, int]) -> int:
            return abs(a[0] - b[0]) + abs(a[1] - b[1]) + abs(a[2] - b[2])

        non_bg = [p for p in buckets if dist(p, bg) > 36]
        non_bg_ratio = len(non_bg) / len(pixels)

        metrics = {
            "width": w,
            "height": h,
            "bgRatio": round(bg_ratio, 3),
            "detailRatio": round(non_bg_ratio, 3),
        }

        if bg_ratio >= 0.94 and non_bg_ratio <= 0.012:
            # Verify-/Fehlerkarten: großer neutraler Hintergrund, zentrierter Inhalt
            if not (slug.startswith("verify__") and h >= 200 and non_bg_ratio >= 0.004):
                return False, "spinner/leer (uniform)", metrics
        if non_bg_ratio < 0.006:
            if not (slug.startswith("verify__") and h >= 150):
                return False, "fast leer", metrics

        return True, "ok", metrics


def cmd_process(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    by_slug = {e["slug"]: e for e in manifest.get("entries", [])}

    processed = approved = rejected = pending = 0
    for path in sorted(IMG_DIR.iterdir()):
        if path.suffix.lower() not in SOURCE_SUFFIXES:
            continue
        slug = path.stem
        entry = by_slug.setdefault(
            slug,
            {"path": slug.replace("__", "/"), "slug": slug, "module": "", "status": "ok", "approval": "pending"},
        )

        trim_whitespace(path)
        ok, reason, metrics = image_qc(path, slug)
        entry["imageQc"] = {"ok": ok, "reason": reason, **metrics}

        if not ok:
            entry["approval"] = "rejected"
            entry["status"] = "rejected"
            entry["detail"] = reason
            path.unlink(missing_ok=True)
            path.with_suffix(".webp").unlink(missing_ok=True)
            rejected += 1
        elif entry.get("approval") == "approved":
            approved += 1
        else:
            entry["approval"] = "pending"
            pending += 1

        processed += 1

    manifest["entries"] = sorted(by_slug.values(), key=lambda e: e.get("path", ""))
    save_manifest(manifest)
    print(f"process: {processed} images — approved={approved} pending={pending} rejected={rejected}")
    return 0


def cmd_review_html(_args: argparse.Namespace) -> int:
    manifest = load_manifest()
    entries = manifest.get("entries", [])

    def card(entry: dict) -> str:
        slug = entry.get("slug", "")
        png = IMG_DIR / f"{slug}.png"
        webp = IMG_DIR / f"{slug}.webp"
        img = f"img/{webp.name}" if webp.is_file() else (f"img/{png.name}" if png.is_file() else "")
        issues = entry.get("qc", {}).get("issues") or []
        if entry.get("detail"):
            issues = [*issues, entry["detail"]]
        img_qc = entry.get("imageQc", {})
        badge = entry.get("approval", "pending")
        color = {"approved": "#16a34a", "pending": "#ca8a04", "rejected": "#dc2626"}.get(badge, "#64748b")
        img_tag = f'<img src="{img}" alt="{slug}" loading="lazy" />' if img else "<p><em>Kein Bild</em></p>"
        return f"""
        <article class="card" data-slug="{slug}" data-approval="{badge}">
          <header><span class="badge" style="background:{color}">{badge}</span> <code>{entry.get('path','')}</code></header>
          {img_tag}
          <ul>{''.join(f'<li>{re.sub("<", "&lt;", str(i))}</li>' for i in issues) or '<li>Keine Hinweise</li>'}</ul>
          <p class="meta">{img_qc.get('width','?')}×{img_qc.get('height','?')} · {entry.get('qc',{}).get('metrics',{}).get('captureSelector','')}</p>
        </article>"""

    pending = [e for e in entries if e.get("approval") == "pending"]
    approved = [e for e in entries if e.get("approval") == "approved"]
    rejected = [e for e in entries if e.get("approval") == "rejected"]

    html = f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="utf-8" /><title>Handbuch-Screenshot Review</title>
<style>
body {{ font-family: system-ui, sans-serif; margin: 1rem 2rem; background: #f8fafc; }}
h1 {{ margin-bottom: .25rem; }} .stats {{ color: #475569; margin-bottom: 1.5rem; }}
.grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 1rem; }}
.card {{ background: #fff; border: 1px solid #e2e8f0; border-radius: 8px; padding: .75rem; }}
.card img {{ width: 100%; height: auto; border: 1px solid #e2e8f0; border-radius: 4px; }}
.badge {{ color: #fff; padding: 2px 8px; border-radius: 999px; font-size: 12px; }}
.meta {{ font-size: 12px; color: #64748b; }}
code {{ font-size: 12px; }}
.help {{ background: #eff6ff; border: 1px solid #bfdbfe; padding: 1rem; border-radius: 8px; margin-bottom: 1rem; }}
</style></head><body>
<h1>Handbuch-Screenshot Sichtkontrolle</h1>
<p class="stats">approved={len(approved)} · pending={len(pending)} · rejected={len(rejected)} · gesamt={len(entries)}</p>
<div class="help">
  <strong>Freigabe:</strong> Nur <code>approval=approved</code> erscheint im Handbuch.<br />
  Einzeln: <code>python scripts/handbuch_screenshot_qc.py approve --slug &lt;slug&gt;</code><br />
  Alle pending mit Bild: <code>python scripts/handbuch_screenshot_qc.py approve-all-pending</code>
</div>
<h2>Pending ({len(pending)})</h2><div class="grid">{''.join(card(e) for e in pending) or '<p>Keine.</p>'}</div>
<h2>Approved ({len(approved)})</h2><div class="grid">{''.join(card(e) for e in approved[:48])}{'…' if len(approved)>48 else ''}</div>
<h2>Rejected ({len(rejected)})</h2><div class="grid">{''.join(card(e) for e in rejected[:24])}</div>
</body></html>"""
    REVIEW_HTML.write_text(html, encoding="utf-8")
    print(f"review-html: {REVIEW_HTML}")
    return 0


def cmd_approve(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    slugs = set(args.slug or [])
    if args.all_pending:
        slugs = {e["slug"] for e in manifest.get("entries", []) if e.get("approval") == "pending"}

    changed = 0
    for entry in manifest.get("entries", []):
        if entry.get("slug") in slugs:
            webp = IMG_DIR / f"{entry['slug']}.webp"
            png = IMG_DIR / f"{entry['slug']}.png"
            if not webp.is_file() and not png.is_file():
                continue
            entry["approval"] = "approved"
            entry["status"] = "ok"
            changed += 1

    save_manifest(manifest)
    print(f"approve: {changed} screenshot(s)")
    return 0


def cmd_reject(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    slugs = set(args.slug or [])
    for entry in manifest.get("entries", []):
        if entry.get("slug") in slugs:
            entry["approval"] = "rejected"
            entry["status"] = "rejected"
            for ext in (".png", ".webp"):
                (IMG_DIR / f"{entry['slug']}{ext}").unlink(missing_ok=True)
    save_manifest(manifest)
    print(f"reject: {len(slugs)} slug(s)")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_process = sub.add_parser("process", help="PNG trimmen + Bild-QC")
    p_process.set_defaults(func=cmd_process)

    p_review = sub.add_parser("review-html", help="Review-Galerie erzeugen")
    p_review.set_defaults(func=cmd_review_html)

    p_approve = sub.add_parser("approve", help="Screenshot(s) freigeben")
    p_approve.add_argument("--slug", action="append")
    p_approve.add_argument("--all-pending", action="store_true")
    p_approve.set_defaults(func=cmd_approve)

    p_reject = sub.add_parser("reject", help="Screenshot(s) ablehnen + löschen")
    p_reject.add_argument("--slug", action="append", required=True)
    p_reject.set_defaults(func=cmd_reject)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
