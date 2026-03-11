# Zielbild VALEO Landhandel ERP

**Stand:** 2026-03-11

## Zweck

Dieses Dokument verdichtet die strategische Zielrichtung fuer VALEO NeuroERP 3.0 in eine umsetzbare Leitlinie fuer Produkt-, Architektur- und Roadmap-Entscheidungen.

## 1. Zielposition

VALEO wird als **vertikales, AI-faehiges ERP fuer Agrarhandel und Genossenschaften** weiterentwickelt.

Nicht das Ziel:

- generisches Horizontal-ERP fuer beliebige Branchen

Zielkundengruppen:

- Agrarhandel
- Genossenschaften / Verbundstrukturen
- Futtermittel- und rohstoffnahe Handels- und Annahmeprozesse

## 2. Produktkern

Die Differenzierung entsteht nicht durch moeglichst viele Einzelfunktionen, sondern durch einen starken Produktkern:

1. **Canonical Domain Model**
2. **Workflow- und Policy-Layer**
3. **Agent-/Action-Layer**
4. **Mask-/Process-Builder**
5. **Read-Model-/Analytics-Schicht**

Jede relevante Weiterentwicklung sollte mindestens einen dieser Kernbereiche staerken.

## 3. Architekturrichtung

### Ziel

**Modularer Monolith mit klaren Domänengrenzen**

### Begruendung

- ERP-Komplexitaet entsteht im Domänenmodell, nicht primaer im Deployment
- Kernprozesse wie `Kontrakt -> Annahme -> Qualitaet -> Settlement -> FiBu` brauchen enge fachliche Konsistenz
- zu fruehe Microservice-Zerlegung erhoeht Kopplung, Betriebsaufwand und Inkonsistenzrisiko

### Leitprinzipien

1. Canonical Domain Model vor API-Wildwuchs
2. Business Commands vor UI-CRUD
3. Workflow-Konfiguration vor harter Prozesslogik
4. Read Models fuer Performance, nicht als zweite Wahrheit
5. Policies, Freigaben und Audit als Kernbestandteil
6. Erweiterungspunkte nur an stabilen Fachgrenzen

## 4. Canonical Domain Model

### Kernaggregate

1. Tenant / Company
2. User / Role / Permission
3. Business Partner
4. Item / Product / Material
5. Location / Warehouse / Silo / Bin
6. Contract
7. Order
8. Delivery / Intake / Shipment
9. Quality Result / Lab Result
10. Invoice / Credit / Settlement
11. Payment / Bank Transaction
12. Inventory Move / Stock Position
13. Journal Entry / Ledger Posting
14. Workflow Instance / Approval
15. Document / Attachment / Audit Evidence

### Agrar-spezifische Pflichtaggregate

- Field / Schlag
- Season / Campaign / Harvest Window
- PSM / Duenger / Saatgut Anwendung
- Weighing Ticket
- Commodity Lot / Charge / Partie

### Modellierungsregeln

- keine konkurrierenden Schattenmodelle pro Modul oder UI
- Aggregatbesitz fachlich eindeutig definieren
- APIs, Read Models und Agent-Tools mappen vom Canonical Model aus
- neue Fachlogik darf keine dritte oder vierte Wahrheit etablieren

## 5. Zielprozesse

Die priorisierten Zielprozesse fuer die Produktreife sind:

1. `Kontrakt -> Annahme -> Qualitaet -> Settlement -> FiBu`
2. `RFQ -> Bestellung -> Wareneingang -> Rechnung -> Zahlung`
3. `Kampagne / Saison -> Beratung -> Auftrag -> Lieferung -> Abrechnung`
4. `Annahme / Wiegen -> Charge / Partie -> Lager / Silo -> Verkauf / Logistik`

Ein Prozess gilt erst dann als „fertig“, wenn er:

- ohne Medienbruch laeuft
- auditierbar ist
- freigabefaehig ist
- agentenfaehige Commands besitzt
- belastbare Read Models und KPIs hat

## 6. Roadmap-Leitlinie

### Jetzt

- Agrar-P0 schliessen
- Rohwarenabrechnung und Qualitaetslogik industrialisieren
- Workflow-Versionierung, SLA, Simulation und Audit standardisieren
- Multi-User-, Read-Model- und Performance-Stabilitaet absichern
- Designsystem und Prozesspatterns verbindlich machen

### Danach

- Supplier Portal
- Genossenschafts-spezifische Domänen
- Plattformfaehige Agent-Contracts
- Silo-/IoT-/Predictive-Erweiterungen

## 7. Vertrauensstrategie

### Zuerst

- GoBD-faehige Produktpfade
- Verfahrensdokumentation
- DSGVO-/Datenschutz-Konzept
- nachweisbare Audit- und Exportpfade

### Danach

- ISO 27001
- optional ISO 9001
- weitere Nachweise nur nach echtem Zielmarktbedarf

## 8. Nicht-Ziele

- kein generisches ERP fuer beliebige Branchen als Hauptstrategie
- keine vorschnelle Microservice-Zerlegung des Kerns
- kein AI-first auf instabilen Fachobjekten
- keine Feature-Vermehrung ohne Rueckkopplung an den Produktkern
- keine Zertifizierungsarbeit ohne produktive, pruefbare Prozesspfade

## 9. Referenzen

- [2026-03-06-valeo-spitzenposition-konsolidiert.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/roadmap/status/2026-03-06-valeo-spitzenposition-konsolidiert.md)
- [2026-03-06-top-50-gap-backlog-landhandel.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/roadmap/status/2026-03-06-top-50-gap-backlog-landhandel.md)
- [2026-03-06-arbeitsaufteilung-codex-hauptstrang.md](c:/Users/Jochen/VALEO-NeuroERP-3.0/docs/roadmap/status/2026-03-06-arbeitsaufteilung-codex-hauptstrang.md)
