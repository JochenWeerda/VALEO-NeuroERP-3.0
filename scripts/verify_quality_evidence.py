#!/usr/bin/env python3
"""Coverage nur fuer denselben Commit und unveraenderten Dateiinhalt wiederverwenden."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, sha: str) -> None:
    if not path.is_file() or path.stat().st_size == 0:
        raise ValueError(f"Nachweis fehlt oder ist leer: {path}")
    path.with_name(path.name + ".evidence.json").write_text(
        json.dumps({"sha": sha, "sha256": digest(path)}, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def verify(path: Path, sha: str) -> None:
    data = json.loads(path.with_name(path.name + ".evidence.json").read_text(encoding="utf-8"))
    if data.get("sha") != sha or data.get("sha256") != digest(path):
        raise ValueError(f"Nachweis gehoert nicht zu diesem Commit/Inhalt: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()
    sha = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    try:
        for path in args.paths:
            (write if args.write else verify)(path, sha)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        raise SystemExit(f"Qualitaetsnachweis ungueltig: {exc}") from exc
    print("Qualitaetsnachweise SHA- und inhaltsgleich.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
