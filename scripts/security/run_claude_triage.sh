#!/usr/bin/env bash
# =============================================================================
# VALEO NeuroERP — Security Agent: Claude Code LLM-Triage
# =============================================================================
# Liest unified_findings.json und laesst Claude Code die Triage durchfuehren.
#
# Voraussetzung: Claude Code CLI installiert (claude)
#
# Nutzung:
#   ./run_claude_triage.sh security-reports/20260331_120000/
#   ./run_claude_triage.sh report/   # nach CI-Download
# =============================================================================
set -euo pipefail

REPORT_DIR="${1:?Usage: $0 <report-dir>}"
UNIFIED="${REPORT_DIR}/unified_findings.json"
PROMPT_FILE="$(dirname "$0")/llm_triage_prompt.txt"
OUTPUT="${REPORT_DIR}/llm_triage_result.md"

if [ ! -f "${UNIFIED}" ]; then
    echo "Fehler: ${UNIFIED} nicht gefunden"
    exit 1
fi

if [ ! -f "${PROMPT_FILE}" ]; then
    echo "Fehler: ${PROMPT_FILE} nicht gefunden"
    exit 1
fi

TOTAL=$(python3 -c "import json; print(json.load(open('${UNIFIED}'))['meta']['total_findings'])")
echo "[claude-triage] ${TOTAL} Findings in ${UNIFIED}"
echo "[claude-triage] Starte Claude Code Triage..."

# Claude Code aufrufen mit Prompt + Findings
PROMPT=$(cat "${PROMPT_FILE}")

cat <<EOF | claude --print > "${OUTPUT}"
${PROMPT}

== FINDINGS ==

$(cat "${UNIFIED}")
EOF

echo "[claude-triage] Ergebnis: ${OUTPUT}"
echo "[claude-triage] Fertig."
