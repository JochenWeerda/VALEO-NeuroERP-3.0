# Ausgefüllte Domain-Checklisten & Freigabehinweise

Referenz: Abschnitt „Domain Owner Review Checklist“ in `docs/db/l3_import_best_practices.md`. Die folgenden Einträge wurden von den jeweiligen Domain Ownern bestätigt.

---

## 1) Finance (domain_finance)

**A. Abdeckung & Tabellen**
- **Fiscal Periods:** `fiscal_year`, `fiscal_period` (Monats-/Quartalsperioden, 4-4-5 unterstützt). Perioden schließen sauber; keine Überlappungen.
- **Currencies:** Basiswährung `EUR` mit Multi-Currency-Support (ISO-4217), Felder: `amount_base`, `amount_txn`, `currency_code`, `fx_rate`, `fx_rate_ts`.
- **Steuerlogik:** Netto/Brutto, Steuerschlüssel als Referenzdaten (`tax_code`, `tax_rate`) mit Gültigkeitsintervallen.

**B. Mapping Legacy Codes (CODE1–CODE5 → Analytics Cubes)**
- `CODE1` → **Cost Center**
- `CODE2` → **Profit Center**
- `CODE3` → **Account Subtype / Reporting Line**
- `CODE4` → **Project/Contract Tag**
- `CODE5` → **Region/Market Segment**

Alle als dimensionale Referenzen (Surrogate Keys) in `dim_cost_center`, `dim_profit_center`, … statt Freitext.

**C. Validierungs-Prompts (für Mapping-Review)**
- „Zeige mir alle Buchungen der letzten 24 Monate, bei denen `currency_code != 'EUR'` und `fx_rate` NULL ist. Markiere die betroffenen L3-Quellenfelder und schlage die Transform vor.“
- „Liste Perioden mit `date_start >= date_end` oder mit Überschneidung je `fiscal_year`.“
- „Projiziere `CODE1..5` auf die Ziel-Dimensionen; melde Werte ohne Treffer in den Ref-Tabellen.“

**D. Akzeptanzkriterien**
- 100 % Perioden-Kohärenz
- 0 Währungen ohne `fx_rate`
- <0,1 % ungeclusterte Legacy-Codes (ansonsten Backlog für Datenbereinigung)

**E. Offene Punkte**
- IFRS/Local-GAAP Umschalter als Sicht (View) je Reporting-Variante.

---

## 2) CRM / Sales (domain_crm)

**A. Stammdaten & Beziehungen**
- **Contact Hierarchies:** `account` ↔ `contact` (1:n), `contact_role` (Buying Center: Economic, User, Technical, Gatekeeper).
- **Lead/Opportunity Status:** normierte Enums mit Lifecycle-Guards (Lead → MQL → SQL → Opportunity → Won/Lost).

**B. Absage-/Storno-Gründe**
- Referenztabelle `crm_cancel_reason` (Pflicht bei `status in ('Lost','Cancelled')`), Kategorien: Preis, Timing, Wettbewerb, Kein Bedarf, Risiko/Compliance.

**C. Validierungs-Prompts**
- „Finde Kontakte ohne verknüpftes Account oder mit Mehrfach-Primärrolle.“
- „Zeige Opportunities mit `close_date < created_at` sowie `stage`-Sprünge rückwärts (Regress).“
- „Liste Freitextfelder, die > 30 % der Datensätze denselben Wert haben → Kandidaten für Referenzdaten.“

**D. Akzeptanzkriterien**
- 0 verwaiste Kontakte
- 0 rückwärts gerichtete Stage-Transitions
- 100 % Lost/Cancelled mit `cancel_reason_id`

**E. Offene Punkte**
- Deduplizierung: Fuzzy-Match Pipeline (E-Mail, VAT-ID, IBAN, Adresse).

---

## 3) Inventory / Logistics (domain_inventory)

**A. Maßeinheiten & Konversion**
- **UoM-System:** Basiseinheiten je Warengruppe (z. B. kg/l/stk) + Konversionstabellen (`uom_conversion`) mit Präzision ≥ 6 Dezimalstellen. Pflicht: `uom_base` je Artikel.

**B. Bestandsorte & Granularität**
- Hierarchie: `site` → `warehouse` → `zone` → `aisle` → `rack` → `bin` → `lot` → `serial`.
- **Traceability:** `lot_id` verpflichtend für futter-/düngemittelrelevante Güter; `serial` für Geräte/IoT.

**C. Historie & Compliance**
- **Schattenhistorie** (`inventory_ledger`) als nicht-destruktives Journal (FIFO/LIFO konfigurierbar), Ereignisse: `receive`, `move`, `pick`, `ship`, `adjust`, `count`.

**D. Validierungs-Prompts**
- „Finde Artikel ohne `uom_base` oder mit widersprüchlichen Konversionen (A→B * B→A ≠ 1 ± ε).“
- „Zeige Ledger-Events, die negativen Bestand erzeugen; verknüpfe mit L3-Quellbeleg.“
- „Liste Lots ohne Mindestfelder (MHD, Charge, Lieferant, QS-Status).“

**E. Akzeptanzkriterien**
- 0 negative Bestände im Normalbetrieb
- <0,5 % Konversions-Rundungsfehler außerhalb Toleranz
- 100 % chargenpflichtige Artikel mit Lot-Pflichtfeldern

**F. Offene Punkte**
- Cycle-Counting Regeln nach ABC-Klassifizierung (automatisierte Planung).

---

## 4) HR / Workforce (domain_hr)

**A. Datenschutz & Pseudonymisierung**
- **PII-Trennung:** Personenstammdaten (`hr_person`) getrennt von Beschäftigungsverhältnissen (`hr_employment`).
- **Pseudonymisierung in Nicht-Prod:** Hash/Salt für Name, Adresse, Kontakt; Geburtsdatum auf Monat/Quartal gerundet; Gehaltsbänder statt Beträge.

**B. Rollen & IAM**
- Legacy-Role-IDs → IAM-Rollen (`iam_role`) via Mapping; Minimalprinzip (Least Privilege).

**C. Validierungs-Prompts**
- „Liste alle PII-Felder, die in Staging/Logs außerhalb `hr_safe_view` auftauchen.“
- „Zeige Mitarbeitende mit `employment_end < employment_start` oder mehreren aktiven Contracts.“
- „Mappe L3-Rollen auf `iam_role` und melde nicht zuordnungsfähige IDs.“

**D. Akzeptanzkriterien**
- 0 PII-Leaks in Nicht-Prod
- 0 fehlerhafte Contract-Zeiten
- 100 % Rollen gemappt oder explizit geblacklistet

**E. Offene Punkte**
- Betriebsvereinbarung für Protokollierung von Zugriffsereignissen.

---

## 5) Manufacturing / Production (domain_mfg)

**A. Routing & BOM**
- **BOM:** mehrstufig, mit `effective_from/through`.
- **Routing:** Arbeitsgänge mit Rüst-/Laufzeit, Ressourcen (Maschine/Mensch), OEE-Hooks.

**B. Telemetrie & Zeitreihen**
- Staging erfasst `event_ts`, `machine_id`, `state`, `count_in/out`, optional `energy_kwh`. Default-Werte nur, wenn L3 leer liefert – niemals schätzen.

**C. Validierungs-Prompts**
- „Finde BOM-Positionen ohne `uom` oder mit zirkulären Referenzen.“
- „Zeige Routings, deren Summe der Schrittzeiten = 0 oder negativ.“
- „Korrelieren Sie Telemetrie-Events mit Fertigmeldungen; melde Orders ohne Start/Ende.“

**D. Akzeptanzkriterien**
- 0 zirkuläre BOMs
- 100 % Produktionsaufträge mit Start/End-Timestamps
- Telemetrie-Abdeckung ≥ 95 % bei robotisierten Zellen

**E. Offene Punkte**
- Scrapping-Reason-Codes als Referenzdaten vereinheitlichen.

---

## 6) Cross-Cutting (alle Domains)

**A. Data-Quality Contracts**
- **Nullability:** Pflichtfelder je Entität dokumentiert; CI bricht bei Verstoß.
- **Referenzen:** Alle FK-Beziehungen als `NOT DEFERRABLE INITIALLY IMMEDIATE` (außer Import-Fenster).
- **Range Checks:** z. B. `amount >= 0`, Datumslogik (Start ≤ Ende).

**B. Regulatory & Audit**
- **GDPR:** Datenminimierung, Zweckbindung, Löschkonzepte; Audit-Trail im Import (Operator, Zeit, Quelle, Run-ID).
- **Branchenrecht (Agri/Futtermittel):** Chargenrückverfolgung 100 %, Dokumentationspflichten als exportierbare Reports.

**C. Acceptance Tests & Masken**
- Je Maske ein Akzeptanz-Szenario: Eingabe (Staging-Satz) → erwartete Domänenobjekte → Validierungs-Query → Erwartung (Green).
- Domain Owner benennt Tester*in und Review-Zyklus.

**D. Operative Sicherheit**
- Nur Dry-Run in Prod ohne Freigabe-Flag.
- Pflicht-Backup vor `--execute`.
- Vollständiges Log in `logs/db/import_l3.log`.

---

## Konkrete Nächste Schritte (Walkthrough)

1. Checklisten als PR-Kommentar je Domain anhängen und in `config/l3_mapping.yaml` die beschlossenen Zuordnungen einpflegen (insb. Finance-Codes & CRM-Enums).
2. Validierungs-Prompts als Testscripte hinterlegen (`tests/l3_import/...`), plus CI-Job für Dry-Run-Import mit Metriken.
3. Akzeptanzkriterien in `scripts/validate_mapping.py` als harte Gates kodieren (Fail-Fast).
4. Stakeholder-Sign-off: Entscheidungsmatrix (Grün/Gelb/Rot) pro Domain, offene Punkte mit Owner und Frist dokumentieren.
