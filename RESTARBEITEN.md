# VALEO-NeuroERP 3.0 – Restarbeiten (Finale Übersicht)

**Stand:** 13.02.2026  
**Branch:** `develop`

## 1. Finaler Status (kompakt)

### Erledigt
- P0/P1 Kernlücken geschlossen (Procurement, GoBD, Eventing/Outbox, zentrale API-Pfade).
- Mock-Reduktion in Frontend-Modulen inkl. Error-State-Handling umgesetzt.
- Procurement P2/P3 API+UI-Welle umgesetzt:
  - Lieferantenbewertung
  - Lieferanten-Dokumente
  - PO-Kommunikation (E-Mail/Portal)
  - Retouren (inkl. Status-Update)
  - Service Entry Sheets
  - Gutschriften/Belastungen
  - Standardreports + Audit-Drilldown
  - EDI-Portal
- OpenAPI/Swagger vervollständigt:
  - `docs/api/openapi.md`
  - `docs/api/openapi.json`
  - `scripts/export_openapi.py`
- Multi-Tenancy technisch aktiviert (Header/Context/Filterpfad):
  - `X-Tenant-ID` Verarbeitung Backend + Frontend-Propagation.
- Redis-Caching für häufige Procurement-Lesezugriffe ergänzt.
- DB-Index-Optimierung per Alembic-Migration ergänzt.
- ArgoCD/GitOps-Basis (App-of-Apps) ergänzt:
  - `k8s/argocd/*`
  - `docs/deployment/gitops/argocd.md`
- Storybook-Dokumentation aktualisiert:
  - `docs/setup/storybook.md`

### Vorbereitet (Artefakte vorhanden, operativ noch auszuführen)
- Production-Secrets-Checkliste: `docs/deployment/production-secrets.md`
- Staging-Verifikations-Runbook: `docs/deployment/staging-verification.md`
- Staging-Check-Skript: `scripts/check-staging.ps1`
- Monitoring-Verifikation: `docs/operations/monitoring-dashboards-verification.md`

---

## 2. Offene Punkte

### Qualität & Tests
- [ ] Unit-Test-Coverage-Ziel konsolidieren und nachweisen (Eintrag ist aktuell widersprüchlich: „>80%“ bei „punktuell 92–98%“).
- [ ] Performance-/Load-Tests durchführen und dokumentieren.

### Deployment & Rollout (operativ)
- [ ] GitHub Secrets (8 Production-Secrets) in der Zielumgebung setzen.
- [ ] Staging-Deployment durchführen und mit Runbook verifizieren.
- [ ] UAT mit Key-Usern durchführen und Abnahme dokumentieren.
- [ ] Blue-Green Deployment durchführen.
- [ ] Monitoring-Dashboards nach Go-Live-Kriterien final verifizieren.

---

## 3. Nächste sinnvolle Reihenfolge
1. Secrets setzen + Staging verifizieren.
2. UAT durchführen und Findings schließen.
3. Load-/Performance-Test fahren.
4. Blue-Green Rollout + Monitoring-Freigabe.

---

## 4. Referenzen
- Abnahme-Template Deployment/Rollout: `docs/deployment/go-live-abnahme-template.md`
- OpenAPI: `docs/api/openapi.md`
- Multi-Tenancy: `docs/deployment/multi-tenancy.md`
- GitOps/ArgoCD: `docs/deployment/gitops/argocd.md`
- Procurement-Smoketest: `docs/procurement-wave2-smoketest.md`
- Production Deployment Plan: `docs/PRODUCTION-DEPLOYMENT.md`


