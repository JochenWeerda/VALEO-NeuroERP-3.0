# 🚀 Release-Runbook – VALERO NeuroERP

Standardabläufe für **Programm-Updates** (Patch, Minor, Major, Hotfix, Migrationen).

**Ziel:** Reproduzierbare, sichere und revisionssichere Rollouts.

---

## 📦 Release-Typen

### 1. Patch/Hotfix

**Zweck:** Fehlerkorrekturen, Security-Fixes, kleine UI-Fixes

**Versionierung:** `X.Y.Z+1` (z.B. 1.2.3 → 1.2.4)

**Strategie:** Rolling Update oder Canary (10% → 100%)

**Downtime:** ❌ Keine

**Tests:** Unit + E2E Regression

**Audit:** Freigabe + Release-Log

**Beispiel:** Bugfix in pricing-domain (falsche Rundung)

---

### 2. Minor Release

**Zweck:** Neue Features, backward-kompatibel

**Versionierung:** `X.Y+1.0` (z.B. 1.2.0 → 1.3.0)

**Strategie:** Blue/Green oder Canary

**Downtime:** ❌ Nein, außer DB-Migration erfordert Lock

**Tests:** Regression + Integrationstests

**Dokumente:** Release Notes → document-domain

**Audit:** Freigaben, Rollout-Schritte, Post-Checks

**Beispiel:** Neue Kanal-Adapter in notifications-domain

---

### 3. Major Release

**Zweck:** Breaking Changes (API, Events, DB-Schema)

**Versionierung:** `X+1.0.0` (z.B. 1.5.0 → 2.0.0)

**Strategie:** Blue/Green + erweiterte Canary-Phasen

**Downtime:** ⚠️ Möglich, nur nach Approval

**DB-Migrationen:** "Expand → Migrate → Contract"-Muster

**Tests:** Vollabdeckung (Unit, Integration, Load, Chaos)

**Dokumente:** Changelog, Migrationsleitfaden

**Audit:** Signierte Freigaben, Protokollierung aller Schritte

**Beispiel:** API v2 in contracts-domain

---

### 4. Migration Release

**Zweck:** Datenmigration (z.B. L3 → NeuroERP)

**Strategie:** Stepwise Migration + Dual-Run (Altsystem parallel)

**Tools:** CSV-Import, API-Connector (doku.service-erp.de)

**Tests:** Feldmapping, Probeimporte, Plausibilitätsprüfungen

**Audit:** Speicherung von Importfiles, Mapping-Logs, Fehlerlisten

**Rollback:** ⚠️ Nur über Backups möglich → vorher Pflicht!

**Beispiel:** Kundenstamm aus L3 → CRM-Domain

---

## 🛠️ Standardablauf (Scheduler + Audit)

### Phase 1: Vorbereitung

**Verantwortlich:** Release Manager + DevOps

**Schritte:**

1. ✅ **Changelog erstellen**
   - Markdown → PDF via document-domain
   - Changelog an Stakeholder via notifications-domain

2. ✅ **Version vergeben** (SemVer)
   - Git-Tag: `v1.3.0`
   - Docker-Image: `valero-neuroerp:1.3.0`

3. ✅ **CI/CD Build + Tests**
   - Unit-Tests: ✅ passing
   - Integration-Tests: ✅ passing
   - E2E-Tests: ✅ passing

4. ✅ **Audit-Log**
   - Release als Draft protokolliert
   - Event: `audit.release.planned`

**Checkpoint:** ✅ Alle Tests grün, Changelog genehmigt

---

### Phase 2: Pre-Checks

**Verantwortlich:** DevOps + QA

**Schritte:**

1. ✅ **Health-Check aller Services**
   ```bash
   curl http://document-domain:3070/health
   curl http://notifications-domain:3080/health
   curl http://audit-domain:3090/health
   ```

2. ✅ **DB-Migrationen Dry-Run**
   ```bash
   npm run migrate:gen --dry-run
   ```

3. ✅ **Schema-Kompatibilität prüfen**
   - Events (NATS-Schemas)
   - DTOs (Zod-Contracts)
   - API-Breaking-Changes (OpenAPI Diff)

4. ✅ **Audit-Log**
   - Pre-Check-Ergebnisse dokumentiert
   - Event: `audit.precheck.completed`

