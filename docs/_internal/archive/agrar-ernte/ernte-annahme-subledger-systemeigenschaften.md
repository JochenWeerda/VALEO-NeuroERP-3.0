# Subledger-Systemeigenschaften – Workflow & Konfiguration

**Erstellt:** 2026-02-18  
**Kontext:** Kreditorische Debitoren, Jahresabschluss, Geschäftsmodell → Subledger-Mapping

---

## 1. Hintergrund: Kreditorische Debitoren

**Buchhalterischer Standard:** Kreditorische Debitoren (Debitoren mit Haben-Saldo) werden zum Stichtag aus dem Forderungsausweis herausgenommen und als Verbindlichkeit / erhaltene Anzahlungen / Guthaben ausgewiesen – i. d. R. im neuen Jahr wieder zurückgedreht.

**ERP-Anforderung:** Diese Logik soll im Subledger-Modell abgebildet werden – ohne Excel-Handarbeit.

---

## 2. Geschäftsmodell → Subledger-Mapping

### A) Ankauf bei Anlieferung (PTBF) ✅

| Aspekt | Wert |
|--------|------|
| **acceptance_mode** | `PURCHASE_AT_DELIVERY_PTBF` |
| **ownership_type** | `OWN_STOCK` |
| **USt** | Vorsteuer bei Anlieferung begründbar (Leistungsbezug + Gutschrift) |
| **Gutschrift** | Self-Billing-Gutschrift (ggf. vorläufig, später Korrektur) |
| **Subledger** | `AP / PRODUCER_CLEARING` (Saldo = Verbindlichkeit) |

### B) Echte Einlagerung / Fremdware ❌

| Aspekt | Wert |
|--------|------|
| **acceptance_mode** | `STORAGE_ONLY` |
| **ownership_type** | `THIRD_PARTY_STOCK` |
| **USt** | Keine Ankauf-Gutschrift mit Vorsteuer (Lieferung noch nicht erfolgt) |
| **Gutschrift** | Keine |
| **Subledger** | `STORAGE` |

### C) Einlagerung + Anzahlung

| Aspekt | Wert |
|--------|------|
| **acceptance_mode** | `ADVANCE_ON_STORAGE` |
| **ownership_type** | `THIRD_PARTY_STOCK` (oder OWN bei Zahlung) |
| **USt** | Nur nach Zahlung + Rechnung/Gutschrift |
| **Subledger** | `ADVANCE_PAYMENTS` / `STORAGE` |

---

## 3. Subledger-Buckets (Systemeigenschaften)

| Bucket-Code | Bezeichnung | Beschreibung | Hauptkonto (SKR03) |
|-------------|-------------|--------------|--------------------|
| `AP` / `PRODUCER_CLEARING` | Rohwaren-Verbindlichkeit | Stehen gelassene Gutschriften aus Ernte-Annahme | 1400 (Debitoren-Sammel) |
| `SETTLEMENT` / `VERRECHNUNG` | Erzeuger-Verrechnung | Stehen gelassene Gutschriften, Verrechnungen | 1400 |
| `STORAGE` | Fremdware Lager | Nur bei echtem Fremdware-Einlagerung | 3300 o. ä. |
| `AR` | Betriebsmittel-Forderungen | Forderungen an Erzeuger (Dünger, Saatgut) | 1400 |
| `ADVANCE_PAYMENTS` | Erhaltene Anzahlungen | Anzahlungen von Erzeugern | 1415 |
| `INTEREST` | Zinsen | Zinsen auf stehende Salden | 2690 o. ä. |

---

## 4. Konten-Mapping (1400 / 1415)

| Systemeigenschaft | Wert (Beispiel) | Bedeutung |
|-------------------|-----------------|-----------|
| `SUBLEDGER_AR_ACCOUNT` | 1400 | Debitoren-Sammelkonto (Forderungen) |
| `SUBLEDGER_CREDITOR_DEBITOR_ACCOUNT` | 1415 | Erhaltene Anzahlungen / Guthaben (kreditorische Debitoren) |
| `SUBLEDGER_STORAGE_ACCOUNT` | 3300 | Fremdware Lager |
| `SUBLEDGER_AP_PRODUCER_ACCOUNT` | 1600 | Verbindlichkeiten aus Lieferungen (Kreditoren) |

