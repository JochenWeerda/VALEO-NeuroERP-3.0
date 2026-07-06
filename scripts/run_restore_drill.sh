#!/usr/bin/env bash
# =============================================================================
# run_restore_drill.sh — Backup-/Restore-Drill mit 15-min-RTO-Messung (SPEC-P0-08)
#
# Fuehrt den bestehenden Restore-Test (scripts/backup-restore-test.sh) aus,
# misst die Wiederherstellungszeit gegen das RTO-Ziel und schreibt ein
# maschinenlesbares Drill-Protokoll. Das Protokoll wird nach
# docs/operations/drill-protocols/ committet — es ist die Evidenz, die
# scripts/check_restore_drill_evidence.py und die Assessor-Simulation pruefen.
#
# Aufruf (Ops, gegen produktionsnahe Umgebung):
#   BACKUP_DIR=/backups/postgresql/daily DB_HOST=... DB_USER=... \
#     bash scripts/run_restore_drill.sh
#
# Variablen:
#   RTO_TARGET_MINUTES  Ziel-Wiederanlaufzeit (Default 15)
#   DRILL_OPERATOR      Name des Durchfuehrenden (Pflicht fuer das Protokoll)
# =============================================================================
set -euo pipefail

RTO_TARGET_MINUTES="${RTO_TARGET_MINUTES:-15}"
DRILL_OPERATOR="${DRILL_OPERATOR:-unbekannt}"
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROTO_DIR="$REPO_ROOT/docs/operations/drill-protocols"
mkdir -p "$PROTO_DIR"

STAMP="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
DATE_SLUG="$(date -u +%Y-%m-%d)"
START_EPOCH=$(date +%s)

echo ">>> Restore-Drill gestartet: $STAMP (RTO-Ziel: ${RTO_TARGET_MINUTES} min)"

STATUS="passed"
ERROR_MSG=""
if ! bash "$REPO_ROOT/scripts/backup-restore-test.sh"; then
    STATUS="failed"
    ERROR_MSG="backup-restore-test.sh exit != 0"
fi

END_EPOCH=$(date +%s)
DURATION_S=$((END_EPOCH - START_EPOCH))
DURATION_MIN=$(( (DURATION_S + 59) / 60 ))
RTO_MET="false"
if [ "$STATUS" = "passed" ] && [ "$DURATION_MIN" -le "$RTO_TARGET_MINUTES" ]; then
    RTO_MET="true"
fi
if [ "$RTO_MET" != "true" ] && [ "$STATUS" = "passed" ]; then
    STATUS="rto_missed"
fi

PROTO_FILE="$PROTO_DIR/restore-drill-$DATE_SLUG.json"
cat > "$PROTO_FILE" <<PROTO
{
  "drill_type": "backup-restore",
  "executed_at": "$STAMP",
  "operator": "$DRILL_OPERATOR",
  "environment": "${DRILL_ENVIRONMENT:-staging}",
  "rto_target_minutes": $RTO_TARGET_MINUTES,
  "duration_seconds": $DURATION_S,
  "duration_minutes": $DURATION_MIN,
  "rto_met": $RTO_MET,
  "status": "$STATUS",
  "error": "$ERROR_MSG",
  "evidence": "Ausgefuehrt via scripts/run_restore_drill.sh (wrappt scripts/backup-restore-test.sh)"
}
PROTO

echo ">>> Drill-Protokoll: $PROTO_FILE (Status: $STATUS, Dauer: ${DURATION_MIN} min)"
echo ">>> Naechste Schritte: Protokoll reviewen, committen, im Freigabe-Protokoll referenzieren."
[ "$STATUS" = "passed" ]