**Checkpoint:** ✅ Alle Pre-Checks grün

---

### Phase 3: Rollout

**Verantwortlich:** DevOps + Release Manager

**Strategien:**

#### **A) Rolling Update** (für Patches)
```bash
# Kubernetes Rolling Update
kubectl set image deployment/document-domain document=valero:1.2.4
```

#### **B) Canary Deployment** (für Minor)
```
Phase 1: 10% Traffic (Tenant: Pilot-1)
  ↓ 15 Min Monitoring
Phase 2: 50% Traffic (Tenant: Pilot-1-5)
  ↓ 30 Min Monitoring
Phase 3: 100% Traffic (alle Tenants)
```

#### **C) Blue/Green** (für Major)
```
Blue (alt): 100% Traffic
  ↓
Green (neu): Deploy + Tests
  ↓
Switch: 0% → 100% (DNS/Load-Balancer)
  ↓
Blue: Standby (15 Min), dann Shutdown
```

**Monitoring während Rollout:**

```bash
# Analytics-Domain KPIs überwachen
GET /analytics/api/v1/kpis/realtime?metric=error_rate,p95_latency,consumer_lag

# Alarm-Schwellwerte:
- Error-Rate > 1% → Pause Rollout
- p95-Latency > 500ms → Pause
- Consumer Lag > 1000 → Pause
```

**Notifications:**
- `notification.maintenance.scheduled` (24h vorher)
- `notification.release.started`
- `notification.release.progress` (pro Welle)

**Audit:**
- Event: `scheduler.release.deployed`
- Jede Welle einzeln geloggt

**Checkpoint:** ✅ Rollout läuft, KPIs stabil

---

### Phase 4: Post-Checks

**Verantwortlich:** QA + DevOps

**Schritte:**

1. ✅ **Logs & KPIs überwachen** (30 Min)
   ```bash
   # Analytics-Domain
   GET /analytics/api/v1/reports/release-comparison?before=1h&after=now
   ```

2. ✅ **UAT Smoke Tests**
   - Kritische User-Journeys durchspielen
   - Dokument erstellen → PDF → Email-Versand
   - Contract anlegen → Audit-Log prüfen

3. ✅ **Integritätsprüfung**
   ```bash
   # Audit-Domain
   GET /audit/api/v1/integrity/check?from=<release-start>
   ```

4. ✅ **Notifications**
   - `notification.release.successful`
   - Email an Stakeholder + On-Call

5. ✅ **Audit-Log**
   - Event: `audit.release.completed`
   - KPI-Vergleich gespeichert

**Checkpoint:** ✅ Release erfolgreich, keine Incidents

---

### Phase 5: Rollback (falls notwendig)

**Trigger:** Error-Rate > 2%, kritische Funktionen defekt, Integritätsverletzung

**Verantwortlich:** Release Manager (Entscheidung) + DevOps (Ausführung)

**Schritte:**

1. ⚠️ **Rollback-Entscheidung**
   - Schweregrad analysieren
   - Stakeholder informieren

2. ⚠️ **Rollback ausführen**
   
   **Rolling Update:**
   ```bash
   kubectl rollout undo deployment/document-domain
   ```

   **Blue/Green:**
   ```bash
   # Switch zurück auf Blue
   kubectl patch service document-domain -p '{"spec":{"selector":{"version":"blue"}}}'
   ```

   **Canary:**
   ```bash
   # Traffic auf 0% setzen
   kubectl set weight canary-service 0
   ```

3. ⚠️ **Down-Migrationen** (falls DB geändert)
   ```bash
   npm run migrate:down
   ```

4. ⚠️ **Feature Flags deaktivieren**
   ```bash
   # Kill-Switch via Redis
   redis-cli SET feature:new-pdf-renderer "false"
   ```

5. ⚠️ **Notifications**
   - `notification.rollback.executed`
   - Incident-Report an Stakeholder

6. ⚠️ **Audit-Log**
   - Event: `audit.release.rolledback`
   - Grund: <error-description>
   - Zeit: <timestamp>
   - Verantwortliche: <release-manager>

**Checkpoint:** ⚠️ Rollback erfolgreich, Altzustand wiederhergestellt

---

## 📑 Rollen & Verantwortung

