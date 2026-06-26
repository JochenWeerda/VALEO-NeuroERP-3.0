#!/usr/bin/env bash
# Meta-Check fuer alle Doku-Generatoren mit --check-Unterstuetzung.
# Aufruf: scripts/check_all_doc_generators.sh [--check]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

MODE="${1:---check}"
if [[ "$MODE" != "--check" ]]; then
  echo "Nur --check wird unterstuetzt (Drift-Pruefung ohne Schreiben)." >&2
  exit 2
fi

echo "== OpenAPI"
python scripts/generate_openapi.py --check

echo "== Code-Inventare"
python scripts/generate_code_inventories.py --check

echo "== ADR-Navigation"
python scripts/generate_adr_nav.py --check

echo "== MCP-Tool-Referenz"
python scripts/generate_mcp_tool_reference.py --check

echo "== Action-Matrix-Report"
python scripts/generate_action_matrix_report.py --check

echo "== AI-Datenklassen-Policy"
python scripts/validate_data_classification.py

echo "== MCP-Tool-Registry (data_classification)"
python -c "from app.services.mcp_tool_registry_service import mcp_tool_registry_service as s; errs=s.validate_all(); assert not errs, errs"

echo "Alle Doc-Generator-Checks gruen."
