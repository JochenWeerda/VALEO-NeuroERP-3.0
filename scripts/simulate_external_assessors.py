from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


@dataclass(frozen=True)
class Check:
    id: str
    title: str
    evidence: tuple[str, ...]
    external_gate: str | None = None
    required_content: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Profile:
    id: str
    assessor: str
    standard: str
    source: str
    checks: tuple[Check, ...]


PROFILES = (
    Profile(
        "tax-gobd",
        "Simulierter Steuerberater / GoBD-Pruefer",
        "GoBD, AO §§ 146/147, VALEO-Zusatzstandard",
        "https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/2025-07-14-GoBD-2-aenderung.html",
        (
            Check(
                "GOBD-01",
                "Unveraenderbarkeit und Gegenbuchung",
                ("app/services/finance_transaction_service.py", "tests/test_crm360_finance_handover.py"),
                required_content=(("app/services/finance_transaction_service.py", "reversal"),),
            ),
            Check(
                "GOBD-02",
                "Nachvollziehbare Audit-Kette",
                ("app/middleware/audit_middleware.py", "tests/test_audit_hash_chain.py"),
                required_content=(("tests/test_audit_hash_chain.py", "hash"),),
            ),
            Check("GOBD-03", "Datenzugriff und Export", ("app/api/v1/endpoints/pos_dsfinvk.py", "docs/architecture/pos-fiscalization-providers.md")),
            Check("GOBD-04", "Verfahrensdokumentation und Betriebsnachweis", ("docs/operations/production-readiness-runbook.md",), "Steuerberater-Abnahme der konkreten Verfahrensdokumentation"),
        ),
    ),
    Profile(
        "cash-register",
        "Simulierter Kassen-Nachschau-/KassenSichV-Pruefer",
        "KassenSichV Stand 14.01.2026, DSFinV-K 2.4, strengere VALEO-Gates",
        "https://www.gesetze-im-internet.de/kassensichv/BJNR351500017.html",
        (
            Check("KASSE-01", "Unmittelbarer Transaktionsstart und Abschluss", ("app/services/fiscalization/service.py", "tests/test_pos_fiscalization_providers.py")),
            Check("KASSE-02", "Belegpflichtdaten und Signaturreferenz", ("app/services/fiscalization/contracts.py", "packages/frontend-web/src/lib/services/fiskaly-tse.ts")),
            Check(
                "KASSE-03",
                "DSFinV-K 2.4 Export- und Tagesabschluss-Gate",
                ("app/api/v1/endpoints/pos_dsfinvk.py", "docs/quality-assurance/pos-fiscalization-operations-uat.md"),
                required_content=(("docs/architecture/pos-fiscalization-providers.md", "DSFinV-K 2.4"),),
            ),
            Check("KASSE-04", "Reale TSE-/Pruefwerkzeugvalidierung", ("docs/architecture/pos-fiscalization-providers.md",), "Hersteller-/Pruefwerkzeug-Abnahme mit produktiver TSE"),
        ),
    ),
    Profile(
        "information-security",
        "Simulierter BSI-/ISO-27001-Auditor",
        "BSI IT-Grundschutz plus VALEO Null-Toleranz fuer ungepruefte Produktionskonfiguration",
        "https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/IT-Grundschutz/it-grundschutz_node.html",
        (
            Check("SEC-01", "IAM, Least Privilege und Tenant-Isolation", ("app/middleware/tenant_enforcement.py", "tests/test_tenant_enforcement.py")),
            Check(
                "SEC-02",
                "Blockierende High/Critical-Scans und SBOM",
                (".github/workflows/security-scan.yml", ".github/workflows/quality-gate.yml"),
                required_content=(
                    (
                        ".github/workflows/security-scan.yml",
                        "trivy image --severity HIGH,CRITICAL --ignore-unfixed --exit-code 1",
                    ),
                    (".github/workflows/security-scan.yml", "fail-build: true"),
                    (".github/workflows/security-scan.yml", "Enforce ZAP medium/high gate"),
                    (".github/workflows/quality-gate.yml", "SBOM (CycloneDX)"),
                ),
            ),
            Check("SEC-03", "Backup und regelmaessiger Restore-Test", ("k8s/helm/valeo-erp/templates/backup-cronjob.yaml", "k8s/helm/valeo-erp/templates/restore-test-cronjob.yaml")),
            Check(
                "SEC-04",
                "Incident-, Rollback- und Monitoring-Vertrag",
                (
                    "docs/operations/production-readiness-runbook.md",
                    ".github/workflows/deploy-staging.yml",
                    ".github/workflows/valeo-erp-deployment.yml",
                ),
                "Betriebsuebung mit realem Cluster und Alarmkanal",
            ),
        ),
    ),
    Profile(
        "privacy",
        "Simulierter Datenschutzbeauftragter",
        "DSGVO Art. 5, 25, 30, 32, 33/34 plus VALEO-Nachweispflichten",
        "https://eur-lex.europa.eu/eli/reg/2016/679/oj",
        (
            Check("DSGVO-01", "Privacy by Design und Zugriffstrennung", ("app/middleware/tenant_enforcement.py", "tests/test_gdpr_api.py")),
            Check("DSGVO-02", "Verzeichnis von Verarbeitungstaetigkeiten", ("app/api/v1/endpoints/gdpr_art30_ropa.py", "tests/test_gdpr_art30_ropa.py")),
            Check("DSGVO-03", "Breach-Prozess und Fristnachweis", ("app/api/v1/endpoints/gdpr_art33_breach.py", "tests/test_gdpr_art33_breach.py")),
            Check("DSGVO-04", "AVV, DSFA und reale Organisationsfreigabe", ("docs/project-context/open-gaps-and-known-issues.md",), "DSB-/Rechtsfreigabe und unterschriebene AVV/DSFA"),
        ),
    ),
    Profile(
        "operations",
        "Simulierter Betriebs-/Notfallpruefer",
        "BSI Datensicherung/Notfallmanagement plus strengere Release-Evidenz",
        "https://www.bsi.bund.de/DE/Themen/Unternehmen-und-Organisationen/Standards-und-Zertifizierung/IT-Grundschutz/it-grundschutz_node.html",
        (
            Check(
                "OPS-01",
                "Immutable Release-Artefakte und geschuetzte Environments",
                (".github/workflows/deploy-staging.yml", ".github/workflows/valeo-erp-deployment.yml", "k8s/helm/valeo-erp/values-production.yaml"),
                required_content=(
                    (".github/workflows/deploy-staging.yml", "sha-${GITHUB_SHA}"),
                    (".github/workflows/deploy-staging.yml", "Dockerfile.frontend"),
                    (".github/workflows/valeo-erp-deployment.yml", "environment:"),
                    (".github/workflows/valeo-erp-deployment.yml", "frontend.image.tag"),
                ),
            ),
            Check(
                "OPS-02",
                "Migration vor Rollout und automatischer Smoke",
                (".github/workflows/deploy-staging.yml", ".github/workflows/valeo-erp-deployment.yml", "scripts/check_production_readiness.py"),
                required_content=(
                    (".github/workflows/deploy-staging.yml", "scripts/init_db.py"),
                    (".github/workflows/deploy-staging.yml", "/readyz"),
                    (".github/workflows/valeo-erp-deployment.yml", "scripts/init_db.py"),
                    (".github/workflows/valeo-erp-deployment.yml", "/readyz"),
                ),
            ),
            Check(
                "OPS-03",
                "Rollback bei fehlgeschlagenem Smoke",
                (".github/workflows/deploy-staging.yml", ".github/workflows/valeo-erp-deployment.yml", "docs/operations/production-readiness-runbook.md"),
                required_content=(
                    (".github/workflows/deploy-staging.yml", "--atomic --wait"),
                    (".github/workflows/valeo-erp-deployment.yml", "helm rollback"),
                ),
            ),
            Check(
                "OPS-04",
                "Wiederanlauf, RTO/RPO und Alarmierung im Zielbetrieb",
                (
                    "k8s/helm/valeo-erp/templates/restore-test-cronjob.yaml",
                    "scripts/run_restore_drill.sh",
                    "scripts/check_restore_drill_evidence.py",
                    "docs/operations/drill-protocols/README.md",
                ),
                "Beobachteter Restore-/Incident-Drill im produktionsnahen Cluster (Protokoll via scripts/run_restore_drill.sh committen)",
            ),
        ),
    ),
    Profile(
        "soc2",
        "Simulierter SOC-2-Pruefer (Type-I-Readiness)",
        "AICPA Trust Services Criteria: Security (Pflicht) + Availability + Confidentiality + Processing Integrity",
        "https://www.aicpa-cima.com/topic/audit-assurance/audit-and-assurance-greater-than-soc-2",
        (
            Check(
                "SOC2-CC1",
                "Kontrollumfeld: Review-Verantwortung und Arbeitssteuerung dokumentiert",
                (".github/CODEOWNERS", "docs/agent-ops/active-workboard.md"),
                required_content=((".github/CODEOWNERS", "SPEC-P0-06"),),
            ),
            Check(
                "SOC2-CC6",
                "Logischer Zugriff: OIDC/JWKS, Bearer-Enforcement, Tenant-Isolation mit Negativtests",
                ("app/middleware/tenant_enforcement.py", "tests/test_tenant_enforcement.py", "app/core/security.py"),
                "Offboarding-/Access-Review-Prozess des Betreibers (Prozessnachweis ausserhalb des Repos)",
            ),
            Check(
                "SOC2-CC7",
                "Betrieb: Monitoring/Alerting, Incident-Runbook, nightly Runtime-Sweep als Betriebsevidenz",
                ("docs/operations/production-readiness-runbook.md", ".github/workflows/runtime-sweep.yml", "scripts/api_runtime_sweep.py"),
                "Beobachteter Incident-/Restore-Drill im Zielbetrieb",
            ),
            Check(
                "SOC2-CC8",
                "Change Management: CI-Pflichtgates, unveraenderliche SHA-Images, only-up-Coverage-Ratchet",
                (".github/workflows/quality-gate.yml", "config/coverage_ratchet_baseline.json", "scripts/check_critical_backend_coverage.py"),
                "Branch-Protection auf main (Review + required Status-Checks) — GitHub-Einstellung des Betreibers",
            ),
            Check(
                "SOC2-CC9",
                "Lieferanten/Subprozessoren: Risiko- und Vertragsuebersicht inkl. LLM-Provider",
                ("docs/operations/production-readiness-runbook.md",),
                "AVV-/Subprozessor-Verzeichnis mit Unterschriften (Keycloak-Betrieb, Fiskaly, Paperless, DATEV, LLM-Provider)",
            ),
            Check(
                "SOC2-A1",
                "Verfuegbarkeit: Backup-/Restore-Automation und Wiederanlauf-Vertrag",
                (
                    "k8s/helm/valeo-erp/templates/backup-cronjob.yaml",
                    "k8s/helm/valeo-erp/templates/restore-test-cronjob.yaml",
                    "scripts/run_restore_drill.sh",
                ),
                "15-min-RTO-Drill (Protokoll in docs/operations/drill-protocols/) und Erntepeak-Lasttest auf Staging (Betreiber)",
            ),
            Check(
                "SOC2-C1",
                "Vertraulichkeit: Secret-Scanning ohne Baseline, PII-Vorfall dokumentiert und remediert",
                (".gitleaks.toml", "artifacts/pii-remediation-report.md", "scripts/purge_pii_history.sh"),
                "History-Purge-Ausfuehrung, Secret-Rotation und DSB-Entscheidung (external)",
            ),
            Check(
                "SOC2-PI1",
                "Verarbeitungsintegritaet: 3-Wege-Match, GoBD-Nachweisraum, Audit-Kette",
                ("tests/test_einkauf_3way_match_ers_rfq.py", "tests/test_docflow_gobd.py", "app/middleware/audit_middleware.py"),
            ),
        ),
    ),
)


