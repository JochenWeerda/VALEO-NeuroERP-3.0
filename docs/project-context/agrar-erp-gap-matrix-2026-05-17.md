# Externe Agrar-ERP-Plattformen — Erweiterter Gap-Vergleich

Stand: `2026-05-17`
Quellen: Direkte Browser-Analyse externer Agrar-ERP-Plattformen (165 Endpoints, 24 Module) und Agrar-Spezialsoftware (vollständiger Modulbaum).

---

## Teil 1: Externe Agrar-ERP-Plattform — 165 Endpoints in 24 Modulen

| Modul | Endpoints | Kernfunktion |
|-------|-----------|--------------|
| AUTH | 6 | Bearer Token, Passwort-Reset, Kundenzugriff |
| l3c-adresse | 5 | Adressen CRUD (OData-Filter) |
| l3c-artikel | 15 | Artikel CRUD, Chargenbestand, Düngemittel CRUD, Rezeptur-Import |
| l3c-auftrag | 12 | Angebot/Auftrag CRUD, Webshop-Integration, Teilbelege |
| l3c-bestellung | 9 | Bestellungen, Bestellvorschlag CRUD |
| l3c-dms | 2 | DMS-Token-Zugriff |
| l3c-eingangslieferschein | 2 | KMS-Dienst Buchung |
| l3c-gs1 | 1 | GS1/SSCC Barcode-Parse |
| l3c-inventur | 5 | Inventur CRUD |
| l3c-kontrakt | 1 | Kontrakt (OData-Expand: Positionen, Sorte, Laborwerte, Disposition, AlternativArtikel) |
| l3c-kunde | 18 | Kunde CRUD, Interessent→Kunde, Umkreissuche, Kontakt+Bediener Workflow |
| l3c-lager | 23 | Umbuchung CRUD, Bestandskorrektur CRUD, Rüstliste, Lagerhalle/Lagerfach |
| l3c-nachricht | 3 | Nachrichten senden/empfangen |
| l3c-nve | 2 | NVE/SSCC Labels anlegen/abrufen |
| l3c-pickliste | 9 | Pickliste CRUD, buchen/parken Aktionen |
| l3c-preis | 1 | Preis berechnen (Kalkulationsengine) |
| l3c-rechnungsausgang | 1 | Ausgangsrechnungen ermitteln |
| l3c-rechnungseingang | 2 | e-Rechnung Import (Datei + Body, ZUGFeRD/XRechnung) |
| l3c-settings | 4 | Mandant, Session, Berechtigung |
| l3c-stammdaten | 28 | Bediener, Fahrzeug, Disponent, Preistabelle, WaageStamm, Versandarten etc. |
| l3c-strecke | 3 | Streckengeschäft Import + Bearbeitung |
| l3c-verkaufslieferschein | 5 | Lieferschein CRUD + Verarbeitet-Aktion |
| l3c-webhook | 4 | Webhook-Registrierung (Bereiche, CRUD) |
| l3c-wiegeschein | 3 | Wiegeschein CRUD (dual weighing, Gosse, Laborwerte-Array, Zielschein) |

### Wiegeschein-Datenschema (kritisch für Agrar)
Schlüsselfelder, die in VALEO noch fehlen:
- `Wiegung1` / `Wiegung2` — Doppelwiegung (Brutto/Tara)
- `WiegungWaageId` / `WiegungIdentNr` — Waagen-Hardware-Referenz je Wiegung
- `Gosse` — Rinnen-/Schüttgut-Nummer an der Waage
- `Zielschein` / `Zielscheinfestgelegt` — Auto-Routing zum Lieferschein
- `Muster` / `MusterNrL3` — Probennummer (Laboranbindung)
- `Handwiegung` — Manuelle Erfassung ohne Hardware
- `Export` — Ausfuhrflag
- Sorte: `Preisa/b/c` — Dreistufige qualitätsbezogene Preise je Sorte

---

## Teil 2: Agrar-Spezialsoftware — Vollständiger Modulbaum

### Neu identifizierte Gaps gegenüber VALEO (gegenüber vorherigem Stand)

