# GitHub Secrets Setup - Schritt-für-Schritt Anleitung

**Repository:** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0  
**Datum:** 2024-10-10  
**Status:** 🔐 Secrets konfigurieren

---

## 📋 Übersicht - Erforderliche Secrets

Für das Staging-Deployment via GitHub Actions benötigst du **4 Secrets**:

| Secret-Name | Beschreibung | Beispielwert |
|-------------|--------------|--------------|
| `STAGING_POSTGRES_PASSWORD` | PostgreSQL-Datenbank-Passwort | `valeo_staging_secure_2024!` |
| `STAGING_KEYCLOAK_PASSWORD` | Keycloak Admin-Passwort | `keycloak_admin_secure_2024!` |
| `STAGING_PGADMIN_PASSWORD` | pgAdmin-Passwort | `pgadmin_secure_2024!` |
| `STAGING_REDIS_PASSWORD` | Redis Commander-Passwort | `redis_secure_2024!` |

---

## 🚀 Schritt-für-Schritt Anleitung

### Schritt 1: GitHub Repository öffnen

Öffne dein Repository im Browser:

**URL:** https://github.com/JochenWeerda/VALEO-NeuroERP-3.0

### Schritt 2: Settings öffnen

1. Klicke auf **"Settings"** (oben rechts im Repository)
2. Falls du keinen Zugriff hast: Du benötigst **Admin**- oder **Maintainer**-Rechte

### Schritt 3: Secrets-Seite öffnen

1. Im linken Menü: **"Secrets and variables"** aufklappen
2. Klicke auf **"Actions"**

**Direkt-Link:**  
https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/settings/secrets/actions

### Schritt 4: Secret erstellen (wiederholen für alle 4 Secrets)

#### Secret 1: STAGING_POSTGRES_PASSWORD

1. Klicke **"New repository secret"** (grüner Button oben rechts)
2. **Name:** `STAGING_POSTGRES_PASSWORD`
3. **Secret:** Gib ein sicheres Passwort ein, z.B.:
   ```
   valeo_staging_secure_2024!
   ```
4. Klicke **"Add secret"**

✅ Secret erfolgreich erstellt!

#### Secret 2: STAGING_KEYCLOAK_PASSWORD

1. Klicke **"New repository secret"**
2. **Name:** `STAGING_KEYCLOAK_PASSWORD`
3. **Secret:** Gib ein sicheres Passwort ein, z.B.:
   ```
   keycloak_admin_secure_2024!
   ```
4. Klicke **"Add secret"**

✅ Secret erfolgreich erstellt!

#### Secret 3: STAGING_PGADMIN_PASSWORD

1. Klicke **"New repository secret"**
2. **Name:** `STAGING_PGADMIN_PASSWORD`
3. **Secret:** Gib ein sicheres Passwort ein, z.B.:
   ```
   pgadmin_secure_2024!
   ```
4. Klicke **"Add secret"**

✅ Secret erfolgreich erstellt!

#### Secret 4: STAGING_REDIS_PASSWORD

1. Klicke **"New repository secret"**
2. **Name:** `STAGING_REDIS_PASSWORD`
3. **Secret:** Gib ein sicheres Passwort ein, z.B.:
   ```
   redis_secure_2024!
   ```
4. Klicke **"Add secret"**

✅ Secret erfolgreich erstellt!

---

## ✅ Verifizierung

Nach dem Erstellen solltest du **4 Secrets** sehen:

```
Repository secrets (4)

Name                           Updated
STAGING_POSTGRES_PASSWORD      now
STAGING_KEYCLOAK_PASSWORD      now
STAGING_PGADMIN_PASSWORD       now
STAGING_REDIS_PASSWORD         now
```

**Screenshot-Beispiel:**
```
🔒 STAGING_POSTGRES_PASSWORD    Updated now    Edit    Remove
🔒 STAGING_KEYCLOAK_PASSWORD    Updated now    Edit    Remove
🔒 STAGING_PGADMIN_PASSWORD     Updated now    Edit    Remove
🔒 STAGING_REDIS_PASSWORD       Updated now    Edit    Remove
```

---

## 🔐 Passwort-Empfehlungen

### Sichere Passwörter generieren

**PowerShell (Windows):**
```powershell
# Generiere zufälliges 20-Zeichen-Passwort
-join ((48..57) + (65..90) + (97..122) | Get-Random -Count 20 | ForEach-Object {[char]$_})
```

**Linux/macOS:**
```bash
# Generiere zufälliges 20-Zeichen-Passwort
openssl rand -base64 20
```

**Online-Generator:**
- https://passwordsgenerator.net/
- Einstellungen: 20+ Zeichen, Groß-/Kleinbuchstaben, Zahlen, Sonderzeichen

### Beispiel-Passwörter (NICHT verwenden!)

```
# Diese Passwörter sind NUR Beispiele!
# Generiere eigene, sichere Passwörter!

STAGING_POSTGRES_PASSWORD=V@l30$taG!nG_DB_2024#Pass
STAGING_KEYCLOAK_PASSWORD=Ke7cL0ak_AdM!n$SecuR3
STAGING_PGADMIN_PASSWORD=pgAdm!n_V@l3o_2024#Secure
STAGING_REDIS_PASSWORD=R3d!s_C0mm@nd3r_S3cUr3
```

---

## 🧪 Secrets testen

### Option 1: Workflow manuell starten

1. Gehe zu: https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions/workflows/deploy-staging.yml
2. Klicke **"Run workflow"**
3. Branch: `develop` (oder aktueller Branch)
4. Klicke **"Run workflow"**

