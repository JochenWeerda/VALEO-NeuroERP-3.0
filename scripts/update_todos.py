import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple

REPO_ROOT = Path(__file__).resolve().parent.parent

try:
    from query_documentation import DocumentationRetriever
except ImportError:  # pragma: no cover
    DocumentationRetriever = None  # type: ignore

def ensure_utf8(text: str) -> str:
    """Stellt sicher, dass ein Text UTF-8 kodiert ist."""
    if isinstance(text, bytes):
        return text.decode('utf-8', errors='replace')
    return text

def analyze_todo_priority(content: str) -> str:
    """Bestimmt Priorität Hoch | Normal | Niedrig."""
    high_priority_indicators = [
        "dringend", "kritisch", "wichtig", "sofort",
        "höchste priorität", "hohe priorität",
        "sicherheitsrelevant", "bug", "fehler",
        "blockiert", "blocker", "abhängigkeit",
    ]
    low_priority_indicators = [
        "niedrig", "low priority", "optional", "nice to have",
        "später", "kann warten", "kosmetisch", "cosmetic",
        "verfeinerung", "hint",
    ]
    medium_priority_indicators = [
        "sollte", "wünschenswert", "verbesserung",
        "optimierung", "enhancement", "mittlere priorität",
    ]
    content_lower = content.lower()
    line_blob = content_lower.split("\n")[0] if content else ""

    if any(p in line_blob for p in ["todo(p3)", "todo(low)", "[low]", "priorität: niedrig"]):
        return "Niedrig"
    if any(f"priorität: {p}" in content_lower for p in ["hoch", "high"]):
        return "Hoch"
    if any(f"priorität: {p}" in content_lower for p in ["niedrig", "low"]):
        return "Niedrig"
    if any(f"priorität: {p}" in content_lower for p in ["mittel", "medium"]):
        return "Normal"
    if any(indicator in content_lower for indicator in high_priority_indicators):
        return "Hoch"
    if any(indicator in content_lower for indicator in low_priority_indicators):
        return "Niedrig"
    if any(indicator in content_lower for indicator in medium_priority_indicators):
        return "Normal"
    return "Normal"

def normalize_path(path: str) -> str:
    """Normalisiert einen Dateipfad für den Vergleich."""
    # Entferne ./ und .\ am Anfang
    path = path.lstrip("./\\")
    # Ersetze Backslashes durch Forward Slashes
    path = path.replace("\\", "/")
    # Entferne #-Abschnitte
    path = path.split("#")[0]
    return path.lower().strip()

def is_duplicate_todo(todo: Dict[str, Any], todos: List[Dict[str, Any]]) -> bool:
    """Prüft, ob ein TODO bereits in der Liste existiert."""
    # Normalisiere den Text für den Vergleich
    todo_text = todo["todo_line"].lower().strip()
    todo_source = normalize_path(todo["source"])

    # Entferne häufige Präfixe und Markierungen
    for prefix in ["todo:", "todo", "fixme:", "fixme", "xxx:", "xxx", "- [ ]", "-", "**", "#"]:
        todo_text = todo_text.replace(prefix, "").strip()

    for existing in todos:
        existing_text = existing["todo_line"].lower().strip()
        existing_source = normalize_path(existing["source"])

        # Entferne die gleichen Präfixe
        for prefix in ["todo:", "todo", "fixme:", "fixme", "xxx:", "xxx", "- [ ]", "-", "**", "#"]:
            existing_text = existing_text.replace(prefix, "").strip()

        # Prüfe auf Textähnlichkeit
        if todo_text == existing_text:
            # Wenn die Quelle die gleiche ist oder eine die andere enthält
            if (todo_source == existing_source or
                todo_source in existing_source or
                existing_source in todo_source):
                return True

    return False

def extract_todo_context(lines: List[str], todo_index: int, window: int = 5) -> Dict[str, str]:
    """Extrahiert den Kontext eines TODOs mit verbesserter Analyse."""
    start = max(0, todo_index - window)
    end = min(len(lines), todo_index + window + 1)

    # Extrahiere Kontext
    context_before = "\n".join(lines[start:todo_index]).strip()
    todo_line = lines[todo_index].strip()
    context_after = "\n".join(lines[todo_index + 1:end]).strip()

    # Analysiere Titel
    title = todo_line
    for prefix in ["TODO:", "ToDo:", "FIXME:", "XXX:", "- [ ]", "-", "**", "#"]:
        if title.startswith(prefix):
            title = title[len(prefix):].strip()

    # Wenn der Titel leer ist oder nur aus dem Marker besteht,
    # versuche einen besseren Titel aus dem Kontext zu extrahieren
    if not title or title.lower() in ["todo", "fixme", "xxx"]:
        # Suche im nachfolgenden Kontext nach einem aussagekräftigen Titel
        next_lines = [l.strip() for l in lines[todo_index + 1:end]]
        for line in next_lines:
            if line and not line.startswith(("#", "//", "/*", "*", "*/", "'''", '"""', "-", "**")):
                title = line
                break

    # Entferne Markdown-Formatierung aus dem Titel
    title = title.strip("*#- ")

    # Stelle sicher, dass alle Strings UTF-8 kodiert sind
    return {
        "title": ensure_utf8(title),
        "context_before": ensure_utf8(context_before),
        "todo_line": ensure_utf8(todo_line),
        "context_after": ensure_utf8(context_after),
        "full_context": ensure_utf8(f"{context_before}\n{todo_line}\n{context_after}".strip())
    }