| Funktion | Modul | Gap-ID | Priorität |
|----------|-----------|--------|-----------|
| Kontraktklassen / Kontraktvarianten (Fixpreis, Basis, Prämie) | Kontrakt | L3-KONTRAKT-001 | P1 |
| Kontrakt-Hedging (MATIF, Terminmarkt-Kopplung) | Kontrakt | L3-KONTRAKT-002 | P1 |
| Kontraktmahnung (Nichterfüllung) | Kontrakt | L3-KONTRAKT-003 | P2 |
| Kontrakt Washout/Circle (gegenseitige Aufhebung) | Kontrakt | L3-KONTRAKT-004 | P2 |
| Kontrakt mark-to-market Bewertung | Kontrakt | L3-KONTRAKT-005 | P2 |
| Rohware-Sammelabrechnung | Rohware | L3-ROHWARE-001 | P1 |
| Rohware Fremdware/Fremdlager (Lohnlagerung) | Rohware | L3-ROHWARE-002 | P2 |
| Rohware Statusstapelkorrektur (Massenänderung) | Rohware | L3-ROHWARE-003 | P2 |
| Disposition sub-resource mit Freigabe + WiegescheinNr | Wiegeschein | L3-DISP-001 | P1 |
| Doppelwiegung (Wiegung1/Wiegung2) + Gosse | Waage | L3-WAAGE-001 | P0 |
| Ladeträgerverwaltung an der Waage | Waage | L3-WAAGE-002 | P2 |
| Hofliste am Waagenterminal | Waage | L3-WAAGE-003 | P2 |
| e-Rechnung Import (ZUGFeRD / XRechnung Datei) | Rechnungseingang | L3-ERECHNUNG-001 | P1 |
| Preis berechnen Endpoint (Kalkulationsengine on-demand) | Preis | L3-PREIS-001 | P1 |
| GS1 Barcode Parse Service | GS1 | L3-GS1-001 | P2 |
| Umkreissuche Kunden (Geo-Radius) | Kunde | L3-CRM-001 | P2 |
| Interessent → Kunde Konvertierung (Action-Endpoint) | Kunde | L3-CRM-002 | P1 |
| Bediener-Kontakt Workflow (gelesen/erledigt) | Kunde | L3-CRM-003 | P2 |
| Webhook-System (Outbound Event Subscriptions) | Webhook | L3-WEBHOOK-001 | P2 |
| Webshop-Integration (B2B-Bestellkatalog + Orders) | Auftrag | L3-WEBSHOP-001 | P2 |
| Rüstliste (Kommissioniervorbereitung) | Lager | L3-LAGER-001 | P2 |
| Streckengeschäft Import-Endpoint | Strecke | L3-LAGER-002 | P2 |
| BestandskorrekturGrund Stamm | Lager | L3-LAGER-003 | P2 |
| Verbotsliste / Sanktionsprüfung (Compliance) | Agrar-Zusatzmodul | VALEO-COMP-001 | P1 |
| Aktionärs-/Gesellschafterverwaltung (Genossenschaft) | Agrar-Zusatzmodul | VALEO-GEN-001 | P1 |
| Saatzucht-Modul | Agrar-Zusatzmodul | VALEO-SAATZ-001 | P2 |
| Gelangensbestätigung (§ 17a UStDV) | Agrar-FIBU | VALEO-FIBU-001 | P1 |
| Intrastat (EU-Handelsstatistik) | Agrar-FIBU | VALEO-FIBU-002 | P1 |
| ATLAS Zollausfuhr | Agrar-FIBU | VALEO-FIBU-003 | P2 |
| Wechselbuchhaltung | Agrar-FIBU | VALEO-FIBU-004 | P2 |
| e-Clearing | Agrar-FIBU | VALEO-FIBU-005 | P2 |
| eBilanz / ELSTER direkt | Agrar-FIBU | VALEO-FIBU-006 | P1 |
| AlternativArtikel per Kontraktposition | Kontrakt | L3-KONTRAKT-006 | P2 |
| Kontraktparitäten-Stamm (INCOTERMS) | Kontrakt | L3-KONTRAKT-007 | P2 |
| NVE/SSCC Lifecycle vollständig | Lager | L3-NVE-001 | P2 |

---

## Teil 3: Umsetzungspriorisierung Wave 2026-05-17

### P0 — Go-live-kritisch (sofort)
1. **L3-WAAGE-001**: Doppelwiegung + Gosse + WaageId in `waage.py` ergänzen
2. **L3-DISP-001**: Disposition sub-resource in `kontrakte.py` (Freigabe-Workflow + WiegescheinNr-Rücklink)

### P1 — Produktionsqualität (diese Woche)
3. **L3-KONTRAKT-001**: Kontraktklassen + Kontraktvarianten (Fixpreis/Basis/Prämie)
4. **L3-KONTRAKT-002**: Kontrakt-Hedging (MATIF-Referenz, mark-to-market Bewertung)
5. **L3-ROHWARE-001**: Rohware-Sammelabrechnung
6. **L3-ERECHNUNG-001**: e-Rechnung Import (ZUGFeRD / XRechnung)
7. **L3-PREIS-001**: Preis berechnen Endpoint
8. **L3-CRM-002**: Interessent → Kunde Konvertierung
9. **VALEO-COMP-001**: Sanktionsliste/Verbotsliste
10. **VALEO-GEN-001**: Aktionärs-/Gesellschafterverwaltung
11. **VALEO-FIBU-001**: Gelangensbestätigung (§17a UStDV)
12. **VALEO-FIBU-002**: Intrastat
13. **VALEO-FIBU-006**: eBilanz/ELSTER-Schnittstelle (Stub)

### P2 — Komfort (nächste Sprint-Welle)
14. GS1 Barcode Parse, Umkreissuche, Webhook-System, Webshop, Rüstliste, Strecke, etc.
