#!/usr/bin/env python3
"""
VALEO NeuroERP — Security Agent: Triage & Unified Report
=========================================================
Liest Scanner-Ergebnisse (Gitleaks, Semgrep, Bandit, Trivy) ein,
normalisiert sie in ein einheitliches Format und erzeugt:
  - unified_findings.json  (fuer LLM-Triage)
  - summary.md             (fuer schnelle menschliche Uebersicht)
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


# ── Severity-Mapping ────────────────────────────────────────────────────────
SEVERITY_MAP = {
    # Semgrep
    "ERROR": "HIGH",
    "WARNING": "MEDIUM",
    "INFO": "LOW",
    # Bandit
    "CRITICAL": "CRITICAL",
    "HIGH": "HIGH",
    "MEDIUM": "MEDIUM",
    "LOW": "LOW",
    # Trivy
    "UNKNOWN": "LOW",
}


def normalize_severity(raw: str) -> str:
    return SEVERITY_MAP.get(raw.upper(), raw.upper())


# ── Parser pro Scanner ──────────────────────────────────────────────────────

def parse_gitleaks(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    findings = []
    for item in data:
        findings.append({
            "scanner": "gitleaks",
            "category": "secrets",
            "severity": "CRITICAL",
            "confidence": "HIGH",
            "title": f"Leaked secret: {item.get('RuleID', item.get('ruleID', 'unknown'))}",
            "file": item.get("File", item.get("file", "")),
            "line": item.get("StartLine", item.get("startLine", 0)),
            "description": item.get("Description", item.get("description", "")),
            "match": item.get("Match", item.get("match", ""))[:120],
            "rule_id": item.get("RuleID", item.get("ruleID", "")),
        })
    return findings


def parse_semgrep(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    findings = []
    for item in data.get("results", []):
        extra = item.get("extra", {})
        findings.append({
            "scanner": "semgrep",
            "category": "sast",
            "severity": normalize_severity(extra.get("severity", "INFO")),
            "confidence": extra.get("metadata", {}).get("confidence", "MEDIUM").upper(),
            "title": item.get("check_id", "").split(".")[-1],
            "file": item.get("path", ""),
            "line": item.get("start", {}).get("line", 0),
            "description": extra.get("message", ""),
            "match": extra.get("lines", "")[:200],
            "rule_id": item.get("check_id", ""),
            "cwe": extra.get("metadata", {}).get("cwe", []),
            "owasp": extra.get("metadata", {}).get("owasp", []),
            "fix": extra.get("fix", ""),
        })
    return findings


def parse_bandit(path: Path) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    findings = []
    for item in data.get("results", []):
        findings.append({
            "scanner": "bandit",
            "category": "sast-python",
            "severity": normalize_severity(item.get("issue_severity", "LOW")),
            "confidence": item.get("issue_confidence", "MEDIUM").upper(),
            "title": item.get("issue_text", ""),
            "file": item.get("filename", ""),
            "line": item.get("line_number", 0),
            "description": item.get("issue_text", ""),
            "match": item.get("code", "")[:200],
            "rule_id": item.get("test_id", ""),
            "cwe": item.get("issue_cwe", {}).get("id", ""),
        })
    return findings


def parse_trivy_vuln(path: Path, source: str) -> list[dict]:
    if not path.exists():
        return []
    data = json.loads(path.read_text(encoding="utf-8"))
    findings = []
    for result in data.get("Results", []):
        target = result.get("Target", "")
        for vuln in result.get("Vulnerabilities", []):
            findings.append({
                "scanner": f"trivy-{source}",
                "category": "dependency-vuln",
                "severity": normalize_severity(vuln.get("Severity", "UNKNOWN")),
                "confidence": "HIGH",
                "title": f"{vuln.get('VulnerabilityID', '')}: {vuln.get('PkgName', '')}",
                "file": target,
                "line": 0,
                "description": vuln.get("Title", vuln.get("Description", ""))[:300],
                "match": f"{vuln.get('PkgName', '')} {vuln.get('InstalledVersion', '')}",
                "rule_id": vuln.get("VulnerabilityID", ""),
                "fixed_version": vuln.get("FixedVersion", ""),
                "cvss_score": vuln.get("CVSS", {}).get("nvd", {}).get("V3Score", 0),
            })
        for misconf in result.get("Misconfigurations", []):
            findings.append({
                "scanner": f"trivy-{source}",
                "category": "misconfig",
                "severity": normalize_severity(misconf.get("Severity", "UNKNOWN")),
                "confidence": "HIGH",
                "title": misconf.get("Title", ""),
                "file": target,
                "line": 0,
                "description": misconf.get("Description", "")[:300],
                "match": misconf.get("Message", "")[:200],
                "rule_id": misconf.get("ID", ""),
                "resolution": misconf.get("Resolution", ""),
            })
        for secret in result.get("Secrets", []):
            findings.append({
                "scanner": f"trivy-{source}",
                "category": "secrets",
                "severity": "CRITICAL",
                "confidence": "HIGH",
                "title": f"Secret: {secret.get('RuleID', '')}",
                "file": target,
                "line": secret.get("StartLine", 0),
                "description": secret.get("Title", ""),
                "match": secret.get("Match", "")[:80],
                "rule_id": secret.get("RuleID", ""),
            })
    return findings


# ── Deduplizierung ──────────────────────────────────────────────────────────

def dedup_key(f: dict) -> str:
    return f"{f['file']}:{f['line']}:{f['rule_id']}:{f['severity']}"


def deduplicate(findings: list[dict]) -> list[dict]:
    seen = {}
    for f in findings:
        key = dedup_key(f)
        if key not in seen:
            seen[key] = f
        else:
            # Merge scanner names
            existing = seen[key]
            if f["scanner"] not in existing["scanner"]:
                existing["scanner"] += f" + {f['scanner']}"
    return list(seen.values())


# ── Sortierung (Prioritaet) ────────────────────────────────────────────────

SEVERITY_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
CATEGORY_ORDER = {"secrets": 0, "misconfig": 1, "sast": 2, "sast-python": 3, "dependency-vuln": 4}


def sort_key(f: dict) -> tuple:
    return (
        SEVERITY_ORDER.get(f["severity"], 9),
        CATEGORY_ORDER.get(f["category"], 9),
        f["file"],
        f["line"],
    )


# ── Summary-Generator ──────────────────────────────────────────────────────

def generate_summary(findings: list[dict], report_dir: Path) -> str:
    lines = [
        "# VALEO NeuroERP — Security Scan Summary",
        f"**Datum:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        f"**Gesamt-Findings:** {len(findings)}",
        "",
    ]

    # By severity
    lines.append("## Nach Severity")
    lines.append("")
    lines.append("| Severity | Anzahl | davon durch Ausnahme gedeckt |")
    lines.append("|----------|--------|------------------------------|")
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = sum(1 for f in findings if f["severity"] == sev)
        covered = sum(
            1 for f in findings if f["severity"] == sev and f.get("gate_excluded")
        )
        if count > 0:
            lines.append(f"| {sev} | {count} | {covered} |")
    lines.append("")

    # Begruendete Ausnahmen - bewusst weit oben, damit sie nicht untergehen
    excepted = [f for f in findings if f.get("exception")]
    if excepted:
        lines.append("## Begruendete Ausnahmen")
        lines.append("")
        lines.append(
            "Diese Befunde bleiben bestehen und sind nicht behoben. Sie sind aus "
            "der Gate-Wertung genommen, weil kein Herstellerfix existiert und der "
            "Angriffsweg im Betrieb nachweislich nicht erreichbar ist."
        )
        lines.append("")
        lines.append("| Befund | Severity | Ausnahme | Zu ueberpruefen bis | Status |")
        lines.append("|--------|----------|----------|---------------------|--------|")
        for f in excepted:
            exc = f["exception"]
            status = "ABGELAUFEN" if exc.get("expired") else "gueltig"
            lines.append(
                f"| {f.get('rule_id', '?')} | {f['severity']} | {exc['id']} "
                f"| {exc['review_by']} | {status} |"
            )
        lines.append("")
        for f in excepted:
            exc = f["exception"]
            lines.append(f"- **{f.get('rule_id', '?')}** ({exc['id']}): {exc['reason']}")
        lines.append("")

    # By category
    lines.append("## Nach Kategorie")
    lines.append("")
    lines.append("| Kategorie | Anzahl |")
    lines.append("|-----------|--------|")
    categories = {}
    for f in findings:
        categories[f["category"]] = categories.get(f["category"], 0) + 1
    for cat, count in sorted(categories.items()):
        lines.append(f"| {cat} | {count} |")
    lines.append("")

    # By scanner
    lines.append("## Nach Scanner")
    lines.append("")
    lines.append("| Scanner | Anzahl |")
    lines.append("|---------|--------|")
    scanners = {}
    for f in findings:
        base = f["scanner"].split(" + ")[0]
        scanners[base] = scanners.get(base, 0) + 1
    for scanner, count in sorted(scanners.items()):
        lines.append(f"| {scanner} | {count} |")
    lines.append("")

    # Top 10 Critical/High
    critical_high = [f for f in findings if f["severity"] in ("CRITICAL", "HIGH")]
    if critical_high:
        lines.append("## Top Critical/High Findings")
        lines.append("")
        for i, f in enumerate(critical_high[:15], 1):
            lines.append(f"### {i}. [{f['severity']}] {f['title']}")
            lines.append(f"- **Scanner:** {f['scanner']}")
            lines.append(f"- **Datei:** `{f['file']}:{f['line']}`")
            lines.append(f"- **Kategorie:** {f['category']}")
            if f.get("description"):
                lines.append(f"- **Details:** {f['description'][:200]}")
            if f.get("fix"):
                lines.append(f"- **Fix:** {f['fix'][:200]}")
            if f.get("resolution"):
                lines.append(f"- **Resolution:** {f['resolution'][:200]}")
            if f.get("fixed_version"):
                lines.append(f"- **Fix-Version:** {f['fixed_version']}")
            lines.append("")

    # Next steps
    lines.append("## Naechste Schritte")
    lines.append("")
    lines.append("1. `unified_findings.json` + `llm_triage_prompt.txt` an LLM geben")
    lines.append("2. LLM-Bewertung pruefen: Welche Findings sind tatsaechlich ausnutzbar?")
    lines.append("3. Nur bestaetigte High/Critical Findings manuell verifizieren")
    lines.append("4. Fixes umsetzen, erneut scannen")

    return "\n".join(lines)



# ── Begruendete Ausnahmen ───────────────────────────────────────────────────
#
# Eine Ausnahme unterdrueckt keinen Befund. Sie nimmt ihn ausschliesslich aus
# der Gate-Wertung heraus, bleibt im Bericht sichtbar und faellt nach dem
# Ueberpruefungsdatum von selbst wieder weg. Zulaessig ist sie nur, wenn kein
# Herstellerfix existiert - genau dann laesst sich ein Befund nicht beheben,
# sondern nur bewerten und ueberwachen.
#
# Bewusst eng gehalten: exakte rule_id, exaktes Paket oder exakte Datei, keine
# Platzhalter. Fehlt ein Pflichtfeld oder ist es unglaubwuerdig gefuellt, bricht
# die Triage ab - ein defekter Ausnahmeeintrag darf nie stillschweigend als
# "keine Ausnahme" durchgehen.

REPO_ROOT = Path(__file__).resolve().parents[2]
EXCEPTIONS_PATH = REPO_ROOT / "config" / "security" / "triage-exceptions.json"

REQUIRED_EXCEPTION_FIELDS = (
    "id",            # eigene Kennung, z. B. der Slice
    "rule_id",       # exakte Regel-/CVE-Kennung
    "scope",         # {"package": "..."} oder {"file": "..."}
    "reason",        # warum der Befund nicht erreichbar oder nicht behebbar ist
    "evidence",      # woran das nachpruefbar ist
    "no_fix_available",  # muss true sein
    "review_by",     # ISO-Datum; danach greift die Ausnahme nicht mehr
    "owner",
)


class ExceptionConfigError(Exception):
    """Der Ausnahmekatalog ist unbrauchbar - die Triage bricht ab."""


def load_exceptions(path: Path = EXCEPTIONS_PATH) -> list[dict]:
    if not path.exists():
        return []
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ExceptionConfigError(f"{path} ist kein gueltiges JSON: {exc}") from exc

    entries = raw.get("exceptions") if isinstance(raw, dict) else raw
    if not isinstance(entries, list):
        raise ExceptionConfigError(f"{path}: 'exceptions' muss eine Liste sein")

    for idx, entry in enumerate(entries):
        where = f"{path}, Eintrag {idx}"
        if not isinstance(entry, dict):
            raise ExceptionConfigError(f"{where}: kein Objekt")
        missing = [f for f in REQUIRED_EXCEPTION_FIELDS if f not in entry]
        if missing:
            raise ExceptionConfigError(f"{where}: Pflichtfelder fehlen: {', '.join(missing)}")
        if entry["no_fix_available"] is not True:
            raise ExceptionConfigError(
                f"{where}: Ausnahmen sind nur zulaessig, wenn kein Herstellerfix "
                "existiert. Gibt es einen Fix, ist der Befund zu beheben."
            )
        scope = entry["scope"]
        if not isinstance(scope, dict) or not ({"package", "file"} & set(scope)):
            raise ExceptionConfigError(f"{where}: 'scope' braucht 'package' oder 'file'")
        for key in ("package", "file"):
            if key in scope and ("*" in str(scope[key]) or not str(scope[key]).strip()):
                raise ExceptionConfigError(f"{where}: '{key}' muss exakt sein, keine Platzhalter")
        if "*" in str(entry["rule_id"]):
            raise ExceptionConfigError(f"{where}: 'rule_id' muss exakt sein, keine Platzhalter")
        for key in ("reason", "evidence"):
            if len(str(entry[key]).strip()) < 30:
                raise ExceptionConfigError(
                    f"{where}: '{key}' muss die Lage nachvollziehbar erklaeren"
                )
        try:
            datetime.strptime(str(entry["review_by"]), "%Y-%m-%d")
        except ValueError as exc:
            raise ExceptionConfigError(f"{where}: 'review_by' muss YYYY-MM-DD sein") from exc

    return entries


def exception_matches(entry: dict, finding: dict) -> bool:
    if str(entry["rule_id"]) != str(finding.get("rule_id", "")):
        return False
    scope = entry["scope"]
    if "file" in scope and str(scope["file"]) != str(finding.get("file", "")):
        return False
    if "package" in scope:
        match = str(finding.get("match", ""))
        package = str(scope["package"])
        if not (match == package or match.startswith(package + " ")):
            return False
    return True


def apply_exceptions(findings: list[dict], entries: list[dict], today: str) -> list[dict]:
    """Markiert Befunde als begruendete Ausnahme. Entfernt nichts."""
    expired: list[dict] = []
    for entry in entries:
        is_expired = str(entry["review_by"]) < today
        hit = False
        for finding in findings:
            if exception_matches(entry, finding):
                hit = True
                finding["exception"] = {
                    "id": entry["id"],
                    "reason": entry["reason"],
                    "review_by": entry["review_by"],
                    "expired": is_expired,
                }
                finding["gate_excluded"] = not is_expired
        if is_expired and hit:
            expired.append(entry)
    return expired


# ── Main ────────────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print("Usage: triage_findings.py <report-dir>")
        sys.exit(1)

    report_dir = Path(sys.argv[1])
    if not report_dir.is_dir():
        print(f"Fehler: {report_dir} ist kein Verzeichnis")
        sys.exit(1)

    print(f"[triage] Lese Ergebnisse aus {report_dir}/ ...")

    # Alle Scanner-Ergebnisse einlesen
    all_findings = []
    all_findings.extend(parse_gitleaks(report_dir / "gitleaks.json"))
    all_findings.extend(parse_semgrep(report_dir / "semgrep.json"))
    all_findings.extend(parse_bandit(report_dir / "bandit.json"))
    all_findings.extend(parse_trivy_vuln(report_dir / "trivy-fs.json", "fs"))
    all_findings.extend(parse_trivy_vuln(report_dir / "trivy-config.json", "config"))
    all_findings.extend(parse_trivy_vuln(report_dir / "trivy-image.json", "image"))

    print(f"[triage] {len(all_findings)} Roh-Findings geladen")

    # Deduplizieren
    unique = deduplicate(all_findings)
    print(f"[triage] {len(unique)} nach Deduplizierung")

    # Sortieren
    unique.sort(key=sort_key)

    # Begruendete Ausnahmen anwenden (entfernt nichts, markiert nur)
    try:
        exceptions = load_exceptions()
    except ExceptionConfigError as exc:
        print(f"[triage] Ausnahmekatalog unbrauchbar: {exc}")
        return 1
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    expired = apply_exceptions(unique, exceptions, today)
    excepted = [f for f in unique if f.get("gate_excluded")]
    if exceptions:
        print(f"[triage] {len(exceptions)} Ausnahme(n) im Katalog, "
              f"{len(excepted)} Befund(e) davon erfasst")

    # Unified JSON
    report = {
        "meta": {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "repo": "VALEO-NeuroERP-3.0",
            "scanners": ["gitleaks", "semgrep", "bandit", "trivy-fs", "trivy-config", "trivy-image"],
            "total_findings": len(unique),
            "by_severity": {
                sev: sum(1 for f in unique if f["severity"] == sev)
                for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            },
            # Gate-Sicht: identisch, abzueglich der begruendeten Ausnahmen
            "by_severity_gate": {
                sev: sum(
                    1 for f in unique
                    if f["severity"] == sev and not f.get("gate_excluded")
                )
                for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]
            },
            "exceptions_applied": len(excepted),
            "exceptions_expired": [e["id"] for e in expired],
        },
        "findings": unique,
    }

    unified_path = report_dir / "unified_findings.json"
    unified_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"[triage] -> {unified_path}")

    # Summary
    summary = generate_summary(unique, report_dir)
    summary_path = report_dir / "summary.md"
    summary_path.write_text(summary, encoding="utf-8")
    print(f"[triage] -> {summary_path}")

    # Kurz-Stats
    crit = report["meta"]["by_severity"]["CRITICAL"]
    high = report["meta"]["by_severity"]["HIGH"]
    if crit > 0:
        print(f"[triage] !! {crit} CRITICAL findings — sofort beheben!")
    if high > 0:
        print(f"[triage] ! {high} HIGH findings — kurzfristig pruefen")

    for entry in expired:
        print(f"[triage] !! Ausnahme {entry['id']} ist seit {entry['review_by']} "
              "abgelaufen und greift nicht mehr - neu bewerten oder verlaengern")

    crit_gate = report["meta"]["by_severity_gate"]["CRITICAL"]
    if crit and not crit_gate:
        print(f"[triage] {crit} CRITICAL durch begruendete Ausnahmen gedeckt "
              "(siehe summary.md) - Gate bleibt gruen")

    return 0 if crit_gate == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