**Workflow startet:**
- Secrets werden automatisch geladen
- Deployment beginnt
- Logs zeigen ob Secrets korrekt sind

### Option 2: Push auf develop

```bash
git checkout develop
git add .
git commit -m "test: secrets configured"
git push origin develop
```

**Auto-Deployment startet:**
- Workflow läuft automatisch
- Secrets werden verwendet
- Status in Actions-Tab sichtbar

---

## 🐛 Troubleshooting

### Problem: "Secret not found"

**Symptom:**
```
Error: Required secret STAGING_POSTGRES_PASSWORD not found
```

**Lösung:**
1. Prüfe Secret-Name exakt (Case-Sensitive!)
2. Secret muss **Repository Secret** sein (nicht Environment Secret)
3. Warte 1-2 Minuten nach Erstellung (GitHub-Sync)
4. Workflow neu starten

### Problem: "Invalid authentication"

**Symptom:**
```
Error: FATAL: password authentication failed for user "valeo_staging"
```

**Lösung:**
1. Secret enthält falsches Passwort
2. Secret bearbeiten: **Edit** → Neues Passwort eingeben
3. Workflow neu starten

### Problem: "Access denied"

**Symptom:**
```
Error: You don't have permission to create secrets
```

**Lösung:**
- Du benötigst **Admin**- oder **Maintainer**-Rechte
- Kontaktiere Repository-Owner
- Alternative: Environment-Secrets (erfordert Approval)

---

## 🔒 Security-Best-Practices

### ✅ DO's

- ✅ **Sichere Passwörter generieren** (20+ Zeichen, Mix aus Buchstaben/Zahlen/Sonderzeichen)
- ✅ **Unterschiedliche Passwörter** für jedes Secret
- ✅ **Secrets regelmäßig rotieren** (alle 3-6 Monate)
- ✅ **GitHub Audit-Log überwachen** (wer hat Secrets geändert?)
- ✅ **2FA aktivieren** für GitHub-Account

### ❌ DON'Ts

- ❌ **NIEMALS Passwörter in Code committen**
- ❌ **NIEMALS Secrets in Logs ausgeben**
- ❌ **NIEMALS gleiche Passwörter für Staging + Production**
- ❌ **NIEMALS Secrets teilen via Email/Chat**
- ❌ **NIEMALS schwache Passwörter** (z.B. "admin123")

---

## 📊 Secret-Rotation (Optional)

### Automatische Rotation mit GitHub Actions

Das Repository hat bereits einen Workflow: `.github/workflows/rotate-secrets.yml`

**Aktivieren:**
1. Secrets mit Prefix `OLD_` erstellen
2. Workflow manuell starten
3. Secrets werden automatisch rotiert

**Schedule:**
- Empfohlen: Alle 3 Monate
- Kritisch: Alle 6 Monate

---

## 🔄 Secrets aktualisieren

### Vorhandenes Secret ändern

1. Gehe zu: https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/settings/secrets/actions
2. Finde das Secret in der Liste
3. Klicke **"Update"** (oder Stift-Icon)
4. Gib neues Passwort ein
5. Klicke **"Update secret"**

✅ Secret aktualisiert!

### Secret löschen

1. Gehe zu Secrets-Seite
2. Finde das Secret
3. Klicke **"Remove"**
4. Bestätige Löschung

⚠️ **Warnung:** Workflow schlägt fehl, wenn Secret fehlt!

---

## 📝 Checkliste

Nach dem Setup solltest du:

- [ ] **4 Secrets erstellt** (POSTGRES, KEYCLOAK, PGADMIN, REDIS)
- [ ] **Sichere Passwörter verwendet** (20+ Zeichen)
- [ ] **Secrets verifiziert** (in GitHub UI sichtbar)
- [ ] **Test-Workflow gestartet** (manuell oder via Push)
- [ ] **Workflow-Logs geprüft** (keine "Secret not found"-Fehler)

---

## 🎯 Nächste Schritte

Nach erfolgreicher Secret-Konfiguration:

### 1. Ersten Deployment-Test

```bash
# Push auf develop triggert Auto-Deploy
git checkout develop
git add .
git commit -m "feat: secrets configured, ready for staging"
git push origin develop
```

### 2. Workflow überwachen

**Actions-Dashboard:**
https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions

**Erwartete Jobs:**
1. ✅ Build & Test (~10 min)
2. ✅ Security Scan (~5 min)
3. ✅ Deploy (~5 min)
4. ✅ Smoke Tests (~3 min)
5. ✅ Notify (~1 min)

**Total:** ~24 Minuten

### 3. Staging-Umgebung testen

Nach erfolgreichem Deployment:

```bash
# Lokal auf Staging zugreifen (falls Windows-Deployment)
# Frontend: http://localhost:3001
# Login: test-admin / Test123!

# API-Test
curl http://localhost:8001/healthz
```

---

## 📞 Support

Bei Problemen:

1. **GitHub Actions Logs prüfen:**
   https://github.com/JochenWeerda/VALEO-NeuroERP-3.0/actions

2. **Dokumentation lesen:**
   - [GITHUB-ACTIONS-STAGING-SETUP.md](./GITHUB-ACTIONS-STAGING-SETUP.md)
   - [STAGING-DEPLOYMENT.md](./STAGING-DEPLOYMENT.md)

3. **Troubleshooting-Guide:**
   Siehe Abschnitt "Troubleshooting" oben

---

**Status:** 🔐 **SECRETS EINRICHTEN - SCHRITT-FÜR-SCHRITT**

**Nächster Schritt:** Workflow starten und Deployment testen! 🚀

