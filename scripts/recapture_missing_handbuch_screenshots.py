#!/usr/bin/env python
"""Re-capture handbook screenshots for rejected/missing slugs."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
IMG = REPO / "docs" / "benutzerhandbuch" / "img"
MANIFEST = REPO / "docs" / "benutzerhandbuch" / "screenshot-manifest.json"
FRONTEND = REPO / "packages" / "frontend-web"


def missing_slugs() -> list[str]:
    if not MANIFEST.is_file():
        return []
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    slugs: list[str] = []
    for entry in data.get("entries", []):
        slug = entry["slug"]
        if not (IMG / f"{slug}.webp").exists() and not (IMG / f"{slug}.png").exists():
            slugs.append(slug)
    return slugs


def main() -> int:
    slugs = missing_slugs()
    if not slugs:
        print("no missing screenshots")
        return 0

    print(f"recapture {len(slugs)} slug(s)")
    env = os.environ.copy()
    env["PLAYWRIGHT_SKIP_WEBSERVER"] = "1"
    env["FRONTEND_BASE_URL"] = env.get("FRONTEND_BASE_URL", "http://127.0.0.1:3001")
    env["HANDBUCH_SKIP_EXISTING"] = "0"
    env["HANDBUCH_SLUGS"] = ",".join(slugs)
    env["HANDBUCH_RENDER_TIMEOUT_MS"] = "60000"

    cmd = [
        "pnpm",
        "exec",
        "playwright",
        "test",
        "tests/e2e/handbuch-screenshots.spec.ts",
        "--project=chromium",
        "--workers=1",
    ]
    result = subprocess.run(cmd, cwd=FRONTEND, env=env)
    if result.returncode != 0:
        return result.returncode

    for step in (
        ["python", str(REPO / "scripts" / "handbuch_screenshot_qc.py"), "process"],
        ["python", str(REPO / "scripts" / "handbuch_screenshot_qc.py"), "approve", "--all-pending"],
        ["python", str(REPO / "scripts" / "compress_screenshots.py")],
        ["python", str(REPO / "scripts" / "generate_benutzerhandbuch_full.py")],
    ):
        r = subprocess.run(step, cwd=REPO)
        if r.returncode != 0:
            return r.returncode
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
