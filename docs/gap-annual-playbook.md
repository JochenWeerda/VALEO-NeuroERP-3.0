# GAP-Annual-Playbook – Prospecting & Potentialdaten

Dieses Playbook beschreibt den jährlichen Ablauf, um GAP-Daten (Agrarfonds) in VALEO/VALERO einzuspielen und daraus Potenzial- und Leaddaten für den Außendienst zu erzeugen.

## 1. Voraussetzungen

- PostgreSQL-Container läuft (`valeo-neuro-erp-postgres`, Port 5432)
- Backend läuft (Port 8000)
- Frontend läuft (Port 3000)
- DB-Schema + GAP-Domäne sind migriert:
  - `gap_payments`
  - `gap_customer_match`
  - `customer_potential_snapshot`
  - `customers` inkl. `analytics_*`-Spalten
- Feature-Flag aktiviert:

```env
VITE_ENABLE_PROSPECTING_UI=true
```

## 2. CSV von agrarzahlungen.de laden

1. Website aufrufen: https://www.agrarzahlungen.de/agrarfonds/bs
2. Für das gewünschte Jahr (z. B. 2024) die **"Gesamtliste der Begünstigten – CSV"** herunterladen.
3. Datei lokal speichern, z. B. `impdata2024.csv`.

## 3. GAP-Pipeline im Admin-UI ausführen

1. Admin-UI öffnen:
   * `http://localhost:3000/admin/gap-pipeline`

2. CSV hochladen:
   * Button "Datei auswählen" klicken.
   * `impdataYYYY.csv` wählen (z. B. `impdata2024.csv`).
   * Das UI extrahiert das Jahr automatisch aus dem Dateinamen (z. B. 2024).
   * Pfad wird serverseitig als `data/gap/impdataYYYY.csv` gespeichert.

3. Nur Import testen (optional, empfohlen beim ersten Lauf pro Jahr):
   * Button "Nur Import" klicken.
   * Statusanzeige prüfen (läuft alle 5 Sekunden aktualisiert):
     * `state: running` → `success`.
   * SQL-Check (optional):

     ```sql
     SELECT ref_year, COUNT(*)
     FROM gap_payments
     GROUP BY ref_year;
     ```

4. Komplette Pipeline ausführen:
   * Button "Komplette Pipeline starten" klicken.
   * Die Pipeline führt nacheinander aus:
     1. Import (falls noch nicht erfolgt)
     2. Aggregation (View `gap_payments_direct_agg`)
     3. Matching gegen Kunden
     4. Schreiben nach `customer_potential_snapshot`
     5. Hydration der `customers.analytics_*`-Spalten
   * Statusanzeige beobachten (Steps, Jahr, Meldungen).

## 4. Datenprüfung in der Datenbank

### 4.1 GAP-Zahlungen

```sql
SELECT ref_year, COUNT(*)
FROM gap_payments
GROUP BY ref_year;
```

### 4.2 Potenzial-Snapshots

```sql
SELECT ref_year, COUNT(*)
FROM customer_potential_snapshot
GROUP BY ref_year;
```

### 4.3 Kunden mit Analytics

```sql
SELECT
  id,
  name,
  analytics_gap_ref_year,
  analytics_gap_direct_total_eur,
  analytics_potential_total_eur,
  analytics_segment
FROM customers
WHERE analytics_gap_ref_year IS NOT NULL
LIMIT 20;
```

## 5. Frontend-Prüfungen

### 5.1 Kunden-Detail – Tab "Potential & Leaddaten"

1. Einen bekannten Betrieb im CRM öffnen (Kundenstamm).
2. Tab **"Potential & Leaddaten"** prüfen:
   * Karten/Werte:
     * geschätzte Fläche (ha)
     * Potenzial gesamt (EUR/Jahr)
     * Umsatz Vorjahr (falls befüllt)
     * Share of Wallet (%)
     * Segment (A/B/C)
   * GAP-Herkunft:
     * Referenzjahr
     * Direktzahlungen
     * Letzter Abgleich / Status
   * Steuerung:
     * "Stammkunde (geschützt)"
     * "Automatische Potenzial-Updates sperren"
     * Letzter manueller Review (Jahr)
     * Potenzial-Notiz

### 5.2 Lead-Explorer – Prospektliste

1. LeadExplorer öffnen:
   * Route: `/prospecting/leads` (ggf. im Menü verlinkt)