---

## 5. Feature: Stichtags-Umgliederung

### Input

| Parameter | Typ | Beschreibung |
|-----------|-----|--------------|
| `stichtag` | date | Stichtag (z. B. 31.12.) |
| `scope` | enum | Nur Partner mit Typ „Erzeuger-Settlement“ oder Tag „Einlagerungskonto“ |
| `zielkonten_mapping` | mapping | AR-Sammelkonto → Erhaltene Anzahlungen |
| `aggregation` | enum | `aggregiert` (eine Summe) oder `je_partner` |

### Output

1. **Report** – Saldenliste (nur Haben-Salden ≠ 0) als PDF/CSV
2. **Journal Entry** – Belegdatum = Stichtag, automatisch nummeriert
3. **Optional** – Automatische Rückbuchung am 01.01.

**Hinweis:** Die Umgliederung ist nur Darstellung; OP im Subledger bleiben unverändert.

---

## 6. Systemeigenschaften-Tabelle (DB-Schema)

```sql
CREATE TABLE domain_shared.system_properties (
  id VARCHAR PRIMARY KEY,
  tenant_id VARCHAR NOT NULL REFERENCES domain_shared.tenants(id),
  property_key VARCHAR(100) NOT NULL,
  property_value TEXT,
  property_type VARCHAR(20) DEFAULT 'string',
  category VARCHAR(50) DEFAULT 'subledger',
  description TEXT,
  CONSTRAINT uq_system_properties_tenant_key UNIQUE (tenant_id, property_key)
);
```

Migration: `alembic/versions/add_system_properties_subledger_20260218.py`

### Seed-Daten (Beispiel)

| property_key | property_value | category | description |
|--------------|----------------|----------|-------------|
| `SUBLEDGER_AR_ACCOUNT` | 1400 | subledger | Debitoren-Sammelkonto |
| `SUBLEDGER_CREDITOR_DEBITOR_ACCOUNT` | 1415 | subledger | Erhaltene Anzahlungen / Guthaben |
| `SUBLEDGER_STORAGE_ACCOUNT` | 3300 | subledger | Fremdware Lager |
| `SUBLEDGER_AP_PRODUCER_ACCOUNT` | 1600 | subledger | Verbindlichkeiten Rohwaren |
| `STICHTAG_UMGLIEDERUNG_ENABLED` | true | year_end | Stichtags-Umgliederung aktiv |
| `STICHTAG_UMGLIEDERUNG_AUTO_REVERSAL` | false | year_end | Rückbuchung 01.01. automatisch |
| `ACCEPTANCE_MODE_DEFAULT` | PURCHASE_AT_DELIVERY_PTBF | harvest | Default Geschäftsmodell |

---

## 7. Workflow-Empfehlung

1. **Ernte-Annahme** mit Feld „Geschäftsmodell“ steuert:
   - Erzeugung Gutschrift (ja/nein)
   - OWN_STOCK vs. THIRD_PARTY_STOCK
   - Ziel-Subledger (AP, STORAGE, ADVANCE_PAYMENTS)
2. **Subledger-Salden** je Business Partner sichtbar (SETTLEMENT, STORAGE, AR, AP, INTEREST)
3. **Stichtags-Umgliederung** als Button statt Excel – Report + Journal Entry
4. **Keine doppelten Stammdaten** – 1 Business Partner, mehrere Subledger-Buckets

---

## Referenzen

- [Landesportal Sachsen-Anhalt – Bilanzierung kreditorische Debitoren](https://mi.sachsen-anhalt.de/...)
- [UStH §15 – Vorsteuerabzug](https://usth.bundesfinanzministerium.de/...)
- [NWB – Umgliederung kreditorischer Debitoren](https://datenbank.nwb.de/...)
