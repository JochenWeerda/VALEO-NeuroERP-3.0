#!/usr/bin/env python3
"""
One-time helper: add summary= to router decorators that lack them.
Derives summary from the Python function name (snake_case → German label).

Safe for multi-line decorators and files with any encoding (UTF-8 / UTF-8-BOM).

Usage:
    python scripts/add_openapi_summaries.py [file1.py file2.py ...]
    # Without args: processes all files in app/api/v1/endpoints/
"""

from __future__ import annotations

import argparse
import os
import re
import sys

ENDPOINTS_DIR = "app/api/v1/endpoints"

_VERB_MAP: dict[str, str] = {
    "list": "auflisten",
    "get": "abrufen",
    "read": "lesen",
    "fetch": "abrufen",
    "create": "anlegen",
    "add": "hinzufügen",
    "post": "erstellen",
    "update": "aktualisieren",
    "patch": "aktualisieren",
    "edit": "bearbeiten",
    "delete": "löschen",
    "remove": "entfernen",
    "cancel": "stornieren",
    "close": "abschließen",
    "approve": "genehmigen",
    "reject": "ablehnen",
    "archive": "archivieren",
    "export": "exportieren",
    "import": "importieren",
    "upload": "hochladen",
    "download": "herunterladen",
    "send": "senden",
    "submit": "einreichen",
    "trigger": "auslösen",
    "execute": "ausführen",
    "run": "ausführen",
    "check": "prüfen",
    "validate": "validieren",
    "search": "suchen",
    "count": "zählen",
    "calculate": "berechnen",
    "generate": "generieren",
    "publish": "veröffentlichen",
    "activate": "aktivieren",
    "deactivate": "deaktivieren",
    "enable": "aktivieren",
    "disable": "deaktivieren",
    "reset": "zurücksetzen",
    "refresh": "aktualisieren",
    "sync": "synchronisieren",
    "process": "verarbeiten",
    "release": "freigeben",
    "lock": "sperren",
    "unlock": "entsperren",
    "block": "blockieren",
    "unblock": "entsperren",
    "assign": "zuweisen",
    "allocate": "zuweisen",
    "transfer": "übertragen",
    "convert": "umwandeln",
    "mark": "markieren",
    "set": "setzen",
    "clear": "leeren",
    "start": "starten",
    "stop": "stoppen",
    "pause": "pausieren",
    "resume": "fortsetzen",
    "retry": "wiederholen",
    "preview": "vorschauen",
    "print": "drucken",
    "scan": "scannen",
    "test": "testen",
    "notify": "benachrichtigen",
    "register": "registrieren",
    "unregister": "abmelden",
    "login": "anmelden",
    "logout": "abmelden",
    "verify": "verifizieren",
    "confirm": "bestätigen",
    "reject_all": "alle ablehnen",
    "accept": "akzeptieren",
    "bulk": "Bulk",
    "batch": "Batch",
    "enrich": "anreichern",
    "merge": "zusammenführen",
    "split": "aufteilen",
    "clone": "klonen",
    "copy": "kopieren",
    "move": "verschieben",
    "reorder": "neuordnen",
    "calculate_price": "Preis berechnen",
    "stream": "streamen",
    "handle": "verarbeiten",
    "forward": "weiterleiten",
    "broadcast": "aussenden",
    "snapshot": "Snapshot erstellen",
    "restore": "wiederherstellen",
    "purge": "bereinigen",
    "flush": "leeren",
    "ping": "anpingen",
}


def _snake_to_summary(name: str) -> str:
    parts = name.split("_")
    verb = parts[0].lower()
    noun_parts = parts[1:]
    action = _VERB_MAP.get(verb, verb)
    noun = " ".join(noun_parts) if noun_parts else ""
    return f"{noun.capitalize()} {action}".strip() if noun else action.capitalize()


def process_file(path: str, dry_run: bool = False) -> int:
    # Read preserving BOM — use utf-8-sig so BOM is stripped from string,
    # then write back as plain utf-8 (BOM-free). This also normalises the file.
    try:
        content = open(path, encoding="utf-8-sig").read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"  SKIP {path}: {e}")
        return 0

    lines = content.splitlines(keepends=True)
    changed = 0
    i = 0
    new_lines: list[str] = []

    while i < len(lines):
        line = lines[i]

        # Does this line start a @router.<method>( decorator?
        if re.match(r'\s*@router\.(get|post|put|patch|delete)\(', line):
            # Collect the complete decorator — all lines until parens balance
            dec_start = i
            dec_buf: list[str] = []
            depth = 0
            j = i
            while j < len(lines):
                l = lines[j]
                dec_buf.append(l)
                depth += l.count("(") - l.count(")")
                j += 1
                if depth <= 0:
                    break

            full_dec = "".join(dec_buf)

            if "summary=" not in full_dec:
                # Find the function name in the next few lines
                func_name: str | None = None
                for k in range(j, min(j + 4, len(lines))):
                    fm = re.match(r'\s*(?:async\s+)?def\s+(\w+)', lines[k])
                    if fm:
                        func_name = fm.group(1)
                        break

                if func_name:
                    summary = _snake_to_summary(func_name)
                    last_line = dec_buf[-1]
                    stripped = last_line.rstrip("\n\r")
                    indent = len(stripped) - len(stripped.lstrip())

                    # Case 1: last line is bare `)` (possibly indented) —
                    # insert a new line before it, properly indented.
                    if stripped.lstrip() == ")":
                        param_indent = " " * (indent + 4) if indent == 0 else stripped[: indent]
                        new_line = f'{param_indent}summary="{summary}",\n'
                        dec_buf.insert(len(dec_buf) - 1, new_line)
                        changed += 1
                    else:
                        # Case 2: last line ends with `)` — insert before it.
                        rpos = stripped.rfind(")")
                        if rpos >= 0:
                            new_last = stripped[:rpos] + f', summary="{summary}"' + stripped[rpos:] + "\n"
                            dec_buf[-1] = new_last
                            changed += 1

            new_lines.extend(dec_buf)
            i = j
        else:
            new_lines.append(line)
            i += 1

    if changed:
        new_content = "".join(new_lines)
        if not dry_run:
            # Always write UTF-8 without BOM — normalises existing BOM files
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write(new_content)
        print(f"  {path}: +{changed} summaries")

    return changed


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("files", nargs="*", help="Files to process (default: all endpoints)")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    files = args.files or [
        os.path.join(ENDPOINTS_DIR, f)
        for f in sorted(os.listdir(ENDPOINTS_DIR))
        if f.endswith(".py")
    ]

    total = 0
    for path in files:
        total += process_file(path, dry_run=args.dry_run)

    print(f"\nTotal summaries added: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
