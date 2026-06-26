# Abnahme-Template: Deployment & Go-Live (Punkte 3-7)

Stand: 2026-02-13
Geltungsbereich: RESTARBEITEN.md offene Deployment/Rollout-Punkte

## Verwendung
- Pro Punkt Owner benennen.
- Nachweis-Link/Artefakt eintragen.
- Erst auf "Erledigt" setzen, wenn alle Done-Kriterien erfüllt sind.

---

## 3) GitHub Secrets setzen (8 Production-Secrets)
Status: [ ] Offen  [ ] In Arbeit  [ ] Erledigt
Owner:
Termin:
Nachweise:

Done-Kriterien:
- Alle 8 Pflicht-Secrets in GitHub Environment `production` vorhanden.
- Secrets sind nicht leer und plausibel formatiert.
- Preflight/Deploy-Workflow liest Secrets erfolgreich (kein missing-secret Fehler).
- Rotationstermin dokumentiert.

Checkliste:
- [ ] `DATABASE_URL`
- [ ] `SECRET_KEY`
- [ ] `ENCRYPTION_KEY`
- [ ] `REDIS_URL`
- [ ] `OIDC_ISSUER_URL`
- [ ] `OIDC_JWKS_URL`
- [ ] `OIDC_CLIENT_ID`
- [ ] `OIDC_CLIENT_SECRET`

---

## 4) Staging-Deployment durchführen und verifizieren
Status: [ ] Offen  [ ] In Arbeit  [ ] Erledigt
Owner:
Termin:
Nachweise:

Done-Kriterien:
- Staging-Deployment erfolgreich ausgerollt.
- `healthz`, `readyz`, `openapi.json` sind 2xx.
- Kern-Smoke (CRM, Einkauf, Finance) erfolgreich.
- Keine kritischen Fehler im Log/Monitoring.

Checkliste:
- [ ] Deployment-Run erfolgreich
- [ ] `scripts/check-staging.ps1 -BaseUrl <staging-url>` erfolgreich
- [ ] Smoke-Test protokolliert
- [ ] Findings erfasst und bewertet

---

## 5) UAT mit Key-Usern durchführen
Status: [ ] Offen  [ ] In Arbeit  [ ] Erledigt
Owner:
Termin:
Nachweise:

Done-Kriterien:
- UAT-Testplan abgestimmt und freigegeben.
- Key-User je Domäne haben Kernprozesse getestet.
- Kritische Defects geschlossen oder mit akzeptiertem Workaround versehen.
- Fachliche Abnahme dokumentiert (Sign-off).

Checkliste:
- [ ] UAT-Slots geplant
- [ ] Testprotokolle vollständig
- [ ] Defect-Liste priorisiert
- [ ] Sign-off vorhanden

---

## 6) Blue-Green Deployment durchführen
Status: [ ] Offen  [ ] In Arbeit  [ ] Erledigt
Owner:
Termin:
Nachweise:

Done-Kriterien:
- Green-Umgebung vollständig provisioniert.
- Smoke/Health auf Green erfolgreich.
- Traffic kontrolliert umgeschaltet.
- Rollback-Pfad getestet und dokumentiert.

Checkliste:
- [ ] Green bereit
- [ ] Pre-Switch Checks grün
- [ ] Traffic-Switch durchgeführt
- [ ] Post-Switch Stabilitätsfenster ohne kritische Incidents
- [ ] Rollback-Drill dokumentiert

---

## 7) Monitoring-Dashboards final verifizieren
Status: [ ] Offen  [ ] In Arbeit  [ ] Erledigt
Owner:
Termin:
Nachweise:

Done-Kriterien:
- Pflicht-Dashboards vollständig und aktuell.
- SLO-relevante Panels (5xx, Latenz, DB, Outbox, Host) im grünen Bereich.
- Alerting getestet (mind. 1 Testalarm je kritischer Klasse).
- Freigabe für Go-Live dokumentiert.

Checkliste:
- [ ] Dashboard-Review abgeschlossen
- [ ] Alert-Test durchgeführt
- [ ] 30-Minuten Stabilitätsbeobachtung dokumentiert
- [ ] Go-Live-Freigabe erteilt

---

## Abschlussprotokoll
Gesamtstatus: [ ] Nicht freigegeben  [ ] Bedingt freigegeben  [ ] Freigegeben
Freigabe durch:
Datum:
Anmerkungen:
