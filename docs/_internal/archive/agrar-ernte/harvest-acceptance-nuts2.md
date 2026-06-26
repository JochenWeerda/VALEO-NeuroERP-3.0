# NUTS-2-Implementierung in Ernte-Annahme (Harvest Acceptance)

**Erstellt:** 2026-02-17  
**Status:** ✅ Implementiert

---

## Übersicht

Die NUTS-2-Implementierung ermöglicht die Erfassung der **Herkunft/Region der Erzeugung** bei Anlieferungen, um Anforderungen für **Nachhaltigkeitsnachweise / Biomasse-Zertifizierung** (RED-II, ISCC, REDcert, SURE) zu erfüllen.

## Bedeutung von NUTS-2 bei Anlieferungen

### Hauptzweck: Nachhaltigkeitsnachweise / Biomasse-Zertifizierung

Wenn Getreide/Ölsaaten in **Bioenergie-/Biokraftstoff-Lieferketten** gehen (z. B. Ethanol aus Mais/Weizen oder Biodiesel aus Raps), taucht NUTS-2 auf **Sustainability Declarations / PoS** auf, weil für die **THG-Bilanz** regionale Werte genutzt werden können.

- **ISCC** nennt explizit, dass (u. a. First Gathering Points) bei Sustainability Declarations **den passenden NUTS-2-Code** angeben können/sollen, je nach gewählter GHG-Option.
- **NUTS-2-Werte** werden als **typische THG-Emissionswerte für den Anbau** je Region geführt (z. B. Deutschland), und sind RED-II-bezogen.
- **REDcert/SURE-Dokumente** erklären ebenfalls, dass **NUTS-2-Werte** entlang der Kette als Input für die GHG-Rechnung genutzt werden.

**Konsequenz fürs ERP:** NUTS-2 an der Anlieferung = „Region of cultivation" / „Region of origin", damit später SD/PoS/Chain-of-Custody korrekt erzeugt werden können.

### Weitere Zwecke

1. **Statistik/Reporting und Warenstrom-Auswertungen** (klassisch im Handel)
   - Reporting: Mengen, Qualitäten, Preise **nach Herkunftsregion**
   - Warenstrom: „Wo kommt's her / wohin geht's", ggf. für Verbände/Behörden/Management

2. **Plausibilisierung von Herkunftsangaben** (Audit-/QS-Zwecke)
   - Standardisierte, auditierbare Regionalklasse
   - Für Nachhaltigkeit/RED-Ketten kann es „must" sein

## Datenmodell

### HarvestAcceptance (Header-Level)

**Bedeutung:** NUTS-2 = "Herkunft/Region der Erzeugung" (nicht Standort des Lagers)

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `origin_nuts2_code` | String(10) | NUTS-2-Code der Herkunft (Region der Erzeugung/Anbau) |
| `nuts_version` | String(20) | NUTS-Version (z.B. "NUTS 2024") für Audit |
| `origin_postal_code` | String(10) | PLZ der Herkunft (für Ableitung/Validierung) |
| `origin_city` | String(100) | Ort der Herkunft (für Ableitung/Validierung) |
| `origin_country_code` | String(2) | Ländercode der Herkunft (ISO 3166-1 alpha-2) |
| `is_sustainable_biomass` | Boolean | Nachhaltige Biomasse (für RED-II/ISCC/REDcert) |

**Index:** `ix_harvest_acceptances_nuts2` auf `(origin_nuts2_code, nuts_version)` für Reporting/Statistik.

### HarvestAcceptancePosition (Position-Level für Mischladungen)

**Bedeutung:** Bei Mischladungen (mehrere Herkunftsorte) kann jede Position eigene Herkunft haben.

| Feld | Typ | Beschreibung |
|------|-----|--------------|
| `origin_nuts2_code` | String(10) | NUTS-2-Code der Herkunft für diese Position |
| `nuts_version` | String(20) | NUTS-Version (z.B. "NUTS 2024") für Audit |
| `origin_postal_code` | String(10) | PLZ der Herkunft (für Ableitung/Validierung) |
| `origin_city` | String(100) | Ort der Herkunft (für Ableitung/Validierung) |
| `origin_country_code` | String(2) | Ländercode der Herkunft (ISO 3166-1 alpha-2) |

**Index:** `ix_harvest_acceptance_positions_nuts2` auf `(origin_nuts2_code, nuts_version)` für Reporting/Statistik.

## Validierung & Versionierung

### NUTS-Versionierung

