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
    lines.append("| Severity | Anzahl |")
    lines.append("|----------|--------|")
    for sev in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
        count = sum(1 for f in findings if f["severity"] == sev)
        if count > 0:
            lines.append(f"| {sev} | {count} |")
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

    return 0 if crit == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