| Rolle | Verantwortung |
|-------|---------------|
| **Release Manager** | Koordination, Approval, Rollback-Entscheidung |
| **DevOps** | CI/CD, Deployment, Monitoring |
| **QA** | Testabdeckung, Regression, Smoke Tests |
| **Product Owner** | Abnahme neuer Features |
| **Audit Officer** | Prüft Vollständigkeit der Logs |

---

## 🔗 Integration mit Domains

### scheduler-domain
- Automatisierte Rollouts
- Canary-Wellen (10% → 50% → 100%)
- Backfills nach DB-Migrationen

### document-domain
- Release Notes (PDF)
- Migrationsleitfäden
- Changelogs für Kunden

### notifications-domain
- Infos an Stakeholder
- Wartungsfenster-Ankündigungen
- On-Call-Alerts bei Problemen

### audit-domain
- Revisionssichere Protokollierung
- Freigaben (signiert)
- KPI-Vergleiche

### analytics-domain
- KPI-Vergleich Vorher/Nachher
- Error-Rate-Monitoring
- Performance-Metriken

---

## ✅ Release-Checkliste

### Vor dem Release

- [ ] Changelog vollständig
- [ ] Version korrekt (Git-Tag + Docker-Image)
- [ ] Alle Tests grün (Unit, Integration, E2E)
- [ ] DB-Migrationen geprüft (Dry-Run)
- [ ] Schema-Breaking-Changes dokumentiert
- [ ] Rollback-Plan bereit
- [ ] Stakeholder informiert (24h vorher)
- [ ] Audit: Release als Draft protokolliert

### Während des Rollouts

- [ ] Health-Checks laufen grün
- [ ] Monitoring aktiv (Error-Rate, Latenz, Lag)
- [ ] Canary-Wellen nach Plan
- [ ] Logs überwacht (Fehler, Warnings)
- [ ] Notifications verschickt (Start, Fortschritt)
- [ ] Audit: Jede Welle geloggt

### Nach dem Release

- [ ] Smoke Tests durchgeführt
- [ ] KPI-Vergleich analysiert
- [ ] Integritätsprüfung erfolgreich
- [ ] Release Notes veröffentlicht
- [ ] Stakeholder informiert (Success)
- [ ] Audit: Release als Completed protokolliert
- [ ] Retrospektive geplant

### Bei Rollback

- [ ] Rollback-Grund dokumentiert
- [ ] Down-Migrationen ausgeführt
- [ ] Feature Flags deaktiviert
- [ ] Incident-Report erstellt
- [ ] Stakeholder informiert
- [ ] Audit: Rollback protokolliert
- [ ] Post-Mortem geplant

---

## 📊 SLO-Schwellwerte für Rollout-Pause

| Metrik | Schwellwert | Aktion |
|--------|-------------|--------|
| **Error-Rate** | > 1% | ⚠️ Pause Rollout |
| **p95-Latenz** | > 500ms | ⚠️ Pause Rollout |
| **Consumer Lag** | > 1000 Events | ⚠️ Pause Rollout |
| **Failed Health-Checks** | > 0 | 🛑 Stop & Rollback |
| **Integrity-Check** | Failed | 🛑 Stop & Rollback |

---

## 🔄 DB-Migrations-Pattern

### Expand → Migrate → Contract

**Kompatible Änderungen (kein Downtime):**

```sql
-- Phase 1: EXPAND (alte + neue Spalten)
ALTER TABLE contracts ADD COLUMN new_field TEXT;

-- Phase 2: MIGRATE (Daten kopieren)
UPDATE contracts SET new_field = old_field WHERE new_field IS NULL;

-- Phase 3: CONTRACT (alte Spalten entfernen, nächstes Release)
ALTER TABLE contracts DROP COLUMN old_field;
```

**Breaking Changes (mit Downtime):**

```sql
-- Downtime-Fenster erforderlich
BEGIN;
  ALTER TABLE invoices RENAME COLUMN amount TO total_gross;
  -- App-Deploy während Transaction
COMMIT;
```

---

## 📡 Event-Sequenz

