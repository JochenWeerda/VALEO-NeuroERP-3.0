# GDPR Compliance Documentation

## Überblick

VALEO-NeuroERP implementiert GDPR-konforme Datenschutzmaßnahmen gemäß EU-DSGVO (Regulation 2016/679).

## Implementierte Rechte

### 1. Recht auf Auskunft (Art. 15)

**Endpoint:** `GET /api/gdpr/export/{user_id}`

Exportiert alle personenbezogenen Daten eines Users:
- Audit-Trail-Einträge
- Erstellte Dokumente
- Archiv-Einträge

**Scope:** `gdpr:export`

### 2. Recht auf Löschung (Art. 17)

**Endpoint:** `DELETE /api/gdpr/erase/{user_id}`

Anonymisiert alle personenbezogenen Daten eines Users:
- User-IDs in `workflow_audit` → `DELETED`
- User-IDs in `archive_index` → `DELETED`
- User-IDs in `documents_header.created_by` → `DELETED`

**Scope:** `gdpr:erase` (Admin-only)

**Hinweis:** Vollständige Löschung ist aus Compliance-Gründen (Aufbewahrungspflichten) nicht möglich. Stattdessen wird eine Anonymisierung durchgeführt.

## PII-Redaction in Logs

### Implementierung

`app/core/logging.py` - `PIIRedactionFilter`

### Redaktierte Felder

- `token`, `password`, `secret`, `api_key` → `***`
- `Bearer {token}` → `Bearer ***`
- E-Mail-Adressen → `***@domain.com`

### Beispiel

```python
logger.info(f"User login: token={token}")
# Output: User login: token=***
```

## Data Processing Impact Assessment (DPIA)

### Verarbeitungszwecke

1. **Dokumenten-Management:** Speicherung von Belegen (Angebote, Aufträge, Rechnungen)
2. **Workflow-Audit:** Nachvollziehbarkeit von Freigaben und Änderungen
3. **Archivierung:** Langzeitarchivierung für rechtliche Aufbewahrungspflichten

### Rechtsgrundlagen

- **Art. 6 (1) b DSGVO:** Vertragserfüllung
- **Art. 6 (1) c DSGVO:** Rechtliche Verpflichtung (Aufbewahrungspflichten)
- **Art. 6 (1) f DSGVO:** Berechtigtes Interesse (Audit-Trail)

### Risiken & Maßnahmen

| Risiko | Maßnahme |
|--------|----------|
| Unbefugter Zugriff | RBAC mit granularen Scopes |
| Datenlecks in Logs | PII-Redaction-Filter |
| Fehlende Löschung | GDPR-Erase-Endpoint |
| Datenexport | GDPR-Export-Endpoint |

## Aufbewahrungsfristen

- **Dokumente:** 10 Jahre (§ 147 AO, § 257 HGB)
- **Audit-Trail:** 10 Jahre
- **Archive:** 10 Jahre

Nach Ablauf: Automatische Anonymisierung via Cronjob.

## Technische & Organisatorische Maßnahmen (TOMs)

### Technisch

- [x] Verschlüsselung in Transit (TLS 1.3)
- [x] Verschlüsselung at Rest (PostgreSQL Encryption)
- [x] RBAC mit granularen Scopes
- [x] PII-Redaction in Logs
- [x] Rate-Limiting (DDoS-Schutz)
- [x] Security-Scanning (OWASP ZAP, Trivy)

### Organisatorisch

- [x] DPIA durchgeführt
- [x] Datenschutzerklärung vorhanden
- [x] Auftragsverarbeitungsverträge (AVV) mit Cloud-Providern
- [x] Incident-Response-Plan
- [x] Regelmäßige Security-Audits

## Meldepflichten

Bei Datenschutzverletzungen (Art. 33, 34 DSGVO):

1. **Intern:** Sofortige Meldung an Datenschutzbeauftragten
2. **Behörde:** Meldung an Aufsichtsbehörde innerhalb 72h
3. **Betroffene:** Benachrichtigung bei hohem Risiko

## Kontakt

**Datenschutzbeauftragter:** datenschutz@valeo-erp.com

**Aufsichtsbehörde:** [Zuständige Landesdatenschutzbehörde]

---

**Letzte Aktualisierung:** 2025-10-09

**Version:** 1.0