def _doc_path_for_exclude(doc: Dict[str, Any]) -> str:
    raw = ensure_utf8(doc.get("file_path", doc.get("source", "")))
    return raw.split("#")[0].strip()


def get_todos_from_docs(retriever: Any, *, skip_semantic: bool = False) -> List[Dict[str, Any]]:
    """Extrahiert TODOs aus der Dokumentation mit verbesserter Kontextanalyse."""
    todos = []

    # Direkte Textsuche nach TODO-Markierungen
    search_terms = [
        "TODO", "ToDo", "To-Do", "FIXME", "XXX",
        "Implementierung ausstehend", "Noch zu implementieren",
        "Muss implementiert werden", "Benötigt Implementierung",
        "Erweiterung geplant", "Zukünftige Erweiterung",
        "Implementiere", "Erweitere", "Verbessere"
    ]

    # Suche nach expliziten TODOs
    for term in search_terms:
        results = retriever.text_search(term, limit=200)
        for doc in results:
            dp = _doc_path_for_exclude(doc)
            if dp and dp != "Unbekannt" and is_excluded_todo_source_path(dp):
                continue
            content = ensure_utf8(doc.get("content", ""))
            sections = doc.get("sections", [])

            # Suche in Hauptinhalt
            if content:
                lines = content.split("\n")
                for i, line in enumerate(lines):
                    if term.lower() in line.lower():
                        if should_skip_todo_marked_line(line):
                            continue
                        # Extrahiere TODO-Kontext
                        todo_context = extract_todo_context(lines, i)

                        # Erstelle ein eindeutiges TODO-Item
                        todo_item = {
                            "type": "explicit",
                            "title": todo_context["title"],
                            "content": todo_context["full_context"],
                            "context_before": todo_context["context_before"],
                            "todo_line": todo_context["todo_line"],
                            "context_after": todo_context["context_after"],
                            "source": ensure_utf8(doc.get("file_path", doc.get("source", "Unbekannt"))),
                            "status": "Offen",
                            "priority": analyze_todo_priority(todo_context["full_context"]),
                            "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        }

                        # Prüfe auf Duplikate mit verbesserter Erkennung
                        if not is_duplicate_todo(todo_item, todos):
                            todos.append(todo_item)

            # Suche in Abschnitten mit gleichem Verfahren
            for section in sections:
                section_content = ensure_utf8(section.get("content", ""))
                if section_content:
                    lines = section_content.split("\n")
                    for i, line in enumerate(lines):
                        if term.lower() in line.lower():
                            if should_skip_todo_marked_line(line):
                                continue
                            todo_context = extract_todo_context(lines, i)

                            todo_item = {
                                "type": "explicit",
                                "title": todo_context["title"],
                                "content": todo_context["full_context"],
                                "context_before": todo_context["context_before"],
                                "todo_line": todo_context["todo_line"],
                                "context_after": todo_context["context_after"],
                                "source": ensure_utf8(f"{doc.get('file_path', doc.get('source', 'Unbekannt'))}#{section.get('title', '')}"),
                                "status": "Offen",
                                "priority": analyze_todo_priority(todo_context["full_context"]),
                                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }

                            # Prüfe auf Duplikate mit verbesserter Erkennung
                            if not is_duplicate_todo(todo_item, todos):
                                todos.append(todo_item)

    if not skip_semantic:
        # Semantische Suche nach impliziten TODOs
        semantic_queries = [
            "Aufgaben die noch implementiert werden müssen",
            "Geplante Erweiterungen und Verbesserungen",
            "Ausstehende Entwicklungsarbeiten",
            "Fehlende Funktionalitäten",
            "Bekannte Probleme die behoben werden müssen"
        ]

        for query in semantic_queries:
            results = retriever.semantic_search(query)
            for doc in results:
                dp = _doc_path_for_exclude(doc)
                if dp and dp != "Unbekannt" and is_excluded_todo_source_path(dp):
                    continue
                content = ensure_utf8(doc.get("content", ""))

                # Prüfe auf relevante Schlüsselwörter
                keywords = [
                    "implementier", "erweitern", "verbessern",
                    "hinzufügen", "entwickeln", "beheben",
                    "optimieren", "anpassen", "integrieren"
                ]

                if content and any(keyword in content.lower() for keyword in keywords):
                    lines = content.split("\n")
                    # Suche nach Zeilen mit Keywords
                    for i, line in enumerate(lines):
                        if any(keyword in line.lower() for keyword in keywords):
                            if should_skip_todo_marked_line(line):
                                continue
                            todo_context = extract_todo_context(lines, i)

                            todo_item = {
                                "type": "implicit",
                                "title": todo_context["title"],
                                "content": todo_context["full_context"],
                                "context_before": todo_context["context_before"],
                                "todo_line": todo_context["todo_line"],
                                "context_after": todo_context["context_after"],
                                "source": ensure_utf8(doc.get("file_path", doc.get("source", "Unbekannt"))),
                                "status": "Offen",
                                "priority": analyze_todo_priority(todo_context["full_context"]),
                                "updated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }

                            # Prüfe auf Duplikate mit verbesserter Erkennung
                            if not is_duplicate_todo(todo_item, todos):
                                todos.append(todo_item)

    return todos

# Verzeichnisse / Endungen fuer Voll-Repo-Scan (ohne Mongo/RAG)
_SCAN_EXCLUDE_DIR_NAMES = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "memory-bank",
    ".cursor",
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    ".venv",
    "venv",
    "env",
    "dist",
    "build",
    ".next",
    "coverage",
    "htmlcov",
    ".turbo",
    "target",
    "playwright-report",
    "storybook-static",
}
_SCAN_SUFFIXES = (
    ".py",
    ".ts",
    ".tsx",
    ".js",
    ".jsx",
    ".mjs",
    ".cjs",
    ".vue",
    ".svelte",
    ".md",
    ".rs",
    ".go",
    ".java",
    ".cs",
    ".yaml",
    ".yml",
    ".sql",
    ".css",
    ".scss",
    ".html",
)
_SCAN_MAX_FILE_BYTES = 2 * 1024 * 1024

# Eigene Ausgaben nicht einlesen (stecken tausende "TODO"-Treffer in MD/JSON)
_SCAN_SKIP_RELATIVE_PATHS = frozenset(
    {
        "docs/todo-repo-scan.md",
        "docs/todo-report.json",
        "docs/TODO-backlog.md",
        "docs/TODO-next-slices.md",
    }
)


def is_excluded_todo_source_path(rel_posix: str) -> bool:
    """Pfade rein historischer Gap-/Abschluss-Doku — keine echten Code-TODOs."""
    r = rel_posix.replace("\\", "/").lstrip("./")
    lower = r.lower()
    if lower.startswith("docs/archive/"):
        return True
    base = Path(r).name.lower()
    if lower.startswith("docs/") and base.startswith("phase-") and "completion-report" in base:
        return True
    if base == "gap-closure-summary.md":
        return True
    if base in ("p0-gaps-complete.md", "gap-analysis-complete.md") and lower.startswith("swarm/"):
        return True
    return False


def is_gap_matrix_technically_closed_row(line: str) -> bool:
    """Gap-Matrix (| Gap | … | Technischer Ist-Stand | …): Zeile mit Ist-Stand geschlossen."""
    s = line.strip()
    if not s.startswith("|") or s.count("|") < 4:
        return False
    parts = [p.strip() for p in s.split("|")]
    if len(parts) < 5:
        return False
    gap_cell = parts[1]
    if not gap_cell.isdigit():
        return False
    return parts[3].lower() == "geschlossen"


def is_completed_todo_narration_line(line: str) -> bool:
    """Meta-Zeilen (Fortschritts-/Abschlussberichte), keine offenen Aufgaben."""
    low = line.lower()
    if "fixme" in low:
        return False
    if "todo" not in low:
        return False
    if is_gap_matrix_technically_closed_row(line):
        return True
    if "abgeschlossen" in low and "todo" in low:
        return True
    if "✅" in line and "abgeschlossen" in low and "todo" in low:
        return True
    if re.search(r"fortschritt:\s*.*todos?\s*abgeschlossen", low):
        return True
    if re.search(r"\d+\s*/\s*\d+\s*todos?", low) and "abgeschlossen" in low:
        return True
    if "resolved" in low and "todo" in low and (" all " in low or " alle " in low or "290+" in line):
        return True
    return False


def should_skip_todo_marked_line(line: str) -> bool:
    """True wenn die Zeile nur geschlossene Gaps / erledigte-TODO-Metrik beschreibt."""
    return is_completed_todo_narration_line(line)


def _load_openai_key(repo_root: Path) -> Optional[str]:
    if os.environ.get("OPENAI_API_KEY"):
        return str(os.environ["OPENAI_API_KEY"]).strip() or None
    keyfile = repo_root / "api_keys.local.json"
    if not keyfile.is_file():
        return None
    try:
        with open(keyfile, "r", encoding="utf-8") as f:
            data = json.load(f)
        keys = data.get("API_KEYS") or {}
        v = keys.get("OPENAI_API_KEY")
        return str(v).strip() if v else None
    except (OSError, json.JSONDecodeError, TypeError, KeyError):
        return None


def scan_repository_for_markers(repo_root: Path) -> List[Dict[str, Any]]:
    """Lint-artige Suche nach TODO/FIXME im Quell- und Doku-Baum (ohne MongoDB)."""
    todos: List[Dict[str, Any]] = []
    markers = ("TODO", "FIXME")
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    seen_files = 0

    for dirpath, dirnames, filenames in os.walk(repo_root):
        dirnames[:] = [d for d in dirnames if d not in _SCAN_EXCLUDE_DIR_NAMES]
        rel_dir = Path(dirpath).relative_to(repo_root)
        if any(p in _SCAN_EXCLUDE_DIR_NAMES for p in rel_dir.parts):
            continue
        for name in filenames:
            path = Path(dirpath) / name
            if path.suffix.lower() not in _SCAN_SUFFIXES:
                continue
            rel_skip = path.relative_to(repo_root).as_posix()
            if rel_skip in _SCAN_SKIP_RELATIVE_PATHS:
                continue
            if is_excluded_todo_source_path(rel_skip):
                continue
            try:
                st = path.stat()
            except OSError:
                continue
            if st.st_size > _SCAN_MAX_FILE_BYTES:
                continue
            try:
                raw = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            seen_files += 1
            lines = raw.splitlines()
            rel = path.relative_to(repo_root).as_posix()
            for i, line in enumerate(lines):
                if not any(m in line for m in markers):
                    continue
                if should_skip_todo_marked_line(line):
                    continue
                ctx = extract_todo_context(lines, i, window=3)
                todo_item: Dict[str, Any] = {
                    "type": "explicit",
                    "title": (ctx["title"][:200] + "…") if len(ctx["title"]) > 200 else ctx["title"],
                    "content": ctx["full_context"],
                    "context_before": ctx["context_before"],
                    "todo_line": ctx["todo_line"],
                    "context_after": ctx["context_after"],
                    "source": rel + f":{i + 1}",
                    "status": "Offen",
                    "priority": analyze_todo_priority(ctx["full_context"]),
                    "updated_at": ts,
                }
                if not is_duplicate_todo(todo_item, todos):
                    todos.append(todo_item)

    print(f"Repository-Scan: {seen_files} Dateien gelesen, {len(todos)} TODO/FIXME-Zeilen.")
    return todos


def merge_todo_lists(primary: List[Dict[str, Any]], secondary: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """primary behält Reihenfolge; secondary nur wenn kein Duplikat."""
    out = list(primary)
    for t in secondary:
        if not is_duplicate_todo(t, out):
            out.append(t)
    return out


def _priority_bucket(p: Optional[str]) -> str:
    if p in ("Hoch", "Normal", "Niedrig"):
        return p
    return "Normal"


def _priority_heading(priority: str) -> str:
    if priority == "Hoch":
        return "Hohe Priorität"
    if priority == "Normal":
        return "Normale Priorität"
    return "Niedrige Priorität"


def render_todo_markdown(
    todos: List[Dict[str, Any]],
    *,
    title: str,
    subtitle: str,
) -> str:
    """Gruppiert explicit/implicit × Hoch/Normal/Niedrig."""
    todo_groups: Dict[str, Dict[str, List[Dict[str, Any]]]] = {
        "explicit": {"Hoch": [], "Normal": [], "Niedrig": []},
        "implicit": {"Hoch": [], "Normal": [], "Niedrig": []},
    }
    for todo in todos:
        typ = todo.get("type") or "explicit"
        if typ not in todo_groups:
            typ = "explicit"
        pr = _priority_bucket(todo.get("priority"))
        todo_groups[typ][pr].append(todo)

    content = f"# {title}\n\n{subtitle}\n\n"
    content += "## Explizit markierte TODOs\n\n"
    for priority in ["Hoch", "Normal", "Niedrig"]:
        bucket = todo_groups["explicit"][priority]
        if not bucket:
            continue
        content += f"### {_priority_heading(priority)}\n\n"
        for todo in bucket:
            content += f"#### {todo['title']}\n\n"
            content += f"**Status:** {todo['status']}\n"
            content += f"**Quelle:** {todo['source']}\n"
            content += f"**Aktualisiert:** {todo['updated_at']}\n\n"
            if todo.get("context_before"):
                content += "**Kontext davor:**\n```\n" + todo["context_before"] + "\n```\n\n"
            content += "**TODO:**\n```\n" + todo["todo_line"] + "\n```\n\n"
            if todo.get("context_after"):
                content += "**Kontext danach:**\n```\n" + todo["context_after"] + "\n```\n\n"

    content += "## Implizit erkannte TODOs\n\n"
    for priority in ["Hoch", "Normal", "Niedrig"]:
        bucket = todo_groups["implicit"][priority]
        if not bucket:
            continue
        content += f"### {_priority_heading(priority)}\n\n"
        for todo in bucket:
            content += f"#### {todo['title']}\n\n"
            content += f"**Status:** {todo['status']}\n"
            content += f"**Quelle:** {todo['source']}\n"
            content += f"**Aktualisiert:** {todo['updated_at']}\n\n"
            if todo.get("context_before"):
                content += "**Kontext davor:**\n```\n" + todo["context_before"] + "\n```\n\n"
            content += "**Relevanter Abschnitt:**\n```\n" + todo["todo_line"] + "\n```\n\n"
            if todo.get("context_after"):
                content += "**Kontext danach:**\n```\n" + todo["context_after"] + "\n```\n\n"

    return content


def write_text_file(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def source_path_for_match(source: str) -> str:
    """Entfernt :Zeile am Ende für Pfad-Vergleiche."""
    s = source.replace("\\", "/").lstrip("./")
    if ":" in s:
        tail = s.rsplit(":", 1)[-1]
        if tail.isdigit():
            return s.rsplit(":", 1)[0]
    return s


def filter_todo_items(todos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Postfilter: Abschluss-Doku + Meta-TODO-Zeilen (geschlossene Gaps / erledigte Kennzahlen)."""
    out: List[Dict[str, Any]] = []
    for t in todos:
        raw_src = str(t.get("source", "") or "")
        path_only = source_path_for_match(raw_src.split("#")[0])
        if path_only and path_only != "Unbekannt" and is_excluded_todo_source_path(path_only):
            continue
        if should_skip_todo_marked_line(t.get("todo_line", "")):
            continue
        out.append(t)
    return out


def parse_source_line(source: str) -> Tuple[str, Optional[int]]:
    """`pfad:123` → (pfad, 123)."""
    s = source.replace("\\", "/")
    if ":" in s:
        prefix, tail = s.rsplit(":", 1)
        if tail.isdigit():
            return prefix.lstrip("./"), int(tail)
    return s.lstrip("./"), None


def package_from_path(rel_path: str) -> str:
    p = rel_path.replace("\\", "/").lstrip("./")
    if p.startswith("packages/"):
        parts = p.split("/")
        if len(parts) >= 3:
            return f"packages/{parts[1]}"
        if len(parts) >= 2:
            return f"packages/{parts[1]}"
    if p.startswith("app/"):
        return "app"
    if p.startswith("services/"):
        parts = p.split("/")
        return parts[1] if len(parts) > 1 else "services"
    return "other"


def marker_from_line(line: str) -> str:
    low = line.lower()
    if "fixme" in low:
        return "FIXME"
    return "TODO"


def build_json_payload(todos: List[Dict[str, Any]]) -> Dict[str, Any]:
    by_pri: Dict[str, int] = {"Hoch": 0, "Normal": 0, "Niedrig": 0}
    by_m: Dict[str, int] = {"TODO": 0, "FIXME": 0}
    items: List[Dict[str, Any]] = []
    for t in todos:
        pr = _priority_bucket(t.get("priority"))
        by_pri[pr] = by_pri.get(pr, 0) + 1
        tl = t.get("todo_line", "")
        m = marker_from_line(tl)
        by_m[m] = by_m.get(m, 0) + 1
        path, line_no = parse_source_line(t.get("source", ""))
        items.append({
            "path": path,
            "line": line_no,
            "marker": m,
            "package": package_from_path(path),
            "title": (t.get("title") or "")[:500],
            "priority": pr,
            "type": t.get("type"),
            "source": t.get("source"),
            "todo_line": (tl or "")[:2000],
        })
    return {
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "counts": {"total": len(todos), "by_priority": by_pri, "by_marker": by_m},
        "items": items,
        "next_slices": next_slices_as_json(todos),
    }


def _slice_sort_metrics(items: List[Dict[str, Any]]) -> Tuple[int, int, int]:
    """Niedriger Rang = dringender Slice; dann mehr Hoch-Punkte; dann mehr Volumen."""
    if not items:
        return 99, 0, 0
    ranks = [_prio_rank(_priority_bucket(t.get("priority"))) for t in items]
    best = min(ranks)
    hoch_n = sum(1 for t in items if _priority_bucket(t.get("priority")) == "Hoch")
    return best, -hoch_n, -len(items)


def _collect_focus_todos(merged: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for t in merged:
        src = t.get("source", "")
        sp = source_path_for_match(str(src)).replace("\\", "/").lstrip("./")
        if not any(sp.startswith(pref) for pref in _BACKLOG_PREFIXES):
            continue
        rows.append(t)
    return rows


def next_slice_bucket(path: str) -> str:
    """Grobe Slice-Beschriftung für Umsetzungsreihenfolge (Verzeichnis-Cluster)."""
    p = path.replace("\\", "/").lstrip("./")
    if p.startswith("packages/frontend-web/"):
        rest = p[len("packages/frontend-web/") :]
        parts = rest.split("/")
        if len(parts) >= 2 and parts[0] == "src":
            return f"frontend-web/src/{parts[1]}"
        if parts:
            return f"frontend-web/{parts[0]}"
        return "frontend-web"
    if p.startswith("app/"):
        parts = p.split("/")
        if len(parts) >= 2:
            return f"app/{parts[1]}"
        return "app"
    if p.startswith("services/"):
        parts = p.split("/")
        if len(parts) >= 2:
            return f"services/{parts[1]}"
        return "services"
    if p.startswith("packages/erp-domain/"):
        rest = p[len("packages/erp-domain/") :].split("/")
        if rest and rest[0]:
            return f"erp-domain/{rest[0]}"
        return "erp-domain"
    return "other"


def next_slices_as_json(
    merged: List[Dict[str, Any]],
    *,
    max_slices: int = 18,
    items_per_slice: int = 10,
) -> List[Dict[str, Any]]:
    """Maschinenlesbare Prioritätsliste je Slice."""
    focus = _collect_focus_todos(merged)
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for t in focus:
        path, _ = parse_source_line(str(t.get("source", "")))
        if not path:
            continue
        sk = next_slice_bucket(path)
        buckets.setdefault(sk, []).append(t)

    keys = sorted(buckets.keys(), key=lambda k: (_slice_sort_metrics(buckets[k]), k))[:max_slices]
    out: List[Dict[str, Any]] = []
    for rank, sk in enumerate(keys, start=1):
        items = buckets[sk]
        items_sorted = sorted(
            items,
            key=lambda x: (_prio_rank(_priority_bucket(x.get("priority"))), source_path_for_match(x.get("source", ""))),
        )[:items_per_slice]
        by_pri: Dict[str, int] = {"Hoch": 0, "Normal": 0, "Niedrig": 0}
        for it in items:
            pr = _priority_bucket(it.get("priority"))
            if pr in by_pri:
                by_pri[pr] += 1
        slice_items: List[Dict[str, Any]] = []
        for t in items_sorted:
            path, line_no = parse_source_line(str(t.get("source", "")))
            tl = t.get("todo_line", "")
            slice_items.append(
                {
                    "path": path,
                    "line": line_no,
                    "priority": _priority_bucket(t.get("priority")),
                    "marker": marker_from_line(tl),
                    "title": (t.get("title") or "")[:300],
                }
            )
        out.append(
            {
                "rank": rank,
                "slice": sk,
                "total_in_slice": len(items),
                "by_priority": by_pri,
                "sort_key": {"best_priority_rank": _slice_sort_metrics(items)[0]},
                "sample_items": slice_items,
                "truncated": len(items) > items_per_slice,
            }
        )
    return out


def render_next_slices_markdown(
    merged: List[Dict[str, Any]],
    *,
    max_slices: int = 18,
    items_per_slice: int = 10,
) -> str:
    """Priorisierte Slice-Übersicht als nächste Umsetzungsblöcke."""
    focus = _collect_focus_todos(merged)
    buckets: Dict[str, List[Dict[str, Any]]] = {}
    for t in focus:
        path, _ = parse_source_line(str(t.get("source", "")))
        if not path:
            continue
        sk = next_slice_bucket(path)
        buckets.setdefault(sk, []).append(t)

    keys = sorted(buckets.keys(), key=lambda k: (_slice_sort_metrics(buckets[k]), k))[:max_slices]

    lines = [
        "# Nächste Arbeitsslices (priorisiert)",
        "",
        f"> Erzeugt am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} aus dem Merge (Fokus-Pfade wie im Kurz-Backlog).",
        "> **Reihenfolge der Slices:** zuerst Bereiche mit der höchsten Dringlichkeit (min. Priorität), dann mehr „Hoch“, dann mehr Einträge.",
        "> **Innerhalb eines Slices:** Hoch → Normal → Niedrig, dann Dateipfad.",
        "> Vollständige Rohdaten: `todo-report.json` → `next_slices`; Zeilenlisten: `todo-repo-scan.md`.",
        "",
    ]
    if not keys:
        lines.append("*Keine TODOs in den Fokus-Pfaden (`packages/frontend-web/`, `app/`, `services/`, `packages/erp-domain/`).*")
        lines.append("")
        return "\n".join(lines)

    for rank, sk in enumerate(keys, start=1):
        items = buckets[sk]
        items_sorted = sorted(
            items,
            key=lambda x: (_prio_rank(_priority_bucket(x.get("priority"))), source_path_for_match(x.get("source", ""))),
        )
        shown = items_sorted[:items_per_slice]
        by_pri: Dict[str, int] = {"Hoch": 0, "Normal": 0, "Niedrig": 0}
        for it in items:
            pr = _priority_bucket(it.get("priority"))
            if pr in by_pri:
                by_pri[pr] += 1
        bm, hneg, _ = _slice_sort_metrics(items)
        pr_label = {0: "Hoch zuerst", 1: "Normal dominiert", 2: "überwiegend Niedrig"}.get(bm, "")
        lines.append(
            f"## {rank}. `{sk}` — {len(items)} TODO(s) "
            f"({by_pri['Hoch']} Hoch · {by_pri['Normal']} Normal · {by_pri['Niedrig']} Niedrig)"
            + (f" _({pr_label})_" if pr_label else "")
        )
        lines.append("")
        for t in shown:
            path, line_no = parse_source_line(str(t.get("source", "")))
            line_part = f"L{line_no}" if line_no is not None else ""
            pr = _priority_bucket(t.get("priority"))
            title = (t.get("title") or "").replace("\n", " ")[:100]
            mk = marker_from_line(t.get("todo_line", ""))
            lines.append(f"- **[{pr}] [{mk}]** `{path}`{(':' + line_part) if line_part else ''} — {title}")
        if len(items) > items_per_slice:
            lines.append(f"- *… {len(items) - items_per_slice} weitere in diesem Slice*")
        lines.append("")
    return "\n".join(lines)


_BACKLOG_PREFIXES = (
    "packages/frontend-web/",
    "app/",
    "services/",
    "packages/erp-domain/",
)


def _prio_rank(p: str) -> int:
    return {"Hoch": 0, "Normal": 1, "Niedrig": 2}.get(p, 1)


def render_backlog_markdown(merged: List[Dict[str, Any]], *, max_items: int = 40) -> str:
    """Kuratierte Kurzliste für Produkt-Fokus (Frontend, Backend app, Services, ERP-Domain)."""
    rows: List[Dict[str, Any]] = []
    for t in merged:
        src = t.get("source", "")
        sp = source_path_for_match(src).replace("\\", "/").lstrip("./")
        if not any(sp.startswith(pref) for pref in _BACKLOG_PREFIXES):
            continue
        rows.append(t)
    rows.sort(
        key=lambda x: (
            _prio_rank(_priority_bucket(x.get("priority"))),
            source_path_for_match(x.get("source", "")),
        )
    )
    rows = rows[:max_items]

    lines = [
        "# Kuratiertes TODO-Backlog (Fokus)",
        "",
        f"> Automatisch erzeugt am {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}.",
        f"> Enthält bis zu {max_items} Einträge aus `packages/frontend-web/`, `app/`, `services/`, `packages/erp-domain/`.",
        "> Vollständige Rohliste: `todo-repo-scan.md`, `memory-bank/todo.md`, Maschinenlesbar: `todo-report.json` (inkl. `next_slices`).",
        "",
    ]
    if not rows:
        lines.append("*Keine passenden Einträge in den gewählten Pfaden — ggf. Roh-Report prüfen.*")
        lines.append("")
        return "\n".join(lines)

    current_pr: Optional[str] = None
    for t in rows:
        pr = _priority_bucket(t.get("priority"))
        if pr != current_pr:
            current_pr = pr
            lines.append(f"## {_priority_heading(pr)}")
            lines.append("")
        path, line_no = parse_source_line(t.get("source", ""))
        pkg = package_from_path(path)
        line_part = f"L{line_no}" if line_no is not None else ""
        title = (t.get("title") or "").replace("\n", " ")[:120]
        lines.append(f"- **[{pkg}]** `{path}`{(':' + line_part) if line_part else ''} — {title}")
    lines.append("")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="TODO-Liste aus Doku-RAG und/oder Repo-Scan erzeugen.")
    parser.add_argument(
        "--repo-only",
        action="store_true",
        help="Nur Repository-Scan (kein MongoDB/OpenAI).",
    )
    parser.add_argument(
        "--no-repo",
        action="store_true",
        help="Kein Voll-Repo-Scan (nur RAG, benötigt Mongo + API-Key).",
    )
    parser.add_argument(
        "--skip-semantic",
        action="store_true",
        help="Keine semantische Doku-Suche (nur Textsuche in Mongo; spart OpenAI-Quota).",
    )
    parser.add_argument(
        "--output-full-md",
        type=str,
        default="",
        help="Voller Merge als Markdown (Default: memory-bank/todo.md).",
    )
    parser.add_argument(
        "--output-repo-md",
        type=str,
        default="",
        help="Nur Repository-Scan als Markdown (Default: docs/todo-repo-scan.md). Leer = aus.",
    )
    parser.add_argument(
        "--output-json",
        type=str,
        default="",
        help="JSON-Report (Default: docs/todo-report.json). Leer = aus.",
    )
    parser.add_argument(
        "--output-backlog",
        type=str,
        default="",
        help="Kuratiertes Backlog (Default: docs/TODO-backlog.md). Leer = aus.",
    )
    parser.add_argument(
        "--no-json",
        action="store_true",
        help="Keine todo-report.json schreiben.",
    )
    parser.add_argument(
        "--no-backlog",
        action="store_true",
        help="Kein docs/TODO-backlog.md.",
    )
    parser.add_argument(
        "--output-slices",
        type=str,
        default="",
        help="Priorisierte Arbeitsslices (Default: docs/TODO-next-slices.md). Leer = aus.",
    )
    parser.add_argument(
        "--no-slices",
        action="store_true",
        help="Keine docs/TODO-next-slices.md.",
    )
    args = parser.parse_args()
    repo_root = REPO_ROOT

    out_full = Path(args.output_full_md or (repo_root / "memory-bank" / "todo.md"))
    out_repo = Path(args.output_repo_md or (repo_root / "docs" / "todo-repo-scan.md"))
    out_json = Path(args.output_json or (repo_root / "docs" / "todo-report.json"))
    out_backlog = Path(args.output_backlog or (repo_root / "docs" / "TODO-backlog.md"))
    out_slices = Path(args.output_slices or (repo_root / "docs" / "TODO-next-slices.md"))

    print("Starte TODO-Aktualisierung...")
    todos_docs: List[Dict[str, Any]] = []

    if not args.repo_only:
        key = _load_openai_key(repo_root)
        if key:
            os.environ["OPENAI_API_KEY"] = key
        if DocumentationRetriever is None:
            print("Hinweis: query_documentation nicht importiert – RAG übersprungen.")
        elif not key:
            print("Hinweis: kein OPENAI_API_KEY / api_keys.local.json – RAG (Embeddings) übersprungen.")
        else:
            try:
                retriever = DocumentationRetriever()
                print("Extrahiere TODOs aus der Dokumentation (MongoDB/RAG)...")
                if args.skip_semantic:
                    print("(Semantische Suche deaktiviert.)")
                todos_docs = get_todos_from_docs(retriever, skip_semantic=args.skip_semantic)
                print(f"Dokumentation: {len(todos_docs)} Einträge.")
            except Exception as e:  # pragma: no cover
                print(f"Warnung: Dokumenten-RAG fehlgeschlagen ({e}); fahre mit Repo-Scan fort.")

    todos_repo: List[Dict[str, Any]] = []
    if not args.no_repo:
        print("Scanne Repository nach TODO/FIXME...")
        todos_repo = scan_repository_for_markers(repo_root)

    todos_docs = filter_todo_items(todos_docs)
    todos_repo = filter_todo_items(todos_repo)
    merged = merge_todo_lists(todos_docs, todos_repo)
    print(f"Gesamt (nach Deduplizierung): {len(merged)} TODOs")

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_md = render_todo_markdown(
        merged,
        title="VALEO-NeuroERP Entwicklungs-TODOs",
        subtitle=f"Automatisch aktualisiert am {ts} (Dokumenten-RAG + Repository-Scan).",
    )
    write_text_file(out_full, full_md)
    print(f"Vollständige TODO-Liste: {out_full}")

    repo_md = render_todo_markdown(
        todos_repo,
        title="Repository-Scan: TODO / FIXME",
        subtitle=f"Automatisch aktualisiert am {ts} (nur Quellcode/Doku-Dateien, ohne `memory-bank/`).",
    )
    write_text_file(out_repo, repo_md)
    print(f"Repo-Scan Markdown: {out_repo}")

    if not args.no_json:
        payload = build_json_payload(merged)
        write_text_file(out_json, json.dumps(payload, ensure_ascii=False, indent=2))
        print(f"JSON-Report: {out_json}")

    if not args.no_backlog:
        bl = render_backlog_markdown(merged, max_items=40)
        write_text_file(out_backlog, bl)
        print(f"Kuratiertes Backlog: {out_backlog}")

    if not args.no_slices:
        sl_md = render_next_slices_markdown(merged)
        write_text_file(out_slices, sl_md)
        print(f"Slice-Priorisierung: {out_slices}")


if __name__ == "__main__":
    main()
