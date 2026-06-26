# Lieferschein-Erfassung: Test-Checkliste

## ✅ Implementierung abgeschlossen

### Backend
- ✅ Migration erstellt: `sales_delivery_notes_branches_audit_20260216.py`
- ✅ API-Endpunkte für Lieferscheine (`/api/v1/sales/delivery-notes`)
- ✅ API-Endpunkte für Niederlassungen (`/api/v1/admin/branches`)
- ✅ API-Endpunkt für Preisberechnung (`/api/v1/pricing/calculate`)

### Frontend
- ✅ Bediener aus Session geladen
- ✅ Vertreter aus Kunden-Stammdaten geladen
- ✅ MWSt. % automatisch aus Artikel-Stammdaten
- ✅ Attestierungs-Dialog implementiert
- ✅ API-Integration für Speichern und Drucken

## 🧪 Test-Schritte

### 1. Migration ausführen
```bash
# Im Backend-Container
docker exec valeo-neuro-erp-backend alembic upgrade head
```

**Erwartetes Ergebnis:**
- ✅ Schemas `domain_sales` und `domain_audit` werden erstellt
- ✅ Tabellen werden angelegt:
  - `domain_shared.branches`
  - `domain_sales.delivery_notes`
  - `domain_sales.delivery_note_positions`
  - `domain_audit.attestations`

### 2. Backend-API testen

#### 2.1 Niederlassungen
```bash
# Liste abrufen
curl http://localhost:8000/api/v1/admin/branches

# Neue Niederlassung erstellen
curl -X POST http://localhost:8000/api/v1/admin/branches \
  -H "Content-Type: application/json" \
  -d '{
    "branch_number": 0,
    "name": "Hauptniederlassung",
    "is_active": true
  }'
```

#### 2.2 Lieferschein erstellen
```bash
curl -X POST http://localhost:8000/api/v1/sales/delivery-notes \
  -H "Content-Type: application/json" \
  -d '{
    "customer_id": "KUNDEN-ID",
    "delivery_date": "2026-02-16",
    "delivery_time": "10:00:00",
    "status": "draft",
    "positionen": [
      {
        "pos_nr": 10,
        "artikel_nr": "ART-10001",
        "bezeichnung": "Test-Artikel",
        "menge": 10,
        "einheit": "Stk",
        "listenpreis": 100.00,
        "rabatt": 5,
        "mwst_prozent": 19
      }
    ]
  }'
```

**Erwartetes Ergebnis:**
- ✅ LS-Nr. wird automatisch generiert (Format: YYYYNNNNNN)
- ✅ Positionen werden gespeichert
- ✅ Totals werden berechnet

#### 2.3 Preisberechnung testen
```bash
curl "http://localhost:8000/api/v1/pricing/calculate?article_id=ARTIKEL-ID&customer_id=KUNDEN-ID&quantity=10"
```

**Erwartetes Ergebnis:**
- ✅ Hierarchische Preislogik (Staffelpreis → Vertragsrabatt → Kunden-Rabatt → Mitarbeiter-Rabatt → Basis-Preis)
- ✅ Nur EIN Rabatt wird angewendet (nicht additiv)

### 3. Frontend testen

#### 3.1 Lieferschein-Erfassung öffnen
```
http://localhost:3000/verkauf/lieferschein-erfassung
```

**Erwartetes Ergebnis:**
- ✅ Seite lädt ohne Fehler
- ✅ Bediener wird automatisch aus Session geladen
- ✅ Datum ist auf heute gesetzt
- ✅ LS-Nr. wird generiert (temporär, bis gespeichert)

#### 3.2 Kunde auswählen
1. Klick auf "..." bei Debitor-Kto.
2. Dialog öffnet sich
3. Kunde auswählen und OK

**Erwartetes Ergebnis:**
- ✅ Kundenadresse wird angezeigt
- ✅ Vertreter wird automatisch gesetzt
- ✅ Kredit-Limit wird angezeigt

#### 3.3 Artikel hinzufügen
1. Klick auf "..." bei Artikel-Nr. in Positions-Details
2. Dialog öffnet sich
3. Artikel suchen und auswählen

**Erwartetes Ergebnis:**
- ✅ Artikel-Felder werden gefüllt (Bezeichnung, Einheit, Listenpreis)
- ✅ MWSt. % wird automatisch aus Artikel-Stammdaten geladen

#### 3.4 Position bestätigen
1. Menge eingeben
2. "Zeile OK" klicken

**Erwartetes Ergebnis:**
- ✅ Position erscheint im Grid
- ✅ Summen werden aktualisiert (Netto, MWSt., Brutto)
- ✅ Nächste Position ist bereit (Pos-Nr. +10)

#### 3.5 Speichern
1. "Speichern" Button klicken

**Erwartetes Ergebnis:**
- ✅ Lieferschein wird gespeichert
- ✅ LS-Nr. wird vom Backend generiert und angezeigt
- ✅ Erfolgs-Meldung erscheint

#### 3.6 Drucken (mit Attestierung)
1. "LS drucken" Button klicken
2. Druck-Dialog öffnet sich
3. "Druck OK - beenden" klicken

**Erwartetes Ergebnis:**
- ✅ Wenn bereits gebucht: Attestierungs-Dialog erscheint
- ✅ Begründung eingeben (mind. 10 Zeichen)
- ✅ Lieferschein wird gedruckt und gebucht
- ✅ Status wird auf "gedruckt" gesetzt

### 4. Fehlerbehandlung testen

#### 4.1 Ohne Kunde speichern
**Erwartetes Ergebnis:**
- ✅ Fehlermeldung: "Bitte wählen Sie einen Kunden aus"

#### 4.2 Position ohne Artikel
**Erwartetes Ergebnis:**
- ✅ Fehlermeldung: "Bitte Artikel und Menge eingeben"

#### 4.3 Attestierung ohne Begründung
**Erwartetes Ergebnis:**
- ✅ Fehlermeldung: "Begründung ist erforderlich"
- ✅ Button "Bestätigen" ist deaktiviert

## 📝 Bekannte Einschränkungen / TODOs

1. **Lagerbestand-Integration**: "verfügbar: Menge" wird noch nicht geladen
2. **Preislogik-Integration**: Staffelpreislisten werden noch nicht abgefragt
3. **Vollständige Positions-Felder**: Lagerhalle, Charge, Serien-Nr. werden noch nicht gespeichert
4. **Niederlassung-Mapping**: `niederlassung` (Integer) muss noch zu `branch_id` (UUID) gemappt werden
5. **Vertreter-Mapping**: `vertreter` (String) muss noch zu `sales_rep_id` (UUID) gemappt werden

## 🎯 Erfolgskriterien

- ✅ Lieferschein kann erstellt werden
- ✅ Kunde kann ausgewählt werden
- ✅ Artikel können hinzugefügt werden
- ✅ Positionen werden korrekt berechnet
- ✅ Lieferschein kann gespeichert werden
- ✅ Lieferschein kann gedruckt werden
- ✅ Attestierung funktioniert für gebuchte LS
- ✅ LS-Nr. wird automatisch generiert

## 🚀 Nächste Schritte

1. Migration ausführen
2. Test-Daten prüfen (Kunden, Artikel)
3. Frontend testen
4. API-Endpunkte testen
5. Fehler beheben
6. Optional: Lagerbestand-Integration
7. Optional: Preislogik-Integration


