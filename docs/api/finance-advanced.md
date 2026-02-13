# Finance Advanced API Documentation

## Overview
Diese Dokumentation beschreibt die erweiterten Finance-Endpunkte für Wechselkurse, Buchungsschemata, Kostenrechnung, Abschlusschecklisten, Nebenbuch-Abstimmung und Intercompany-Buchungen.

---

## 1. Wechselkurse & Fremdwährung

### FXLoader - EZB Integration
Das System unterstützt automatische Wechselkursabholung von der Europäischen Zentralbank (EZB).

**Unterstützte Quellen:**
- `EZB`: Europäische Zentralbank (täglich + historisch)
- `MANUELL`: Manueller Import
- `CSV`: CSV-Upload

### 1.0 EZB Kurse importieren
**POST** `/api/finance/wechselkurse/ezb/import`

**Query Parameters:**
- `historic` (optional): Wenn `true`, lade historische Daten (letzte 90 Tage)
- `days` (optional): Anzahl Tage für historischen Import (default: 90)

**Response (200):**
```json
{
  "message": "EZB rates imported",
  "count": 28,
  "source": "EZB",
  "historic": false
}
```

### 1.0.1 Währung konvertieren
**POST** `/api/finance/wechselkurse/convert`

**Query Parameters:**
- `betrag`: Zu konvertierender Betrag
- `waehrung_von`: Quellwährung (ISO 4217)
- `waehrung_nach`: Zielwährung (ISO 4217)

**Response (200):**
```json
{
  "betrag": 1000,
  "waehrung_von": "USD",
  "waehrung_nach": "EUR",
  "ergebnis": 920.0,
  "kurs_datum": "2026-02-12"
}
```

### 1.1 Wechselkurs erstellen
**POST** `/api/finance/wechselkurse`

**Request Body:**
```json
{
  "waehrung_von": "USD",
  "waehrung_nach": "EUR",
  "kurs": 0.92,
  "kurs_datum": "2026-02-12",
  "quelle": "EZB"
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "tenant_id": "tenant-uuid",
  "waehrung_von": "USD",
  "waehrung_nach": "EUR",
  "kurs": 0.92,
  "kurs_datum": "2026-02-12",
  "quelle": "EZB",
  "created_at": "2026-02-12T06:00:00Z"
}
```

### 1.2 Liste Wechselkurse
**GET** `/api/finance/wechselkurse`

**Query Parameters:**
- `waehrung` (optional): Filter nach Währung
- `von_datum` (optional): Start-Datum
- `bis_datum` (optional): End-Datum

**Response (200):**
```json
[
  {
    "id": "uuid",
    "waehrung_von": "USD",
    "waehrung_nach": "EUR",
    "kurs": 0.92,
    "kurs_datum": "2026-02-12"
  }
]
```

---

## 2. Buchungsschemata

### 2.1 Buchungsschema erstellen
**POST** `/api/finance/buchungsschemata`

**Request Body:**
```json
{
  "name": "Eingangsrechnung Standard",
  "beschreibung": "Standard-Buchungsschema für ER",
  "belegart": "ER",
  "soll_konto_schema": "6000",
  "haben_konto_schema": "4400",
  "steuer_code": "VORSTEUER",
  "steuer_satz": 19.0,
  "aktiv": true,
  "prioritaet": 10
}
```

### 2.2 Buchungsvorschlag generieren
**POST** `/api/finance/buchungsschemata/vorschlag`

**Request Body:**
```json
{
  "belegart": "ER",
  "betrag": 1000.00,
  "text": "Testrechnung Lieferant A",
  "partner_id": "LIEFERANT-001"
}
```

**Response (200):**
```json
{
  "belegnr": "BV-2026-0001",
  "datum": "2026-02-12",
  "text": "Testrechnung Lieferant A",
  "betrag": 1000.00,
  "soll_konto": "6000",
  "haben_konto": "4400",
  "steuer_code": "VORSTEUER",
  "steuer_betrag": 190.00,
  "konfidenz": 0.85
}
```

---

## 3. Kostenrechnung

### 3.1 Kostenstelle erstellen
**POST** `/api/finance/kostenstellen`

**Request Body:**
```json
{
  "nummer": "KS-100",
  "bezeichnung": "Produktion Hauptwerk",
  "kostenstelle_art": "KOSTENSTELLE",
  "uebergeordnet": "parent-uuid",
  "verantwortlicher": "Max Mustermann",
  "budget": 50000.00,
  "budget_periode": "MONAT",
  "aktiv": true
}
```

