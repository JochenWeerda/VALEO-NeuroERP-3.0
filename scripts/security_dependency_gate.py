"""Deterministic dependency decision gate; never changes dependencies or merges PRs.

Scanner findings remain intact. Unknown, expired or changed evidence blocks.
Only explicitly reviewed, unreachable findings may pass. A known reachable
vulnerability cannot be accepted by this policy format, regardless of severity.
"""
from datetime import date
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "config/security/dependency-decisions.json"
EVIDENCE_GLOBS = ("services/ai/**/*.py", "services/ai/Dockerfile", "services/ai/requirements.txt", "docker-compose*.yml", "k8s/**/*.yaml", "k8s/**/*.yml")


def fingerprint(root=ROOT):
    files = sorted({p for pattern in EVIDENCE_GLOBS for p in root.glob(pattern) if p.is_file()})
    return {p.relative_to(root).as_posix(): hashlib.sha256(p.read_text(encoding="utf-8").replace("\r\n", "\n").encode()).hexdigest() for p in files}


def embedded_chroma(root=ROOT):
    path = root / "services/ai/app/services/vector_store.py"
    if not path.is_file():
        return False
    source = path.read_text(encoding="utf-8")
    if "chromadb.PersistentClient(" not in source:
        return False
    forbidden = r"HttpClient|AsyncHttpClient|chroma_server_|SimpleRBACAuthorizationProvider|trust_remote_code"
    for pattern in EVIDENCE_GLOBS:
        for file in root.glob(pattern):
            if not file.is_file() or file.suffix == ".txt":
                continue
            text = file.read_text(encoding="utf-8")
            if re.search(forbidden, text) or "chromadb/chroma" in text or "ghcr.io/chroma-core" in text:
                return False
    return True


def evaluate(report, manifest, policy, root=ROOT, today=None):
    today = today or date.today()
    dependencies = report.get("dependencies")
    if not isinstance(dependencies, list) or not dependencies:
        raise ValueError("Missing or empty dependency inventory")
    if policy.get("schema_version") != 1 or not isinstance(policy.get("decisions"), list):
        raise ValueError("Invalid dependency decision policy")
    findings = []
    current = None
    for package in dependencies:
        if not isinstance(package, dict) or not package.get("name") or not package.get("version") or "skip_reason" in package:
            raise ValueError("Incomplete dependency inventory")
        vulns = package.get("vulns")
        if not isinstance(vulns, list):
            raise ValueError("Missing vulnerability collection")
        for vuln in vulns:
            if not isinstance(vuln, dict) or not vuln.get("id"):
                raise ValueError("Malformed finding")
            ids = {vuln["id"], *vuln.get("aliases", [])}
            candidates = [d for d in policy["decisions"] if d.get("manifest") == manifest
                          and d.get("package") == package["name"] and d.get("version") == package["version"]
                          and d.get("advisory") in ids]
            status, reason = "blocked", "No exact reviewed decision"
            decision_id = None
            if len(candidates) == 1:
                decision = candidates[0]
                decision_id = decision.get("advisory")
                try:
                    if decision.get("decision") != "not_affected" or decision.get("exploitability") != "unreachable":
                        raise ValueError("Reachable or unresolved finding blocks release")
                    if not decision.get("owner") or not decision.get("reason") or not decision.get("sources"):
                        raise ValueError("Review lacks owner, rationale or sources")
                    reviewed = date.fromisoformat(decision["reviewed_on"])
                    expires = date.fromisoformat(decision["review_by"])
                    if not reviewed <= today < expires or (expires - reviewed).days > 90:
                        raise ValueError("Review expired, future-dated or longer than 90 days")
                    if current is None:
                        current = fingerprint(root)
                    if not current or current != decision.get("evidence_sha256"):
                        raise ValueError("Reviewed source, manifest or deployment evidence changed")
                    if (decision.get("control") != "chroma_embedded_only"
                            or package["name"] != "chromadb"
                            or manifest != "services/ai/requirements.txt"
                            or decision["advisory"] not in {"CVE-2026-45833", "CVE-2026-45830", "CVE-2026-45831"}
                            or not embedded_chroma(root)):
                        raise ValueError("Reachability control not satisfied")
                    status, reason = "not_affected", decision["reason"]
                except (ValueError, KeyError, TypeError) as exc:
                    reason = str(exc)
            elif len(candidates) > 1:
                reason = "Conflicting decisions"
            findings.append({"package": package["name"], "version": package["version"],
                             "advisory": vuln["id"], "aliases": sorted(ids - {vuln["id"]}),
                             "fix_versions": vuln.get("fix_versions", []),
                             "decision": status, "reason": reason, "review": decision_id})
    # Deduplicate only display/decision rows, never mutate the original report.
    unique = {}
    for finding in findings:
        key = (finding["package"], finding["version"], finding["advisory"])
        if key not in unique or finding["decision"] == "blocked":
            unique[key] = finding
    rows = list(unique.values())
    blocked = sum(f["decision"] == "blocked" for f in rows)
    return {"manifest": manifest, "findings": rows, "blocked": blocked,
            "not_affected": len(rows) - blocked, "release_allowed": blocked == 0}


def assess_file(report, manifest, output, root=ROOT):
    data = json.loads(report.read_text(encoding="utf-8"))
    policy = json.loads((root / "config/security/dependency-decisions.json").read_text(encoding="utf-8"))
    result = evaluate(data, manifest, policy, root)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result
