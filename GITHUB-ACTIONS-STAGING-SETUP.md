***REMOVED*** GitHub Actions - Staging Deployment Setup

**Repository:** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0  
**Workflow-Datei:** `.github/workflows/deploy-staging.yml`  
**Status:** ✅ **READY TO USE**

---

***REMOVED******REMOVED*** 🎯 Übersicht

Der GitHub Actions Workflow `deploy-staging.yml` automatisiert das Deployment auf die Staging-Umgebung.

**Features:**
- ✅ Auto-Deploy bei Push auf `develop`-Branch
- ✅ Manueller Trigger via GitHub UI
- ✅ Automatische Security-Scans (Trivy, TruffleHog)
- ✅ Docker-Image-Build & Push
- ✅ Smoke-Tests nach Deployment
- ✅ Auto-Rollback bei Fehler
- ✅ Notifications bei Success/Failure

---

***REMOVED******REMOVED*** 🔐 GitHub Secrets konfigurieren

***REMOVED******REMOVED******REMOVED*** Erforderliche Secrets

Gehe zu: https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/settings/secrets/actions

Erstelle folgende **Repository Secrets:**

***REMOVED******REMOVED******REMOVED******REMOVED*** 1. Staging-Credentials

```
STAGING_POSTGRES_PASSWORD
```
**Wert:** Passwort für PostgreSQL-Datenbank (Staging)  
**Beispiel:** `valeo_staging_secure_2024!`

```
STAGING_KEYCLOAK_PASSWORD
```
**Wert:** Keycloak Admin-Passwort (Staging)  
**Beispiel:** `keycloak_admin_secure_2024!`

```
STAGING_PGADMIN_PASSWORD
```
**Wert:** pgAdmin Admin-Passwort (Staging)  
**Beispiel:** `pgadmin_secure_2024!`

```
STAGING_REDIS_PASSWORD
```
**Wert:** Redis Commander-Passwort (Staging)  
**Beispiel:** `redis_secure_2024!`

***REMOVED******REMOVED******REMOVED******REMOVED*** 2. Docker Registry (Optional)

Falls du Docker-Images in ein Registry pushen möchtest:

```
DOCKER_REGISTRY_USERNAME
```
**Wert:** Username für Docker Hub / GitHub Container Registry  
**Beispiel:** `JochenWeerda`

```
DOCKER_REGISTRY_TOKEN
```
**Wert:** Access Token für Docker Hub / GitHub Container Registry  
**Wie erstellen:**
- Docker Hub: https://hub.docker.com/settings/security
- GitHub: https://github.com/settings/tokens (mit `write:packages` Scope)

***REMOVED******REMOVED******REMOVED******REMOVED*** 3. Notifications (Optional)

```
SLACK_WEBHOOK_URL
```
**Wert:** Slack Webhook-URL für Deployment-Notifications  
**Wie erstellen:** https://api.slack.com/messaging/webhooks

---

***REMOVED******REMOVED*** 🚀 Workflow aktivieren

***REMOVED******REMOVED******REMOVED*** Option 1: Auto-Deploy bei Push auf `develop`

```bash
***REMOVED*** 1. Branch wechseln
git checkout develop

***REMOVED*** 2. Änderungen committen
git add .
git commit -m "feat: neues Feature für Staging"

***REMOVED*** 3. Pushen (triggert automatisch Workflow)
git push origin develop
```

**Workflow startet automatisch:**
1. Build & Test
2. Security-Scans
3. Deploy to Staging
4. Smoke-Tests
5. Notification

***REMOVED******REMOVED******REMOVED*** Option 2: Manueller Trigger (Workflow Dispatch)

1. Gehe zu: https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml
2. Klicke "Run workflow"
3. Wähle Branch: `develop` (oder anderen)
4. Optional: "Skip tests" auswählen
5. Klicke "Run workflow"

**Workflow startet manuell:**
- Vollständiger Deploy-Prozess
- Smoke-Tests (optional überspringen)
- Notification

---

***REMOVED******REMOVED*** 📊 Workflow-Jobs

Der Workflow besteht aus **6 Jobs:**

***REMOVED******REMOVED******REMOVED*** 1. Build & Test
- ⏱️ Dauer: ~5-10 Minuten
- 🔨 Node.js & Python Setup
- 📦 Dependencies installieren
- 🧪 Unit-Tests ausführen (optional)
- 🏗️ Docker-Images bauen
- 💾 Images als Artifacts speichern

***REMOVED******REMOVED******REMOVED*** 2. Security Scan
- ⏱️ Dauer: ~3-5 Minuten
- 🔍 Trivy Vulnerability Scanner
- 🔐 TruffleHog Secret Scanner
- 📤 SARIF-Upload zu GitHub Security

***REMOVED******REMOVED******REMOVED*** 3. Deploy
- ⏱️ Dauer: ~3-5 Minuten
- 📥 Docker-Images laden
- 🚀 Docker-Compose-Stack starten
- ⏳ Health-Checks warten
- 💾 Database-Migration

