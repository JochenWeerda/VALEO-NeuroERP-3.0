# Mayan-DMS Infrastructure für VALEO-NeuroERP

**Ein-Befehl-Setup** für Mayan-DMS als eigener Docker-Stack mit VALEO-NeuroERP-Preset.

---

## 🚀 Quick-Start

### 1. Konfiguration vorbereiten

```bash
cd infra/dms

# .env erstellen
cp env.example .env

# Pfade anpassen (optional)
vim .env
```

**Wichtige Variablen:**
- `DMS_MEDIA_PATH` - Wo Dokumente gespeichert werden
- `DMS_HTTP_PORT` - Port für Mayan-UI (default: 8010)
- `DMS_BOOTSTRAP_TOKEN` - Wird später eingetragen

### 2. Mayan starten

```bash
docker compose -f docker-compose.mayan.yml up -d
```

**Enthält:**
- Mayan-DMS (Hauptanwendung)
- PostgreSQL 15 (Database)
- Redis (Cache)
- Mayan-Worker (OCR, Background-Tasks)

**Warte bis bereit:**
```bash
# Health-Check
docker compose -f docker-compose.mayan.yml ps

# Logs anschauen
docker compose -f docker-compose.mayan.yml logs -f mayan
```

### 3. API-Token erstellen (einmalig)

1. **Browser öffnen:** http://localhost:8010
2. **Login:** 
   - Username: `admin`
   - Password: `admin` (beim ersten Start)
3. **Passwort ändern** (wird beim ersten Login gefordert)
4. **API-Token erstellen:**
   - Einstellungen (⚙️) → API-Token
   - Button "Neues Token erstellen"
   - Token kopieren (z.B. `abc123def456789...`)
5. **In .env eintragen:**
   ```bash
   vim .env
   # DMS_BOOTSTRAP_TOKEN=abc123def456789...
   ```

### 4. Bootstrap ausführen

```bash
# Ausführbar machen (Linux/Mac)
chmod +x bin/*.sh

# Bootstrap ausführen
bin/bootstrap.sh
```

**Output:**
```
🚀 VALEO-NeuroERP Mayan-DMS Bootstrap
Base-URL: http://localhost:8010
Config: config/bootstrap.json

⏳ Waiting for Mayan to be ready...
✅ http://localhost:8010/api/ is ready!

📄 Creating Document Types...
Creating document type: sales_order
Creating document type: delivery
...
✅ Document Types: 7 total, 7 created

🏷️  Creating Metadata Types...
Creating metadata type: number
Creating metadata type: domain
...
✅ Metadata Types: 7 total, 7 created

🔗 Creating Metadata Bindings...
Creating binding: invoice → number
Creating binding: invoice → domain
...
✅ Metadata Bindings: 42 created

ℹ️  OCR is active (languages: deu,eng)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✔ Mayan-DMS Bootstrap Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Summary:
  Document Types: 7 (7 created)
  Metadata Types: 7 (7 created)
  Bindings: 42 created

🎉 Mayan is ready for VALEO-NeuroERP integration!
```

### 5. Idempotenz testen

```bash
# Nochmal ausführen → sollte nichts mehr erstellen
bin/bootstrap.sh
```

**Expected Output:**
```
Document type already exists: sales_order
Metadata type already exists: number
...
✅ Document Types: 7 total, 0 created
✅ Metadata Types: 7 total, 0 created
✅ Metadata Bindings: 0 created
```

---

## 🔧 Konfiguration

### .env-Variablen

| Variable | Default | Beschreibung |
|----------|---------|--------------|
| DMS_MEDIA_PATH | ./data/mayan/media | Dokument-Speicherort |
| DMS_SETTINGS_PATH | ./data/mayan/settings | Mayan-Settings |
| DMS_PG_DATA | ./data/mayan/postgres | PostgreSQL-Daten |
| DMS_HTTP_PORT | 8010 | HTTP-Port für Mayan-UI |
| DMS_BASE | http://localhost:8010 | Base-URL für API |
| DMS_BOOTSTRAP_TOKEN | - | API-Token (aus Mayan-UI) |
| VALEO_BRAND | VALEO NeuroERP | Branding |
| POSTGRES_USER | mayan | PostgreSQL-User |
| POSTGRES_PASSWORD | mayan | PostgreSQL-Passwort |
| POSTGRES_DB | mayan | PostgreSQL-Datenbank |

### bootstrap.json

**Document Types (7):**
- sales_order
- delivery
- invoice
- purchase_order
- goods_receipt
- supplier_invoice
- contract

**Metadata Types (7):**
- number (Text, required)
- domain (Choice: sales/purchase/logistics/contract)
- customerId (Text)
- supplierId (Text)
- status (Choice: draft/pending/approved/posted/rejected)
- hash (Text)
- date (Date)

**Metadata-Bindings (42):**
- Jeder DocType hat passende Metadaten
- Beispiel: invoice → number, domain, customerId, status, hash, date

---

## 🔄 Management

### Mayan stoppen
```bash
docker compose -f docker-compose.mayan.yml down
```

### Mayan neustarten
```bash
docker compose -f docker-compose.mayan.yml restart
```

### Logs anschauen
```bash
docker compose -f docker-compose.mayan.yml logs -f mayan
```

### Mayan aktualisieren
```bash
docker compose -f docker-compose.mayan.yml pull
docker compose -f docker-compose.mayan.yml up -d
```

### Backup erstellen
```bash
# PostgreSQL-Backup
docker exec mayan-postgres pg_dump -U mayan mayan > backup_mayan_$(date +%Y%m%d).sql

# Media-Backup
tar czf backup_media_$(date +%Y%m%d).tar.gz data/mayan/media
```

