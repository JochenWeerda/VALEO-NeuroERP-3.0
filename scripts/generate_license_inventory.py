#!/usr/bin/env python3
"""SPEC-P1-09: Lizenzinventar aus installierten Distributionen + Requirements erzeugen.

Schreibt artifacts/license-inventory.json und aktualisiert den maschinenlesbaren
Block in docs/operations/license-inventory.md. THIRD_PARTY_NOTICES.md bleibt die
menschliche Attribution fuer besondere Upstream-Integrationen.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from datetime import date
from importlib.metadata import PackageNotFoundError, distribution, distributions
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "requirements.txt"
OUT_JSON = ROOT / "artifacts" / "license-inventory.json"
OUT_MD = ROOT / "docs" / "operations" / "license-inventory.md"

# Bekannte Integrations- und Betriebs-Abhaengigkeiten ausserhalb von pip
STATIC_INTEGRATIONS = (
    {
        "name": "superglue",
        "source": "github.com/superglue-ai/superglue",
        "license": "FSL-1.1-Apache-2.0",
        "notes": "Siehe THIRD_PARTY_NOTICES.md; Attributionspflicht bei Redistribution.",
    },
    {
        "name": "Keycloak / OIDC-Provider",
        "source": "Betrieb / Compose",
        "license": "Apache-2.0",
        "notes": "IAM-Sidecar; Lizenz des konkreten Distributionsimages pruefen.",
    },
    {
        "name": "Paperless-ngx",
        "source": "DMS-Sidecar",
        "license": "GPL-3.0",
        "notes": "Separater Container; kein VALEO-Code-Merge.",
    },
    {
        "name": "PostgreSQL",
        "source": "Datenbank",
        "license": "PostgreSQL License",
        "notes": "Betriebssystem-/Image-Lizenz des Betreibers.",
    },
    {
        "name": "Redis",
        "source": "Cache",
        "license": "RSALv2 / SSPL (Image-abhaengig)",
        "notes": "Offizielle Redis-Images beachten; ggf. Valkey/KeyDB-Alternative.",
    },
    {
        "name": "NATS JetStream",
        "source": "Event-Bus",
        "license": "Apache-2.0",
        "notes": "nats-server Image.",
    },
)


def _parse_requirements(path: Path) -> list[str]:
    names: list[str] = []
    if not path.exists():
        return names
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("-") or line.startswith("http"):
            continue
        name = re.split(r"[<>=!~;\[]", line, maxsplit=1)[0].strip()
        if name:
            names.append(name)
    return names


def _license_of(dist_name: str) -> tuple[str, str]:
    try:
        dist = distribution(dist_name)
    except PackageNotFoundError:
        return ("not-installed", "")
    meta = dist.metadata
    lic = (
        meta.get("License-Expression")
        or meta.get("License")
        or ""
    ).strip()
    if not lic:
        for classifier in meta.get_all("Classifier") or []:
            if classifier.startswith("License ::"):
                lic = classifier.split("::")[-1].strip()
                break
    version = meta.get("Version") or ""
    return (lic or "UNKNOWN", version)


def build_inventory() -> dict:
    req_names = _parse_requirements(REQ)
    packages = []
    for name in sorted(set(req_names), key=str.lower):
        lic, version = _license_of(name)
        packages.append(
            {
                "name": name,
                "version": version or None,
                "license": lic,
                "from": "requirements.txt",
            }
        )

    # Zusaetzlich: grobe Statistik aller installierten Distributionen (Dev-Umgebung)
    installed_licenses = Counter()
    for dist in distributions():
        name = dist.metadata.get("Name") or dist.metadata.get("name")
        if not name:
            continue
        lic = (
            dist.metadata.get("License-Expression")
            or dist.metadata.get("License")
            or "UNKNOWN"
        ).strip() or "UNKNOWN"
        installed_licenses[lic.splitlines()[0][:80]] += 1

    return {
        "generated": date.today().isoformat(),
        "spec": "SPEC-P1-09",
        "requirements_packages": packages,
        "static_integrations": list(STATIC_INTEGRATIONS),
        "installed_license_histogram": dict(installed_licenses.most_common(40)),
        "sbom_source": ".github/workflows/quality-gate.yml → SBOM (CycloneDX)",
        "notices_file": "THIRD_PARTY_NOTICES.md",
    }


def render_markdown(data: dict) -> str:
    lines = [
        "---",
        "title: Lizenzinventar",
        "type: reference",
        "audience: [betrieb, recht, entwickler]",
        "owner: Cursor Agent",
        "status: aktiv",
        f"last_reviewed: {data['generated']}",
        "version: 1.0.0",
        "description: SPEC-P1-09 — Lizenzinventar aus Requirements und bekannten Integrationen; SBOM via CycloneDX in CI.",
        "---",
        "",
        "# Lizenzinventar (SPEC-P1-09)",
        "",
        f"Stand: **{data['generated']}** (generiert durch `scripts/generate_license_inventory.py`).",
        "",
        "Vollstaendige Release-SBOM: CI-Job **SBOM (CycloneDX)** in",
        "`.github/workflows/quality-gate.yml` → Artefakt `valeo-neuroerp-sbom.cdx.json`.",
        "",
        "Besondere Attribution: [`THIRD_PARTY_NOTICES.md`](../../THIRD_PARTY_NOTICES.md).",
        "",
        "## Statische Integrationen / Sidecars",
        "",
        "| Name | Lizenz | Quelle | Hinweis |",
        "|---|---|---|---|",
    ]
    for item in data["static_integrations"]:
        lines.append(
            f"| {item['name']} | {item['license']} | {item['source']} | {item['notes']} |"
        )
    lines.extend(
        (
            "",
            "## Python-Requirements (installiert falls vorhanden)",
            "",
            "| Paket | Version | Lizenz |",
            "|---|---|---|",
        )
    )
    for pkg in data["requirements_packages"]:
        ver = pkg["version"] or "—"
        lines.append(f"| `{pkg['name']}` | {ver} | {pkg['license']} |")
    lines.extend(
        (
            "",
            "## Hinweise",
            "",
            "- `UNKNOWN` / `not-installed`: Paket lokal nicht installiert oder ohne",
            "  Metadaten — fuer Release immer die CycloneDX-SBOM massgeblich.",
            "- GPL-/AGPL-Sidecars (z. B. Paperless) werden **nicht** in den VALEO-",
            "  Anwendungscode gemerged; sie laufen als separate Container.",
            "- Redis-Image-Lizenz je Distribution pruefen (RSALv2/SSPL vs. Valkey).",
            "",
        )
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json-out", type=Path, default=OUT_JSON)
    parser.add_argument("--md-out", type=Path, default=OUT_MD)
    args = parser.parse_args()
    data = build_inventory()
    args.json_out.parent.mkdir(parents=True, exist_ok=True)
    args.json_out.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    args.md_out.parent.mkdir(parents=True, exist_ok=True)
    # docs-markdown-check verbietet Trailing-Whitespace; eingebettete
    # Upstream-Lizenztexte bringen ihn mit, semantisch traegt er nichts.
    markdown = "\n".join(
        line.rstrip() for line in render_markdown(data).split("\n")
    )
    args.md_out.write_text(markdown, encoding="utf-8")
    print(f"wrote {args.json_out}")
    print(f"wrote {args.md_out}")
    print(f"packages={len(data['requirements_packages'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