***REMOVED******REMOVED******REMOVED*** 4. Smoke Tests
- ⏱️ Dauer: ~2-3 Minuten
- ✅ 18 automatisierte Tests
- 🏥 Health-Checks
- 🔑 OIDC-Tests
- 📡 API-Tests

***REMOVED******REMOVED******REMOVED*** 5. Notify
- ⏱️ Dauer: ~1 Minute
- 📧 Email-Notification (optional)
- 💬 Slack-Notification (optional)
- ✅/❌ Success/Failure-Status

***REMOVED******REMOVED******REMOVED*** 6. Rollback (bei Fehler)
- ⏱️ Dauer: ~2 Minuten
- ⏪ Automatischer Rollback
- 📋 Previous-Version wiederherstellen
- 🚨 Notification

---

***REMOVED******REMOVED*** 📈 Workflow-Status überwachen

***REMOVED******REMOVED******REMOVED*** GitHub UI

**Workflow-Übersicht:**  
https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions

**Letzter Workflow-Run:**  
https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml

***REMOVED******REMOVED******REMOVED*** Workflow-Badge in README

Füge diesen Badge in die `README.md` ein:

```markdown
![Deploy Staging](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml/badge.svg)
```

**Ergebnis:**  
![Deploy Staging](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml/badge.svg)

***REMOVED******REMOVED******REMOVED*** GitHub CLI

```bash
***REMOVED*** Installiere GitHub CLI
***REMOVED*** https://cli.github.com/

***REMOVED*** Workflow-Status prüfen
gh workflow list

***REMOVED*** Letzte Runs anzeigen
gh run list --workflow=deploy-staging.yml

***REMOVED*** Logs anzeigen
gh run view <run-id> --log

***REMOVED*** Workflow manuell triggern
gh workflow run deploy-staging.yml --ref develop
```

---

***REMOVED******REMOVED*** 🐛 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Problem: Workflow startet nicht

**Mögliche Ursachen:**
1. Branch-Name falsch (nur `develop` triggert Auto-Deploy)
2. Workflow-Datei nicht im `main`-Branch
3. GitHub Actions für Repository deaktiviert

**Lösung:**
```bash
***REMOVED*** Prüfen ob Workflow-Datei existiert
git ls-files .github/workflows/

***REMOVED*** Workflow-Status prüfen
gh workflow list

***REMOVED*** GitHub Actions aktivieren
***REMOVED*** Settings → Actions → General → "Allow all actions"
```

***REMOVED******REMOVED******REMOVED*** Problem: Secrets nicht gefunden

**Symptom:**
```
Error: Required secret STAGING_POSTGRES_PASSWORD not found
```

**Lösung:**
1. Gehe zu: https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/settings/secrets/actions
2. Erstelle fehlendes Secret
3. Workflow neu starten

***REMOVED******REMOVED******REMOVED*** Problem: Docker-Build schlägt fehl

**Symptom:**
```
Error: failed to solve: process "/bin/sh -c npm install" did not complete successfully
```

**Lösung:**
```yaml
***REMOVED*** In .github/workflows/deploy-staging.yml prüfen:
***REMOVED*** - Node.js-Version korrekt? (20)
***REMOVED*** - Python-Version korrekt? (3.11)
***REMOVED*** - Cache-Konfiguration OK?
```

***REMOVED******REMOVED******REMOVED*** Problem: Smoke-Tests schlagen fehl

**Symptom:**
```
❌ PostgreSQL Health Check
❌ Keycloak Health Check
```

**Lösung:**
```yaml
***REMOVED*** Health-Check-Timeouts erhöhen:
- name: Wait for Health Checks
  run: |
    timeout 180 bash -c '...'  ***REMOVED*** Von 60 auf 180 erhöhen
```

***REMOVED******REMOVED******REMOVED*** Problem: Rollback funktioniert nicht

**Symptom:**
```
Error: Previous Docker images not found
```

**Lösung:**
- Beim ersten Deployment ist kein Rollback möglich (keine Previous-Version)
- Ab zweitem Deployment funktioniert Auto-Rollback

---

***REMOVED******REMOVED*** 🔧 Workflow anpassen

***REMOVED******REMOVED******REMOVED*** Build-Schritt überspringen

Wenn Images bereits gebaut sind:

```yaml
***REMOVED*** In .github/workflows/deploy-staging.yml:
***REMOVED*** Job "build" entfernen oder:
- name: Build Docker Images
  if: ${{ github.event.inputs.skip_build != 'true' }}
  run: |
    docker-compose -f docker-compose.staging.yml build
```

Dann manuell triggern mit Parameter.

***REMOVED******REMOVED******REMOVED*** Tests überspringen

Bereits implementiert:

```bash
***REMOVED*** Via GitHub UI: "Skip tests" = true auswählen
***REMOVED*** Via CLI:
gh workflow run deploy-staging.yml --ref develop -f skip_tests=true
```

***REMOVED******REMOVED******REMOVED*** Notifications hinzufügen

