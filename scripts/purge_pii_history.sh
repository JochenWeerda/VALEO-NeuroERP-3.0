#!/usr/bin/env bash
# =============================================================================
# purge_pii_history.sh — Git-History-Bereinigung (SPEC-P0-04 / Prompt A2)
#
# ACHTUNG: DIESES SKRIPT NICHT UNGEPRUEFT AUSFUEHREN.
# Es schreibt die komplette Git-Historie um und erfordert einen Force-Push.
# Vorbereitet am 2026-07-02 durch den PII-Remediation-Lauf (Branch
# fix/pii-remediation). Ausfuehrung ist eine bewusste Betreiber-Entscheidung
# (external_gate) — siehe artifacts/pii-remediation-report.md.
#
# VORAUSSETZUNGEN
#   1. git-filter-repo installiert:  pip install git-filter-repo
#   2. Alle offenen Branches/PRs gemerged oder gesichert — Force-Push
#      invalidiert JEDE bestehende Clone-Historie.
#   3. VOLLSTAENDIGES BACKUP (Schritt 1 unten) an sicherem Ort.
#
# FOLGEN DES FORCE-PUSH (vorab kommunizieren!)
#   - Alle Clones muessen neu geklont werden (git pull führt zu Konflikt-Chaos).
#   - Offene PRs verlieren ihre Basis; Commit-SHAs aendern sich repo-weit.
#   - GitHub cached alte Blobs weiter (Forks, PR-Refs, Web-Cache). Nach dem
#     Force-Push MUSS ein GitHub-Support-Ticket gestellt werden:
#     https://support.github.com/ -> "Remove cached views / dangling commits".
#   - Secret-Rotation ist UNABHAENGIG davon Pflicht: Historisch exponierte
#     Schluessel (LinkUp-API-Key, Keycloak-DB-Passwoerter, Fiskaly-Key,
#     Beispiel-JWTs) gelten als kompromittiert, egal ob die Historie
#     bereinigt wird. (external_gate fuer Betreiber)
# =============================================================================
set -euo pipefail

REMOTE_URL="https://github.com/JochenWeerda/VALEO-NeuroERP-3.0.git"
WORKDIR="${WORKDIR:-$HOME/pii-purge-$(date +%Y%m%d)}"

echo ">>> Schritt 1: Backup-Clone (Mirror) anlegen"
mkdir -p "$WORKDIR"
git clone --mirror "$REMOTE_URL" "$WORKDIR/backup.git"
echo "    Backup liegt in $WORKDIR/backup.git — NICHT loeschen."

echo ">>> Schritt 2: Frischen Arbeits-Clone fuer filter-repo anlegen"
# git-filter-repo verlangt einen frischen Clone (Schutzmechanismus).
git clone "$REMOTE_URL" "$WORKDIR/filter-work"
cd "$WORKDIR/filter-work"

echo ">>> Schritt 3: Pfade aus der GESAMTEN Historie entfernen"
# Hygiene-/PII-Kandidaten aus dem A2-Lauf 2026-07-02.
# Hinweis Befund: PLZ_26XXX_final_leads.json enthielt in ALLEN historischen
# Versionen KEINE personenbezogenen Daten (nur aggregierte Nullstatistik).
# Die Entfernung aus der Historie ist Hygiene, keine Breach-Remediation.
git filter-repo \
  --invert-paths \
  --path PLZ_26XXX_final_leads.json \
  --path ostfriesland_flaechenprämien_leads.json \
  --path ostfriesland_leads_26400-26999.json \
  --path ostfriesland_corrected_26400-26999.json \
  --path ostfriesland_measure_codes_analysis.json \
  --path .tmp_changed_files.txt \
  --path .tmp_dlg01_23.txt \
  --path .tmp_dlg01_25.txt \
  --path tmp_lieferschein_head.tsx \
  --path .tmp_export/ \
  --path tmp_playwright_mask_test/ \
  --path playwright-results.json \
  --path dist/ \
  --path evidence/screenshots/ \
  --path node_modules/ \
  --path de_modules/ \
  --path-glob '*/dist/*'

echo ">>> Schritt 4 (OPTIONAL, empfohlen): historische Secret-Strings scrubben"
# Die Dateien mit historisch eingecheckten Secrets (siehe gitleaks-History-Scan
# im Remediation-Report) existieren im Arbeitsbaum nicht mehr, ihre Inhalte
# aber noch in der Historie:
#   ALLE-SCHRITTE-ABGESCHLOSSEN.md, CRM-IMPLEMENTATION-COMPLETE.md,
#   CRM-IMPLEMENTATION-STATUS-FINAL.md, HEUTE-IMPLEMENTIERT-2025-10-11-FINAL.md,
#   INVENTORY-AUDIT-WORKFLOWS.md, POLICY-AUTH-COMPLETE.md,
#   scripts/genxais_prompt_generator_simple.py (alte Version),
#   scripts/mcp_server.py (alte Version), scripts/test_mcp_api.py (alte Version),
#   docker-compose.auth.yml / docker-compose.production.yml (alte Versionen)
#
# Variante A — Secret-Werte ersetzen (Dateien bleiben in der Historie):
#   1. Secrets aus dem gitleaks-History-Report extrahieren (Feld "Secret")
#      und je Zeile in expressions.txt schreiben:  <secret>==>REDACTED
#   2. git filter-repo --replace-text expressions.txt
#
# Variante B — die Alt-Dokumente komplett aus der Historie entfernen:
#   git filter-repo --invert-paths \
#     --path ALLE-SCHRITTE-ABGESCHLOSSEN.md \
#     --path CRM-IMPLEMENTATION-COMPLETE.md \
#     --path CRM-IMPLEMENTATION-STATUS-FINAL.md \
#     --path HEUTE-IMPLEMENTIERT-2025-10-11-FINAL.md \
#     --path INVENTORY-AUDIT-WORKFLOWS.md \
#     --path POLICY-AUTH-COMPLETE.md
#
# In BEIDEN Varianten gilt: Rotation der betroffenen Secrets bleibt Pflicht.

echo ">>> Schritt 5: Ergebnis pruefen (NICHTS wird gepusht)"
git log --oneline -5
echo "    Kontrolle: git log --all --follow -- PLZ_26XXX_final_leads.json  (muss leer sein)"
echo "    Kontrolle: gitleaks git . --no-banner  (History-Scan wiederholen)"

cat <<'NEXT'
>>> Schritt 6: MANUELL — Force-Push (bewusste Entscheidung, NICHT Teil dieses Skripts)
    cd <filter-work>
    git remote add origin https://github.com/JochenWeerda/VALEO-NeuroERP-3.0.git
    git push origin --force --all
    git push origin --force --tags

>>> Schritt 7: MANUELL — Nacharbeiten
    1. GitHub-Support-Ticket: Cached Views / dangling Commits entfernen lassen.
    2. Branch-Protection auf main reaktivieren (Force-Push wieder verbieten).
    3. Alle Mitarbeitenden/Agenten informieren: Clones verwerfen, neu klonen.
    4. Secret-Rotation abschliessen und im Freigabe-Protokoll dokumentieren.
    5. artifacts/pii-remediation-report.md um Ausfuehrungsdatum ergaenzen.
NEXT
