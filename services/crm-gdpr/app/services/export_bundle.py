"""Export als JSON-, CSV- und PDF-Bundle."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from io import StringIO


def flatten_snapshot_for_csv(snapshot: dict[str, Any]) -> list[list[str]]:
    rows: list[list[str]] = [["section", "path", "value"]]

    def walk(prefix: str, obj: Any) -> None:
        if obj is None:
            rows.append([prefix, "", ""])
            return
        if isinstance(obj, (str, int, float, bool)):
            rows.append([prefix, "", str(obj)])
            return
        if isinstance(obj, list):
            for i, item in enumerate(obj):
                walk(f"{prefix}[{i}]", item)
            return
        if isinstance(obj, dict):
            for k, v in obj.items():
                walk(f"{prefix}.{k}" if prefix else k, v)
            return
        rows.append([prefix, "", str(obj)])

    for key in ("contacts", "activities", "opportunities", "consents", "campaign_recipients"):
        if snapshot.get(key) is not None:
            walk(key, snapshot[key])
    for err in snapshot.get("_errors") or []:
        rows.append(["_errors", "", json.dumps(err, ensure_ascii=False)])
    return rows


def write_json(path: Path, snapshot: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        json.dump(snapshot, fh, indent=2, ensure_ascii=False)


def write_csv(path: Path, snapshot: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = flatten_snapshot_for_csv(snapshot)
    buf = StringIO()
    writer = csv.writer(buf)
    writer.writerows(rows)
    path.write_text(buf.getvalue(), encoding="utf-8")


def write_pdf(path: Path, snapshot: dict[str, Any], title: str) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas

    path.parent.mkdir(parents=True, exist_ok=True)
    c = canvas.Canvas(str(path), pagesize=A4)
    width, height = A4
    y = height - 50
    c.setFont("Helvetica-Bold", 12)
    c.drawString(40, y, title)
    y -= 28
    c.setFont("Helvetica", 9)
    text = json.dumps(snapshot, indent=2, ensure_ascii=False)
    chunk = 4200
    pos = 0
    line_height = 12
    while pos < len(text):
        block = text[pos : pos + chunk]
        for line in block.splitlines():
            if y < 50:
                c.showPage()
                y = height - 50
                c.setFont("Helvetica", 9)
            c.drawString(40, y, line[:120])
            y -= line_height
        pos += chunk
        if pos < len(text):
            y -= line_height
    c.save()