### Erfolgreicher Rollout:
```
1. scheduler.release.planned        (T-24h)
2. notification.maintenance.scheduled (T-24h)
3. scheduler.release.started        (T+0)
4. scheduler.release.wave1          (T+5min)
5. scheduler.release.wave2          (T+20min)
6. scheduler.release.wave3          (T+50min)
7. scheduler.release.completed      (T+60min)
8. analytics.release.metrics        (T+90min)
9. notification.release.successful  (T+90min)
10. audit.release.logged            (T+90min)
```

### Rollback-Sequenz:
```
1. scheduler.release.paused         (T+15min)
2. notification.rollback.initiated  (T+15min)
3. scheduler.release.rolledback     (T+20min)
4. notification.rollback.completed  (T+20min)
5. audit.rollback.logged            (T+20min)
```

---

## 🎯 Beispiel: Minor Release (document-domain 1.3.0)

### Scope
- Neue Funktion: Batch-Processing
- API: `POST /documents/batch`
- DB: Keine Schema-Änderungen
- Events: Keine Breaking Changes

### Timeline

| Zeit | Phase | Aktion |
|------|-------|--------|
| **T-24h** | Vorbereitung | Release Notes erstellt, Stakeholder informiert |
| **T-1h** | Pre-Checks | Health-Checks ✅, DB-Dry-Run ✅ |
| **T+0** | Rollout Start | Canary 10% (Pilot-Tenant) |
| **T+15min** | Monitoring | Error-Rate 0.1%, Latenz 120ms ✅ |
| **T+15min** | Wave 2 | Canary 50% (5 Tenants) |
| **T+30min** | Monitoring | Error-Rate 0.2%, Latenz 135ms ✅ |
| **T+30min** | Wave 3 | 100% (alle Tenants) |
| **T+60min** | Post-Checks | Smoke Tests ✅, KPI-Vergleich ✅ |
| **T+90min** | Abschluss | Release Notes published, Audit completed |

### Audit-Trail
```json
{
  "releaseId": "rel-2025-10-001",
  "version": "1.3.0",
  "domain": "document-domain",
  "approvedBy": "release-manager-123",
  "deployedAt": "2025-10-15T20:00:00Z",
  "completedAt": "2025-10-15T21:30:00Z",
  "waves": [
    {"wave": 1, "tenants": ["pilot-1"], "traffic": "10%", "status": "success"},
    {"wave": 2, "tenants": ["pilot-2","pilot-3","pilot-4","pilot-5"], "traffic": "50%", "status": "success"},
    {"wave": 3, "tenants": ["all"], "traffic": "100%", "status": "success"}
  ],
  "kpiComparison": {
    "errorRateBefore": 0.05,
    "errorRateAfter": 0.02,
    "p95LatencyBefore": 180,
    "p95LatencyAfter": 135
  }
}
```

---

## 🚨 Incident-Handling

### Schweregrade

| Grad | Beschreibung | Aktion |
|------|--------------|--------|
| **P0** | Kompletter Service-Ausfall | 🛑 Sofortiger Rollback |
| **P1** | Kritische Funktion defekt | ⚠️ Rollback oder Hotfix |
| **P2** | Performance-Degradation | ⏸️ Pause, Analyse, weiter oder Rollback |
| **P3** | Minor-Bug, Workaround verfügbar | ✅ Weiter, Hotfix später |

### Eskalationskette
```
1. On-Call Engineer (sofort)
   ↓ (15 Min, keine Lösung)
2. Release Manager
   ↓ (30 Min, keine Lösung)
3. CTO
```

---

## 📖 Dokumentations-Artefakte

### Vor Release
- [ ] Release Notes (Markdown)
- [ ] API-Changelog (OpenAPI Diff)
- [ ] DB-Migrations-Plan
- [ ] Rollback-Strategie

### Nach Release
- [ ] Deployment-Report (PDF)
- [ ] KPI-Vergleich (CSV/PDF)
- [ ] Audit-Trail (signiert)
- [ ] Lessons Learned (Retrospektive)

---

## 🎯 Success-Kriterien

✅ **Release erfolgreich, wenn:**
- Alle Tests grün
- Error-Rate < Baseline
- p95-Latenz < Baseline + 10%
- Keine Rollback-Trigger
- Integritätsprüfung ✅
- Audit-Log vollständig

---

**Version:** 1.0  
**Wartung:** Bei jedem Major-Release aktualisieren  
**Owner:** DevOps + Release Management