Aktiviere Slack-Notifications:

```yaml
***REMOVED*** In .github/workflows/deploy-staging.yml auskommentieren:
- name: Slack Notification
  uses: slackapi/slack-github-action@v1
  if: always()
  with:
    webhook-url: ${{ secrets.SLACK_WEBHOOK_URL }}
    payload: |
      {
        "text": "Staging Deployment: ${{ needs.smoke-tests.result }}"
      }
```

Dann `SLACK_WEBHOOK_URL` Secret erstellen.

---

***REMOVED******REMOVED*** 📋 Deployment-Checklist

Vor dem ersten Deployment:

***REMOVED******REMOVED******REMOVED*** GitHub-Setup
- [ ] Repository ist öffentlich oder Private-Access konfiguriert
- [ ] GitHub Actions aktiviert (Settings → Actions)
- [ ] Workflow-Datei in `main`-Branch vorhanden
- [ ] Branch `develop` existiert

***REMOVED******REMOVED******REMOVED*** Secrets konfiguriert
- [ ] `STAGING_POSTGRES_PASSWORD` gesetzt
- [ ] `STAGING_KEYCLOAK_PASSWORD` gesetzt
- [ ] `STAGING_PGADMIN_PASSWORD` gesetzt
- [ ] `STAGING_REDIS_PASSWORD` gesetzt
- [ ] (Optional) `DOCKER_REGISTRY_USERNAME` gesetzt
- [ ] (Optional) `DOCKER_REGISTRY_TOKEN` gesetzt
- [ ] (Optional) `SLACK_WEBHOOK_URL` gesetzt

***REMOVED******REMOVED******REMOVED*** Staging-Server
- [ ] Docker & Docker-Compose installiert
- [ ] Server erreichbar via SSH (falls Remote-Deploy)
- [ ] Genug Disk-Space (min. 20 GB)
- [ ] Ports verfügbar (3001, 8001, 8180, etc.)

***REMOVED******REMOVED******REMOVED*** Code bereit
- [ ] `docker-compose.staging.yml` committed
- [ ] `config/keycloak/realm-staging.json` committed
- [ ] `scripts/smoke-tests-staging.sh` committed
- [ ] `env.example.staging` committed

---

***REMOVED******REMOVED*** 🔄 Workflow-Lifecycle

***REMOVED******REMOVED******REMOVED*** Typischer Deployment-Ablauf

```mermaid
graph TD
    A[Push to develop] --> B[Workflow startet]
    B --> C[Build & Test]
    C --> D{Tests OK?}
    D -->|Ja| E[Security Scan]
    D -->|Nein| F[Workflow fails]
    E --> G{Vulnerabilities?}
    G -->|Nein| H[Deploy]
    G -->|Critical| F
    H --> I[Smoke Tests]
    I --> J{Tests OK?}
    J -->|Ja| K[Notify Success]
    J -->|Nein| L[Rollback]
    L --> M[Notify Failure]
```

***REMOVED******REMOVED******REMOVED*** Zeit-Übersicht

| Phase | Dauer | Kumuliert |
|-------|-------|-----------|
| Build & Test | 5-10 min | 10 min |
| Security Scan | 3-5 min | 15 min |
| Deploy | 3-5 min | 20 min |
| Smoke Tests | 2-3 min | 23 min |
| Notify | 1 min | 24 min |
| **Total** | **14-24 min** | - |

---

***REMOVED******REMOVED*** 📚 Weitere Ressourcen

***REMOVED******REMOVED******REMOVED*** GitHub Actions Dokumentation
- [GitHub Actions Overview](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Secrets Management](https://docs.github.com/en/actions/security-guides/encrypted-secrets)

***REMOVED******REMOVED******REMOVED*** VALEO-NeuroERP Dokumentation
- [STAGING-DEPLOYMENT.md](./STAGING-DEPLOYMENT.md) - Staging-Setup
- [DEPLOYMENT-PLAN.md](./DEPLOYMENT-PLAN.md) - Production-Deployment
- [scripts/README.md](./scripts/README.md) - Scripts-Dokumentation

***REMOVED******REMOVED******REMOVED*** Monitoring
- [GitHub Actions Dashboard](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions)
- [Security Alerts](https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/security)

---

***REMOVED******REMOVED*** ✅ Quick-Start

Minimale Schritte für erstes Deployment:

```bash
***REMOVED*** 1. Secrets konfigurieren (siehe oben)

***REMOVED*** 2. Code committen
git checkout develop
git add .
git commit -m "feat: staging deployment setup"
git push origin develop

***REMOVED*** 3. Workflow überwachen
***REMOVED*** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions

***REMOVED*** 4. Nach erfolgreichem Deploy testen
***REMOVED*** http://localhost:3001
```

---

**Status:** ✅ **GITHUB ACTIONS BEREIT - READY TO DEPLOY!**

**Repository:** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0  
**Workflow:** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml

---

**🚀 Auto-Deploy aktiviert! 🎉**