def evaluate(profile: Profile) -> dict:
    checks = []
    for check in profile.checks:
        missing = [path for path in check.evidence if not (ROOT / path).exists()]
        failed_assertions = []
        for path, required in check.required_content:
            target = ROOT / path
            if not target.exists() or required not in target.read_text(encoding="utf-8"):
                failed_assertions.append(f"{path}: fehlt Inhalt {required!r}")
        status = "fail" if missing or failed_assertions else ("external_gate" if check.external_gate else "pass")
        checks.append(
            {
                **asdict(check),
                "status": status,
                "missing_evidence": missing,
                "failed_assertions": failed_assertions,
            }
        )
    return {
        "id": profile.id,
        "assessor": profile.assessor,
        "standard": profile.standard,
        "source": profile.source,
        "status": "fail" if any(item["status"] == "fail" for item in checks) else "conditional",
        "checks": checks,
    }


def markdown_report(result: dict) -> str:
    lines = [
        "# Simulierte externe Production-Readiness-Pruefung",
        "",
        f"Stand: {result['date']}",
        "",
        "> Eine Simulation ersetzt keine gesetzliche Zertifizierung, Herstellerpruefung oder Unterschrift.",
        "> Fehlende Live-Evidenz bleibt ein blockierendes externes Gate.",
        "",
    ]
    for profile in result["profiles"]:
        lines.extend((f"## {profile['assessor']}", "", f"Standard: {profile['standard']}", ""))
        for check in profile["checks"]:
            lines.append(f"- `{check['id']}` {check['status'].upper()}: {check['title']}")
            if check["external_gate"]:
                lines.append(f"  Externes Gate: {check['external_gate']}")
        lines.append("")
    lines.extend(
        (
            "## Gesamturteil",
            "",
            "Repo-seitige Evidenz ist nur dann bestanden, wenn alle referenzierten Artefakte vorhanden sind.",
            "Der Go-live bleibt blockiert, solange mindestens ein externes Gate nicht durch reale Evidenz geschlossen ist.",
            "",
        )
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-json", type=Path, required=True)
    parser.add_argument("--output-markdown", type=Path, required=True)
    args = parser.parse_args()
    result = {"date": date.today().isoformat(), "profiles": [evaluate(profile) for profile in PROFILES]}
    args.output_json.parent.mkdir(parents=True, exist_ok=True)
    args.output_markdown.parent.mkdir(parents=True, exist_ok=True)
    args.output_json.write_text(json.dumps(result, indent=2, ensure_ascii=True), encoding="utf-8")
    args.output_markdown.write_text(markdown_report(result), encoding="utf-8")
    failed = any(profile["status"] == "fail" for profile in result["profiles"])
    print(json.dumps(result, indent=2, ensure_ascii=True))
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