2. Filter-Empfehlung für den Außendienst:
   * `ref_year =` Vorjahr (z. B. 2024)
   * Segment: "A" (später ggf. "B" ergänzen)
   * Mindestpotenzial: z. B. 50.000–100.000 EUR
   * Region: "Mein Gebiet" (AD-spezifisches Gebiet)
   * Option "Nur neue Prospekte" aktivieren (keine bestehenden Kunden)

3. Ergebnisliste prüfen:
   * Spalten:
     * Name / PLZ / Ort
     * Potenzial gesamt
     * Segment-Badge (A/B/C)
     * Zertifizierungs-Icons (Bio / QS / QM-Milch)
     * Kunde? (Ja/Nein)
   * Aktionen pro Zeile:
     * "Lead anlegen"
     * "Kunde öffnen" (wenn bereits Kunde)
     * "Aufgabe" / "Zu meinen Aufgaben hinzufügen"

## 6. Umgang mit Stammkunden und Schutz-Logik

* Für Kunden, bei denen das Potenzial **manuell gepflegt** wird, im Tab "Potential & Leaddaten" setzen:
  * `Stammkunde (geschützt)`
  * `Automatische Potenzial-Updates sperren`

* Der Hydrate-Job überschreibt bei solchen Kunden keine `analytics_*`-Felder mehr.

* Empfehlung: einmal jährlich im Außendienst-Team festlegen, welche A/B-Kunden als "Stammkunden" markiert werden.

## 7. Jahres-Routine (Kurzfassung)

1. CSV für Vorjahr von agrarzahlungen.de laden.
2. Im Admin-UI `/admin/gap-pipeline` hochladen.
3. Pipeline für das Jahr starten ("Komplette Pipeline").
4. Kunden-Analytics & LeadExplorer prüfen.
5. Leads pro Außendienstgebiet zuweisen und abarbeiten.
6. Stammkunden-Flags (Schutz) und Potenzial-Notizen gezielt nachpflegen.

## 8. Troubleshooting

### Pipeline startet nicht
- Prüfe Backend-Logs: `docker logs valeo-neuro-erp-backend`
- Prüfe ob CSV-Datei existiert: `ls -lh data/gap/impdata2024.csv`
- Prüfe Datenbankverbindung im Backend

### CSV-Upload schlägt fehl
- Prüfe ob `data/gap/` Verzeichnis existiert
- Prüfe Dateigröße (sollte < 200MB sein)
- Prüfe Backend-Logs für Fehlerdetails

### Keine Daten nach Pipeline
- Prüfe Backend-Logs für Fehler
- Prüfe ob `customers`-Tabelle existiert
- Prüfe ob GAP-Tabellen existieren: `\dt gap_*`

### Matching findet keine Kunden
- Prüfe ob Kunden in `customers`-Tabelle existieren
- Prüfe Name-Normalisierung (PLZ, Ort müssen übereinstimmen)
- Prüfe `gap_customer_match` Tabelle für Match-Ergebnisse

## 9. API-Referenz

### CSV-Upload
```http
POST /api/v1/gap/pipeline/upload
Content-Type: multipart/form-data
Body: file=<impdata2024.csv>
```

### Pipeline starten
```http
POST /api/v1/gap/pipeline/run-year
Content-Type: application/json
Body: {
  "year": 2024,
  "csv_path": "data/gap/impdata2024.csv"
}
```

### Status prüfen
```http
GET /api/v1/gap/pipeline/status?year=2024
```

## 10. Segmentierung (A/B/C)

Die Segmentierung basiert auf dem Share of Wallet (SOW):

- **Segment A**: SOW ≥ 80% (Stammkunden)
- **Segment B**: SOW ≥ 40% (Wachstumspotenzial)
- **Segment C**: SOW < 40% (Neue Prospekte)

Berechnung:
```
SOW = (Umsatz Vorjahr / Potenzial gesamt) * 100
```

## 11. Potenzial-Berechnung

Das Potenzial wird basierend auf der geschätzten Fläche berechnet:

- **Geschätzte Fläche**: `GAP-Direktzahlungen / 270 EUR/ha`
- **Potenzial Saatgut**: `Fläche * 50 EUR/ha`
- **Potenzial Dünger**: `Fläche * 150 EUR/ha`
- **Potenzial PSM**: `Fläche * 80 EUR/ha`
- **Potenzial gesamt**: Summe der drei Komponenten

Die EUR/ha-Werte können über die Umgebungsvariable `GAP_EUR_PER_HA` angepasst werden (Standard: 270).

