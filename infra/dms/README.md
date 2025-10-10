***REMOVED*** Mayan-DMS Infrastructure für VALEO-NeuroERP

**Ein-Befehl-Setup** für Mayan-DMS als eigener Docker-Stack mit VALEO-NeuroERP-Preset.

---

***REMOVED******REMOVED*** 🚀 Quick-Start

***REMOVED******REMOVED******REMOVED*** 1. Konfiguration vorbereiten

```bash
cd infra/dms

***REMOVED*** .env erstellen
cp env.example .env

***REMOVED*** Pfade anpassen (optional)
vim .env
```

**Wichtige Variablen:**
- `DMS_MEDIA_PATH` - Wo Dokumente gespeichert werden
- `DMS_HTTP_PORT` - Port für Mayan-UI (default: 8010)
- `DMS_BOOTSTRAP_TOKEN` - Wird später eingetragen

***REMOVED******REMOVED******REMOVED*** 2. Mayan starten

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
***REMOVED*** Health-Check
docker compose -f docker-compose.mayan.yml ps

***REMOVED*** Logs anschauen
docker compose -f docker-compose.mayan.yml logs -f mayan
```

***REMOVED******REMOVED******REMOVED*** 3. API-Token erstellen (einmalig)

1. **Browser öffnen:** http://localhost:8010
2. **Login:** 
   - Username: `admin`
   - Password: `admin` (beim ersten Start)
3. **Passwort ändern** (wird beim ersten Login gefordert)
4. **API-Token erstellen:**
   - Einstellungen (⚙️) → API-Token
   - Button "Neues Token erstellen"
   - Token kopieren (z.B. `REDACTED_TOKEN789...`)
5. **In .env eintragen:**
   ```bash
   vim .env
   ***REMOVED*** DMS_BOOTSTRAP_TOKEN=REDACTED_TOKEN789...
   ```

***REMOVED******REMOVED******REMOVED*** 4. Bootstrap ausführen

```bash
***REMOVED*** Ausführbar machen (Linux/Mac)
chmod +x bin/*.sh

***REMOVED*** Bootstrap ausführen
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

***REMOVED******REMOVED******REMOVED*** 5. Idempotenz testen

```bash
***REMOVED*** Nochmal ausführen → sollte nichts mehr erstellen
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

***REMOVED******REMOVED*** 🔧 Konfiguration

***REMOVED******REMOVED******REMOVED*** .env-Variablen

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

***REMOVED******REMOVED******REMOVED*** bootstrap.json

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

***REMOVED******REMOVED*** 🔄 Management

***REMOVED******REMOVED******REMOVED*** Mayan stoppen
```bash
docker compose -f docker-compose.mayan.yml down
```

***REMOVED******REMOVED******REMOVED*** Mayan neustarten
```bash
docker compose -f docker-compose.mayan.yml restart
```

***REMOVED******REMOVED******REMOVED*** Logs anschauen
```bash
docker compose -f docker-compose.mayan.yml logs -f mayan
```

***REMOVED******REMOVED******REMOVED*** Mayan aktualisieren
```bash
docker compose -f docker-compose.mayan.yml pull
docker compose -f docker-compose.mayan.yml up -d
```

***REMOVED******REMOVED******REMOVED*** Backup erstellen
```bash
***REMOVED*** PostgreSQL-Backup
docker exec mayan-postgres pg_dump -U mayan mayan > backup_mayan_$(date +%Y%m%d).sql

***REMOVED*** Media-Backup
tar czf backup_media_$(date +%Y%m%d).tar.gz data/mayan/media
```

---

***REMOVED******REMOVED*** 🔗 ERP-Integration

***REMOVED******REMOVED******REMOVED*** ENV-Variable für ERP-Backend

```bash
***REMOVED*** In VALEO-NeuroERP .env
export DMS_BASE=http://localhost:8010
export DMS_TOKEN=REDACTED_TOKEN...
```

***REMOVED******REMOVED******REMOVED*** Auto-Upload nach PDF-Generierung

**Bereits implementiert in:** `app/routers/print_router.py`

```python
***REMOVED*** Nach PDF-Generierung
if is_dms_configured():
    upload_document(domain, doc_id, str(pdf_path), metadata)
```

***REMOVED******REMOVED******REMOVED*** Admin-UI Integration

**Bereits implementiert:** `packages/frontend-web/src/pages/admin/setup/dms-integration.tsx`

**Navigation:**
1. VALEO-NeuroERP öffnen
2. Admin → Ersteinrichtung
3. Card "Mayan-DMS integrieren"
4. Button "Jetzt einrichten"

---

***REMOVED******REMOVED*** 🧪 Testing

***REMOVED******REMOVED******REMOVED*** 1. Mayan erreichbar?
```bash
curl http://localhost:8010/api/
***REMOVED*** Expected: {"detail": "Authentication credentials were not provided."}
```

***REMOVED******REMOVED******REMOVED*** 2. Bootstrap erfolgreich?
```bash
cat data/mayan/postgres/.initialized  ***REMOVED*** Sollte existieren
```

***REMOVED******REMOVED******REMOVED*** 3. Document Types vorhanden?
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

***REMOVED******REMOVED******REMOVED*** 4. PDF-Upload testen
```bash
***REMOVED*** Via VALEO-ERP API
curl http://localhost:8000/api/documents/sales_order/SO-00001/print \
  -H "Authorization: Bearer $TOKEN"

***REMOVED*** Im Mayan-UI prüfen
open http://localhost:8010
***REMOVED*** → Dokumente → SO-00001 sollte sichtbar sein
```

---

***REMOVED******REMOVED*** 📁 Verzeichnis-Struktur

```
infra/dms/
├── env.example              ***REMOVED*** Template für .env
├── .env                     ***REMOVED*** Deine Config (nicht in Git!)
├── docker-compose.mayan.yml ***REMOVED*** Docker-Stack
├── config/
│   └── bootstrap.json       ***REMOVED*** VALEO-Preset
├── bin/
│   ├── wait-for-http.sh     ***REMOVED*** Health-Check-Helper
│   └── bootstrap.sh         ***REMOVED*** Bootstrap-Script
└── data/                    ***REMOVED*** Wird automatisch erstellt
    └── mayan/
        ├── media/           ***REMOVED*** Dokumente
        ├── settings/        ***REMOVED*** Mayan-Settings
        └── postgres/        ***REMOVED*** PostgreSQL-Daten
```

---

***REMOVED******REMOVED*** 🔒 Security

***REMOVED******REMOVED******REMOVED*** Production-Empfehlungen

1. **Passwörter ändern:**
   ```bash
   ***REMOVED*** In .env
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

***REMOVED******REMOVED*** 🆘 Troubleshooting

***REMOVED******REMOVED******REMOVED*** Problem: Bootstrap schlägt fehl mit "Authentication failed"

**Ursache:** DMS_BOOTSTRAP_TOKEN falsch oder abgelaufen

**Lösung:**
1. Neues Token im Mayan-UI erstellen
2. In .env eintragen
3. Bootstrap nochmal ausführen

***REMOVED******REMOVED******REMOVED*** Problem: "curl: (7) Failed to connect"

**Ursache:** Mayan noch nicht bereit

**Lösung:**
```bash
***REMOVED*** Logs prüfen
docker compose -f docker-compose.mayan.yml logs mayan

***REMOVED*** Warte länger
bin/wait-for-http.sh http://localhost:8010/api/ 180
```

***REMOVED******REMOVED******REMOVED*** Problem: "Permission denied" bei bootstrap.sh

**Ursache:** Script nicht ausführbar

**Lösung:**
```bash
chmod +x bin/*.sh
```

***REMOVED******REMOVED******REMOVED*** Problem: Dokumente nicht im DMS sichtbar

**Ursache:** Auto-Upload fehlgeschlagen oder DMS_TOKEN nicht gesetzt

**Lösung:**
```bash
***REMOVED*** ENV prüfen
echo $DMS_TOKEN

***REMOVED*** Backend-Logs prüfen
tail -f logs/valeo-erp.log | grep DMS
```

---

***REMOVED******REMOVED*** 📊 Warum diese Struktur?

***REMOVED******REMOVED******REMOVED*** ✅ Trennung der Zuständigkeiten
- **Mayan:** Eigener Stack (Updates, OCR-Worker, DB-Backups)
- **ERP:** Nur leichter Adapter (REST-API)

***REMOVED******REMOVED******REMOVED*** ✅ Reproduzierbar
- Volle Einrichtung per `bootstrap.json`
- Änderungen versionierbar in Git
- Idempotent (mehrfach ausführbar)

***REMOVED******REMOVED******REMOVED*** ✅ Portabel
- **Lokal:** Docker-Compose
- **Production:** Helm-Chart (analog zu VALEO-ERP)
- Scripts bleiben gleich

***REMOVED******REMOVED******REMOVED*** ✅ Sicher
- Token nie in Config gespeichert
- ENV-basierte Konfiguration
- Admin-only Zugriff

---

***REMOVED******REMOVED*** 🔄 Next Steps

***REMOVED******REMOVED******REMOVED*** Für Production:

1. **Helm-Chart erstellen:**
   ```bash
   ***REMOVED*** Analog zu k8s/helm/valeo-erp
   k8s/helm/mayan-dms/
   ```

2. **Backups automatisieren:**
   ```bash
   ***REMOVED*** Cronjob für PostgreSQL-Backup
   0 2 * * * docker exec mayan-postgres pg_dump ...
   ```

3. **Monitoring integrieren:**
   - Prometheus-Exporter für Mayan
   - Grafana-Dashboard
   - Alerts bei Fehler

---

**🎉 Ein-Befehl-Setup für Mayan-DMS! 🚀**