### 3.2 Kostenstellen-Report
**GET** `/api/finance/kostenstellen/report`

**Query Parameters:**
- `von`: Start-Datum (YYYY-MM-DD)
- `bis`: End-Datum (YYYY-MM-DD)

**Response (200):**
```json
{
  "periode_von": "2026-01-01",
  "periode_bis": "2026-01-31",
  "gesamt_budget": 150000.00,
  "gesamt_verbraucht": 125000.00,
  "gesamt_offen": 25000.00,
  "kostenstellen": [...],
  "auswertungen": [...]
}
```

---

## 4. Abschlusschecklisten

### 4.1 Checkliste erstellen
**POST** `/api/finance/checklisten`

**Request Body:**
```json
{
  "periode": "2026-01",
  "abschluss_art": "MONATLICH",
  "verantwortlicher": "Max Mustermann",
  "items": [
    {
      "id": "1",
      "name": "Alle Belege gebucht",
      "status": "OFFEN",
      "bearbeiter": null,
      "datum": null,
      "bemerkung": null
    }
  ]
}
```

### 4.2 Checklisten-Item aktualisieren
**PUT** `/api/finance/checklisten/{id}/items/{item_id}`

**Request Body:**
```json
{
  "item_id": "1",
  "status": "ERLEDIGT",
  "bearbeiter": "Max Mustermann",
  "bemerkung": "Erledigt am 12.02.2026"
}
```

### 4.3 Checkliste abschließen
**PUT** `/api/finance/checklisten/{id}`

**Request Body:**
```json
{
  "status": "ABGESCHLOSSEN",
  "abschluss_datum": "2026-02-12"
}
```

---

## 5. Nebenbuch-Abstimmung

### 5.1 Abstimmung erstellen
**POST** `/api/finance/abstimmung/nebenbuch`

**Request Body:**
```json
{
  "abstimmungs_datum": "2026-02-12",
  "buchungskreis": "DE01"
}
```

### 5.2 Abstimmung ausführen
**POST** `/api/finance/abstimmung/nebenbuch/{id}/ausfuehren`

**Response (200):**
```json
{
  "message": "Abstimmung ausgeführt",
  "id": "uuid",
  "differenz": 0.00,
  "nebenbuch_saldo": 100000.00,
  "hauptbuch_saldo": 100000.00,
  "nicht_abgestimmte": []
}
```

---

## 6. Intercompany-Buchungen

### 6.1 Intercompany-Buchung erstellen
**POST** `/api/finance/intercompany`

**Request Body:**
```json
{
  "gesellschaft_von": "DE01",
  "gesellschaft_nach": "AT01",
  "belegnr": "IC-2026-0001",
  "datum": "2026-02-12",
  "betrag": 10000.00,
  "waehrung": "EUR",
  "wechselkurs": 1.0,
  "konto_von": "1400",
  "konto_nach": "2400",
  "referenz": "Interne Verrechnung Q1"
}
```

### 6.2 Gegenbuchung erstellen
**POST** `/api/finance/intercompany/{id}/gegenbuchung`

**Response (200):**
```json
{
  "message": "Gegenbuchung erstellt",
  "original_id": "uuid-original",
  "gegenbuchung_id": "uuid-gegen"
}
```

### 6.3 Intercompany-Salden
**GET** `/api/finance/intercompany/salden`

**Query Parameters:**
- `gesellschaft`: Company Code

**Response (200):**
```json
[
  {
    "gesellschaft": "DE01",
    "partner_gesellschaft": "AT01",
    "waehrung": "EUR",
    "saldo": 50000.00,
    "faelligkeiten": [...]
  }
]
```

---

## Fehlercodes

| Code | Beschreibung |
|------|--------------|
| 400 | Ungültige Anfrage |
| 401 | Nicht autorisiert |
| 403 | Keine Berechtigung |
| 404 | Nicht gefunden |
| 422 | Validierungsfehler |
| 500 | Interner Serverfehler |

---

## Authentication

Alle Endpunkte erfordern einen Bearer Token im Header:
```
Authorization: Bearer <token>
```

---

## Version

**API Version:** 1.0.0  
**Last Updated:** 2026-02-12
