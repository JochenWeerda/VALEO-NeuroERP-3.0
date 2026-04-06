#!/usr/bin/env python3
"""Pytest mit periodischem Heartbeat auf stderr (fuer lange CI-/lokale Laeufe).

Beispiel:
  set DATABASE_URL=postgresql://...
  set API_DEV_TOKEN=dev-token
  python scripts/pytest_with_heartbeat.py tests/ --tb=line -ra
"""
from __future__ import annotations

import os
import subprocess
import sys
import threading
import time


def _heartbeat(interval_sec: float = 90.0) -> None:
    start = time.monotonic()
    print("[heartbeat] pytest gestartet", file=sys.stderr, flush=True)
    while not _stop.is_set():
        if _stop.wait(timeout=interval_sec):
            break
        elapsed = int(time.monotonic() - start)
        print(
            f"[heartbeat] pytest laeuft noch … {elapsed}s vergangen",
            file=sys.stderr,
            flush=True,
        )


_stop = threading.Event()


def main() -> int:
    args = [sys.executable, "-m", "pytest", *sys.argv[1:]]
    env = os.environ.copy()
    env.setdefault("PYTHONUNBUFFERED", "1")
    t = threading.Thread(target=_heartbeat, kwargs={"interval_sec": 90.0}, daemon=True)
    t.start()
    try:
        p = subprocess.run(args, env=env)
        return int(p.returncode)
    finally:
        _stop.set()


if __name__ == "__main__":
    raise SystemExit(main())
