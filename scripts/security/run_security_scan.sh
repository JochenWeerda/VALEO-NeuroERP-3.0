#!/usr/bin/env bash
# =============================================================================
# VALEO NeuroERP — Security Agent: Lokaler Scanner-Orchestrator
# =============================================================================
# Kombiniert: Gitleaks + Semgrep + Trivy + Bandit
# Erzeugt: unified_findings.json + summary.md
#
# Voraussetzungen:
#   brew/apt/choco install: gitleaks semgrep trivy jq python3
#   pip install bandit[toml]
#
# Nutzung:
#   ./run_security_scan.sh                          # Repo-Scan
#   IMAGE_NAME=local/app:test ./run_security_scan.sh  # + Docker-Image
# =============================================================================
set -euo pipefail

REPO_ROOT="${1:-$(git rev-parse --show-toplevel 2>/dev/null || pwd)}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="${REPO_ROOT}/security-reports/${TIMESTAMP}"
mkdir -p "${REPORT_DIR}"

IMAGE_NAME="${IMAGE_NAME:-}"
SCAN_TIMEOUT="${SCAN_TIMEOUT:-300}"

# Farben (falls Terminal)
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; BLUE='\033[0;34m'; NC='\033[0m'

log()  { echo -e "${BLUE}[security-agent]${NC} $*"; }
ok()   { echo -e "${GREEN}[OK]${NC} $*"; }
warn() { echo -e "${YELLOW}[WARN]${NC} $*"; }
fail() { echo -e "${RED}[FAIL]${NC} $*"; }

# ─── Tool-Check ──────────────────────────────────────────────────────────────
check_tool() {
    if command -v "$1" &>/dev/null; then
        ok "$1 gefunden: $(command -v "$1")"
        return 0
    else
        warn "$1 nicht installiert — Scan wird uebersprungen"
        return 1
    fi
}

log "VALEO NeuroERP Security Agent"
log "Repo:     ${REPO_ROOT}"
log "Reports:  ${REPORT_DIR}"
log "Image:    ${IMAGE_NAME:-<kein Image-Scan>}"
echo ""

TOOLS_AVAILABLE=()
for tool in gitleaks semgrep trivy bandit jq python3; do
    if check_tool "$tool"; then
        TOOLS_AVAILABLE+=("$tool")
    fi
done

if ! printf '%s\n' "${TOOLS_AVAILABLE[@]}" | grep -q "^jq$"; then
    fail "jq ist Pflicht fuer die Ergebnis-Zusammenfuehrung. Bitte installieren."
    exit 1
fi
if ! printf '%s\n' "${TOOLS_AVAILABLE[@]}" | grep -q "^python3$"; then
    fail "python3 ist Pflicht fuer die Triage. Bitte installieren."
    exit 1
fi

echo ""
log "═══════════════════════════════════════════════════════════"
log "  Stufe 1: Secrets-Scan (Gitleaks)"
log "═══════════════════════════════════════════════════════════"

if printf '%s\n' "${TOOLS_AVAILABLE[@]}" | grep -q "^gitleaks$"; then
    log "Starte Gitleaks..."
    gitleaks detect \
        --source="${REPO_ROOT}" \
        --report-format=json \
        --report-path="${REPORT_DIR}/gitleaks.json" \
        --no-banner \
        --exit-code 0 \
        2>&1 | tail -5 || true
    GITLEAKS_COUNT=$(jq 'length' "${REPORT_DIR}/gitleaks.json" 2>/dev/null || echo "0")
    log "Gitleaks: ${GITLEAKS_COUNT} Findings"
else
    echo '[]' > "${REPORT_DIR}/gitleaks.json"
    GITLEAKS_COUNT=0
fi

echo ""
log "═══════════════════════════════════════════════════════════"
log "  Stufe 2: SAST (Semgrep)"
log "═══════════════════════════════════════════════════════════"

if printf '%s\n' "${TOOLS_AVAILABLE[@]}" | grep -q "^semgrep$"; then
    log "Starte Semgrep (auto + custom rules)..."

    SEMGREP_ARGS=(
        scan
        --json
        --output "${REPORT_DIR}/semgrep.json"
        --timeout "${SCAN_TIMEOUT}"
        --max-target-bytes 1000000
    )

    # Custom Rules falls vorhanden
    CUSTOM_RULES="${REPO_ROOT}/scripts/security/semgrep-rules.yml"
    if [ -f "${CUSTOM_RULES}" ]; then
        SEMGREP_ARGS+=(--config "${CUSTOM_RULES}")
    fi

    # Standard-Rulesets
    SEMGREP_ARGS+=(
        --config "p/python"
        --config "p/javascript"
        --config "p/typescript"
        --config "p/owasp-top-ten"
        --config "p/security-audit"
    )

    SEMGREP_ARGS+=("${REPO_ROOT}")

    semgrep "${SEMGREP_ARGS[@]}" 2>&1 | tail -10 || true
    SEMGREP_COUNT=$(jq '.results | length' "${REPORT_DIR}/semgrep.json" 2>/dev/null || echo "0")
    log "Semgrep: ${SEMGREP_COUNT} Findings"
else
    echo '{"results":[],"errors":[]}' > "${REPORT_DIR}/semgrep.json"
    SEMGREP_COUNT=0
fi

echo ""
log "═══════════════════════════════════════════════════════════"
log "  Stufe 3: Python-SAST (Bandit)"
log "═══════════════════════════════════════════════════════════"