---

## 🔗 ERP-Integration

### ENV-Variable für ERP-Backend

```bash
# In VALEO-NeuroERP .env
export DMS_BASE=http://localhost:8010
export DMS_TOKEN=abc123def456...
```

### Auto-Upload nach PDF-Generierung

**Bereits implementiert in:** `app/routers/print_router.py`

```python
# Nach PDF-Generierung
if is_dms_configured():
    upload_document(domain, doc_id, str(pdf_path), metadata)
```

### Admin-UI Integration

**Bereits implementiert:** `packages/frontend-web/src/pages/admin/setup/dms-integration.tsx`

**Navigation:**
1. VALEO-NeuroERP öffnen
2. Admin → Ersteinrichtung
3. Card "Mayan-DMS integrieren"
4. Button "Jetzt einrichten"

---

## 🧪 Testing

### 1. Mayan erreichbar?
```bash
curl http://localhost:8010/api/
# Expected: {"detail": "Authentication credentials were not provided."}
```

### 2. Bootstrap erfolgreich?
```bash
cat data/mayan/postgres/.initialized  # Sollte existieren
```

### 3. Document Types vorhanden?
```bash
curl -H "Authorization: Token $DMS_BOOTSTRAP_TOKEN" \
  http://localhost:8010/api/document_types/document_types/ | jq '.results[].label'
```

**Expected:**
```
"sales_order"
"delivery"
"invoice"
...
```

### 4. PDF-Upload testen
```bash
# Via VALEO-ERP API
curl http://localhost:8000/api/documents/sales_order/SO-00001/print \
  -H "Authorization: Bearer $TOKEN"

# Im Mayan-UI prüfen
open http://localhost:8010
# → Dokumente → SO-00001 sollte sichtbar sein
```

---

## 📁 Verzeichnis-Struktur

```
infra/dms/
├── env.example              # Template für .env
├── .env                     # Deine Config (nicht in Git!)
├── docker-compose.mayan.yml # Docker-Stack
├── config/
│   └── bootstrap.json       # VALEO-Preset
├── bin/
│   ├── wait-for-http.sh     # Health-Check-Helper
│   └── bootstrap.sh         # Bootstrap-Script
└── data/                    # Wird automatisch erstellt
    └── mayan/
        ├── media/           # Dokumente
        ├── settings/        # Mayan-Settings
        └── postgres/        # PostgreSQL-Daten
```

---

## 🔒 Security

### Production-Empfehlungen

1. **Passwörter ändern:**
   ```bash
   # In .env
   POSTGRES_PASSWORD=<starkes-passwort>
   REDIS_PASSWORD=<starkes-passwort>
   ```

2. **TLS aktivieren:**
   - Nginx-Reverse-Proxy vor Mayan
   - Let's Encrypt-Zertifikat
   - HTTPS-Only

3. **Token-Management:**
   - Token in Kubernetes-Secret
   - Rotation alle 90 Tage
   - Logging bei Token-Nutzung

4. **Network-Isolation:**
   - Mayan in eigenem Docker-Network
   - Firewall-Regeln (nur Port 8010 erreichbar)

---

## 🆘 Troubleshooting

### Problem: Bootstrap schlägt fehl mit "Authentication failed"

**Ursache:** DMS_BOOTSTRAP_TOKEN falsch oder abgelaufen

**Lösung:**
1. Neues Token im Mayan-UI erstellen
2. In .env eintragen
3. Bootstrap nochmal ausführen

### Problem: "curl: (7) Failed to connect"

**Ursache:** Mayan noch nicht bereit

**Lösung:**
```bash
# Logs prüfen
docker compose -f docker-compose.mayan.yml logs mayan

# Warte länger
bin/wait-for-http.sh http://localhost:8010/api/ 180
```

### Problem: "Permission denied" bei bootstrap.sh

**Ursache:** Script nicht ausführbar

**Lösung:**
```bash
chmod +x bin/*.sh
```

### Problem: Dokumente nicht im DMS sichtbar

**Ursache:** Auto-Upload fehlgeschlagen oder DMS_TOKEN nicht gesetzt

**Lösung:**
```bash
# ENV prüfen
echo $DMS_TOKEN

# Backend-Logs prüfen
tail -f logs/valeo-erp.log | grep DMS
```

---

## 📊 Warum diese Struktur?

### ✅ Trennung der Zuständigkeiten
- **Mayan:** Eigener Stack (Updates, OCR-Worker, DB-Backups)
- **ERP:** Nur leichter Adapter (REST-API)

### ✅ Reproduzierbar
- Volle Einrichtung per `bootstrap.json`
- Änderungen versionierbar in Git
- Idempotent (mehrfach ausführbar)

### ✅ Portabel
- **Lokal:** Docker-Compose
- **Production:** Helm-Chart (analog zu VALEO-ERP)
- Scripts bleiben gleich

### ✅ Sicher
- Token nie in Config gespeichert
- ENV-basierte Konfiguration
- Admin-only Zugriff

---

## 🔄 Next Steps

### Für Production:

1. **Helm-Chart erstellen:**
   ```bash
   # Analog zu k8s/helm/valeo-erp
   k8s/helm/mayan-dms/
   ```

2. **Backups automatisieren:**
   ```bash
   # Cronjob für PostgreSQL-Backup
   0 2 * * * docker exec mayan-postgres pg_dump ...
   ```

3. **Monitoring integrieren:**
   - Prometheus-Exporter für Mayan
   - Grafana-Dashboard
   - Alerts bei Fehler

---

**🎉 Ein-Befehl-Setup für Mayan-DMS! 🚀**