- **NUTS wird periodisch aktualisiert** → speichert zusätzlich `nuts_version` (z. B. "NUTS 2024") oder ein Datum, damit spätere Änderungen alte Belege nicht verfälschen.
- **Default:** `nuts_version = "NUTS 2024"` (konfigurierbar pro Tenant/System)

### Ableitung von NUTS-2

**Best Practice (automatisch ableiten):**

1. **Primärquelle:** Herkunftsadresse (Betrieb/Schlag/Abholort) beim Lieferantenprofil oder beim Ticket
2. **Ableitung:** PLZ/Ort → NUTS-2 über offizielle Zuordnungstabellen (Eurostat „correspondence tables")
3. **Anlieferung übernimmt den Code als Snapshot** (mit Version)

**TODO:** Implementierung einer PLZ/Ort → NUTS-2-Ableitung (Service/API-Endpoint)

### Validierung

- **Format:** NUTS-2-Code muss gültigem Format entsprechen (z.B. "DE12" für Sachsen)
- **Unbekannt/noch nicht ermittelbar:** erlaubt, aber dann Status/Warnung („SD/PoS nicht erzeugbar")
- **Mischladung:** Pro Position `origin_nuts2_code` + Menge (Summe der Positionen = Gesamtmenge)

## Verwendung

### Einfache Anlieferung (eine Herkunft)

```json
{
  "acceptance_number": "HA-2025-001",
  "customer_id": "customer-uuid-123",
  "article_id": "article-uuid-456",
  "delivery_date": "2025-02-17",
  "origin_nuts2_code": "DE12",
  "nuts_version": "NUTS 2024",
  "origin_postal_code": "01067",
  "origin_city": "Dresden",
  "origin_country_code": "DE",
  "is_sustainable_biomass": true
}
```

### Mischladung (mehrere Herkunftsorte)

```json
{
  "acceptance_number": "HA-2025-002",
  "customer_id": "customer-uuid-123",
  "article_id": "article-uuid-456",
  "delivery_date": "2025-02-17",
  "positions": [
    {
      "position_number": 10,
      "description": "Angelieferte Menge",
      "quantity_kg": 5000.0,
      "origin_nuts2_code": "DE12",
      "nuts_version": "NUTS 2024",
      "origin_postal_code": "01067",
      "origin_city": "Dresden"
    },
    {
      "position_number": 10,
      "description": "Angelieferte Menge",
      "quantity_kg": 3000.0,
      "origin_nuts2_code": "DE14",
      "nuts_version": "NUTS 2024",
      "origin_postal_code": "06108",
      "origin_city": "Halle"
    }
  ]
}
```

## Entscheidungshilfe: Braucht ihr das wirklich?

- **Ja, zwingend**, wenn ihr **RED/ISCC/REDcert/SURE**-Ströme abbildet oder SD/PoS erzeugt.
- **Optional**, wenn ihr "nur" klassischen Handel ohne Nachhaltigkeitskette macht – dann ist es eher Reporting.

## Nächste Schritte

1. ✅ **DB-Modelle erstellt** (`HarvestAcceptance`, `HarvestAcceptancePosition`)
2. ✅ **Migration erstellt** (`b38680c2f581_add_harvest_acceptance_with_nuts2_20260217.py`)
3. ⏳ **API-Endpoints** (CRUD für Harvest Acceptance)
4. ⏳ **PLZ/Ort → NUTS-2-Ableitung** (Service/API-Endpoint)
5. ⏳ **Validierung** (NUTS-2-Format, Versionierung)
6. ⏳ **Frontend-Integration** (Eingabefelder, Auto-Ableitung)
7. ⏳ **Reporting** (Mengen/Qualitäten/Preise nach Herkunftsregion)

## Referenzen

- [ISCC System - NUTSII Update](https://www.iscc-system.org/news/nutsii-update/)
- [Umweltbundesamt - Report on typical GHG emission values](https://www.umweltbundesamt.de/en/publikationen/report-on-typical-ghg-emission-values-for-the)
- [REDcert - Scheme principles for GHG calculation](https://www.redcert.org/fileadmin/user_upload/REDcert/PDF_Dokumente/Mobilit%C3%A4t/Englisch/SP_EU_GHG_Vers07.pdf)
- [Eurostat - Correspondence tables](https://ec.europa.eu/eurostat/web/nuts/correspondence-tables)
- [Eurostat - Territorial units for statistics (NUTS)](https://ec.europa.eu/eurostat/web/gisco/geodata/statistical-units/territorial-units-statistics)