if printf '%s\n' "${TOOLS_AVAILABLE[@]}" | grep -q "^bandit$"; then
    log "Starte Bandit..."
    bandit -r "${REPO_ROOT}/app" "${REPO_ROOT}/modules" \
        -f json \
        -o "${REPORT_DIR}/bandit.json" \
        --exit-zero \
        2>&1 | tail -5 || true
    BANDIT_COUNT=$(jq '.results | length' "${REPORT_DIR}/bandit.json" 2>/dev/null || echo "0")
    log "Bandit: ${BANDIT_COUNT} Findings"
else
    echo '{"results":[],"metrics":{}}' > "${REPORT_DIR}/bandit.json"
    BANDIT_COUNT=0
fi

echo ""
log "═══════════════════════════════════════════════════════════"
log "  Stufe 4: Trivy (Filesystem + Config)"
log "═══════════════════════════════════════════════════════════"

TRIVY_FS_COUNT=0
TRIVY_CONFIG_COUNT=0
TRIVY_IMAGE_COUNT=0

if printf '%s\n' "${TOOLS_AVAILABLE[@]}" | grep -q "^trivy$"; then
    # 4a: Filesystem (Dependencies + Secrets)
    log "Trivy fs (Abhaengigkeiten + Secrets)..."
    trivy fs \
        --format json \
        --output "${REPORT_DIR}/trivy-fs.json" \
        --severity HIGH,CRITICAL \
        --scanners vuln,secret \
        "${REPO_ROOT}" 2>&1 | tail -5 || true
    TRIVY_FS_COUNT=$(jq '[.Results[]? | .Vulnerabilities // [] | length] | add // 0' "${REPORT_DIR}/trivy-fs.json" 2>/dev/null || echo "0")
    log "Trivy fs: ${TRIVY_FS_COUNT} Vulnerabilities"

    # 4b: Config (Dockerfiles + IaC)
    log "Trivy config (Dockerfile + IaC Misconfigs)..."
    trivy config \
        --format json \
        --output "${REPORT_DIR}/trivy-config.json" \
        --severity HIGH,CRITICAL \
        "${REPO_ROOT}" 2>&1 | tail -5 || true
    TRIVY_CONFIG_COUNT=$(jq '[.Results[]? | .Misconfigurations // [] | length] | add // 0' "${REPORT_DIR}/trivy-config.json" 2>/dev/null || echo "0")
    log "Trivy config: ${TRIVY_CONFIG_COUNT} Misconfigurations"

    # 4c: Image (optional)
    if [ -n "${IMAGE_NAME}" ]; then
        log "Trivy image: ${IMAGE_NAME}..."
        trivy image \
            --format json \
            --output "${REPORT_DIR}/trivy-image.json" \
            --severity HIGH,CRITICAL \
            --image-config-scanners misconfig \
            "${IMAGE_NAME}" 2>&1 | tail -5 || true
        TRIVY_IMAGE_COUNT=$(jq '[.Results[]? | (.Vulnerabilities // []) + (.Misconfigurations // []) | length] | add // 0' "${REPORT_DIR}/trivy-image.json" 2>/dev/null || echo "0")
        log "Trivy image: ${TRIVY_IMAGE_COUNT} Findings"
    fi
else
    echo '{"Results":[]}' > "${REPORT_DIR}/trivy-fs.json"
    echo '{"Results":[]}' > "${REPORT_DIR}/trivy-config.json"
fi

echo ""
log "═══════════════════════════════════════════════════════════"
log "  Stufe 5: Triage + Unified Report"
log "═══════════════════════════════════════════════════════════"

TRIAGE_SCRIPT="${REPO_ROOT}/scripts/security/triage_findings.py"
if [ -f "${TRIAGE_SCRIPT}" ]; then
    python3 "${TRIAGE_SCRIPT}" "${REPORT_DIR}"
    ok "Unified report: ${REPORT_DIR}/unified_findings.json"
    ok "Summary:        ${REPORT_DIR}/summary.md"
else
    warn "triage_findings.py nicht gefunden — uebersprungen"
fi

echo ""
log "═══════════════════════════════════════════════════════════"
log "  ERGEBNIS"
log "═══════════════════════════════════════════════════════════"

TOTAL=$((GITLEAKS_COUNT + SEMGREP_COUNT + BANDIT_COUNT + TRIVY_FS_COUNT + TRIVY_CONFIG_COUNT + TRIVY_IMAGE_COUNT))

echo ""
echo "  Gitleaks (Secrets):        ${GITLEAKS_COUNT}"
echo "  Semgrep  (SAST):           ${SEMGREP_COUNT}"
echo "  Bandit   (Python SAST):    ${BANDIT_COUNT}"
echo "  Trivy fs (Dependencies):   ${TRIVY_FS_COUNT}"
echo "  Trivy config (Dockerfile): ${TRIVY_CONFIG_COUNT}"
echo "  Trivy image (Container):   ${TRIVY_IMAGE_COUNT}"
echo "  ─────────────────────────────"
echo "  GESAMT:                    ${TOTAL}"
echo ""
echo "  Reports: ${REPORT_DIR}/"
echo ""

if [ "${TOTAL}" -gt 0 ]; then
    log "Naechster Schritt: unified_findings.json + llm_triage_prompt.txt an LLM geben"
else
    ok "Keine High/Critical Findings gefunden."
fi
