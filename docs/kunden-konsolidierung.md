# Kunden-Stammdaten-Konsolidierung — Mapping & Inventur (Phase 1)

> Begleitdokument zum Plan „Business-Partner / Kundenstamm als System of Record".
> Ziel: **eine** Kunden-Wahrheit. Business Partner (`domain_crm.business_partners`)
> ist die führende Identität; `public.kunden` bleibt operativer ERP-Sitz, gebunden
> über `business_partner_id`. CRM-Microservices reichern an, besitzen aber keine
> eigene Kundentabelle mehr. Stand: 2026-06-01.

## 1. Tabellen-Inventar

| Tabelle | Rolle | Spalten | Zeilen (Dev) | Schlüssel |
|---|---|---|---|---|
| `domain_crm.business_partners` | **SoR-Identität** (Ziel) | 149 | 149 | `partner_id` (UUID), `partner_number` |
| `public.kunden` (+ `kunden_*`-Satelliten) | **Operativer ERP-Sitz** (führend kurzfristig) | 81 | 5 | `kunden_nr` (PK) + NEU `business_partner_id`, `legacy_kunden_nr` |
| `domain_crm.customers` | Silo (CRM-Stub, → mergen) | 23 | 3 | `id` (UUID), hat `business_partner_id` |
| `domain_crm.crm_customers` | Silo (CRM-Spiegel, → mergen) | 29 | 0 | `id` (UUID) |
| `public.crm_core_customers` | Silo (crm-core-Cache, → CRM-Projektion) | 15 | 1 | `id` (UUID) |
| `domain_erp.business_partners` | BP-Fragment (→ in SoR mergen/klären) | 8 | — | — |

## 2. Identitäts-/Schlüssel-Strategie

- **`business_partner_id` (UUID)** = technische Integrations-Identität (= `business_partners.partner_id`). Einziger stabiler Cross-System-Schlüssel.
- **`kunden_nr` / `partner_number`** = fachliche Nummern (KEINE Integrations-ID).
- **`legacy_kunden_nr`, external_refs** = Alt-/Importnummern (CRM, übernommene Systeme).
- Brücke (Phase 1, additiv, umgesetzt): `public.kunden.business_partner_id` + `legacy_kunden_nr` (Migration `alembic/versions/kunden_bp_bridge_20260601.py`). FK + Backfill in Phase 2.

## 3. Spalten-Mapping der Silos → Ziel

Legende: **BP** = `business_partners`, **K** = `public.kunden`, **BP-Sat** = BusinessPartner-Satellit, **CRM-Proj** = CRM-Projektion (Phase 2), **LÜCKE** = Zielspalte fehlt → in Phase 2 ergänzen.

### 3.1 `domain_crm.customers` (Stub, hat bereits `business_partner_id`)
| Silo-Spalte | Ziel |
|---|---|
| id | → wird `business_partner_id` (UUID-Identität) |
| customer_number | BP.partner_number / K.kunden_nr |
| company_name | BP.name_1 / K.name1 |
| contact_person | BP-Sat `BusinessPartnerContact` |
| email, phone, website | BP (Kontaktfelder) / BP-Sat Contact |
| address, city, postal_code, country | BP.city/postal_code + BP-Sat `BusinessPartnerAddress` |
| industry | BP / CRM-Proj |
| customer_type | BP (Rolle/Typ) |
| credit_limit, payment_terms | BP-Sat `BusinessPartnerBillingConfig` |
| tax_id | BP.tax_number / vat_id |
| chefanweisung | BP-Sat `BusinessPartnerInstruction` |
| is_active, deleted_at | BP-Status / Soft-Delete |
| business_partner_id | = Brückenschlüssel (bereits vorhanden) |

### 3.2 `domain_crm.crm_customers` (Spiegel)
| Silo-Spalte | Ziel |
|---|---|
| customer_number | BP.partner_number / K.kunden_nr |
| company_name, salutation, first_name, last_name | BP.name_1/name_2, first_name, last_name |
| street, postal_code, city, country | BP-Sat Address / BP.postal_code/city |
| phone, email, mobile | BP / BP-Sat Contact |
| ust_id, tax_number | BP.vat_id, BP.tax_number |
| credit_limit, payment_terms, discount, credit_rating, price_group, tax_category | BP-Sat BillingConfig/PricingRule |
| last_order_date, total_revenue | **CRM-Proj** (Verkaufs-/Analytik-Projektion, nicht im Stamm) |
| customer_segment, status | **CRM-Proj** (crm_segments / crm_customer_profile) |

### 3.3 `public.crm_core_customers` (crm-core-Cache → CRM-Projektion)
| Silo-Spalte | Ziel |
|---|---|
| display_name, legal_name | BP.name_1 / name_2 |
| type, status | BP-Typ + **CRM-Proj** (Status/Pipeline) |
| email, phone, industry, region | BP / CRM-Proj |
| **lead_score, churn_score** | **CRM-Proj** (`crm_customer_profile`, FK business_partner_id) — reine CRM-Anreicherung |
| notes | BP-Sat / CRM-Proj |

## 4. Identifizierte LÜCKEN (Phase 2 — in BP/Satelliten ergänzen)

- CRM-Scoring (`lead_score`, `churn_score`, `customer_segment`, Pipeline-`status`) → neue **CRM-Projektionstabellen** (`crm_customer_profile`, `crm_segments`), FK `business_partner_id`. Nicht in den Stamm.
- Verkaufsaggregat (`total_revenue`, `last_order_date`) → Analytik-/Verkaufs-Projektion (vgl. Share-of-Wallet-Quelle), nicht im Stamm.
- `external_refs` (Mehrfach-Fremdschlüssel) → ggf. eigene `business_partner_external_refs`-Tabelle.

## 5. Konsumenten-Inventar (~26 Dateien)

### Lesen/Schreiben auf `domain_crm.customers` (12)
`app/services/customer_service.py` (+ `app/integrations/crm_core_client.py`), `app/api/v1/endpoints/customers.py` (Hybrid!), `credit_management.py`, `payment_matching.py`, `pricing.py`, `sales_invoice_einvoice.py`, `sales_orders.py`, `customer_sales_eligibility.py`; ORM `app/infrastructure/models/__init__.py`, `agrar_models.py`, `l3c_models.py`.

### Lesen/Schreiben auf `public.kunden` (14)
`app/api/v1/endpoints/customers.py`, `dauerauftraege.py`, `fibu_zahlungsmeldungen.py`, `kundenbanken.py`, `price_calculation.py`, `vermehrungsvertrag.py`, `versandprofile.py`, `geo.py`; `app/verkauf/{models,router,schemas}.py`; `app/services/{geo_pipeline,lkv_pipeline}.py`; `app/api/v1/schemas/dauerauftraege_schemas.py`.

**Regel ab sofort:** Kein neuer Direktzugriff auf Kundentabellen — nur über die kanonische Schicht (`BusinessPartnerService` / `build_customer_match_lookup`).

## 6. Phase-1-Stand (umgesetzt)

- **1B** Brücke `public.kunden.business_partner_id` + `legacy_kunden_nr` (Migration + in Dev angewandt).
- **1C** Kanonische Schicht: `business_partner_service.build_customer_match_lookup(db)` (BP ∪ kunden, tokenset+plz) + `resolve_customer_ref`.
- **1D** Pilot: `lkv_pipeline.build_kunden_lookup` delegiert an die Schicht; GAP/Dairy/Geo-Match jetzt BP-aware. Nachweis: dairy→kunden 0→1, geo `is_customer` 0→1.

## 8. 81-Spalten-Klassifizierung `public.kunden` → Domänen (Phase 2D)

Ziel: schlanker Kernstamm + ausgelagerte Domänen. **Viele Zieltabellen existieren bereits** (Spalte „Vorhandene Tabelle"). Nur dort, wo „NEU", muss angelegt werden.

| Domäne | Spalten aus `public.kunden` | Vorhandene Zieltabelle |
|---|---|---|
| **Kern (bleibt in kunden)** | business_partner_id, kunden_nr, name1, name2, name3, gueltig_ab, gueltig_bis, geloescht, sprachschluessel, erstellt_am, geaendert_am | — (Kern) · `matchcode` NEU (suchoptimiert) · `status`/`kundentyp` NEU (abgeleitet) |
| **Adresse** | strasse, plz, ort, land, postfach, postfach_plz, postfach_ort | **NEU** `kunden_adressen` (Typ Haupt/Liefer/Post) — alternativ `BusinessPartnerAddress` |
| **Kommunikation** | tel, fax, email, homepage | `kunden_ansprechpartner` (vorh.) bzw. NEU `kunden_kommunikation` |
| **Bank** | bank, iban, bic, sepa_verfahren, mandat, lastschriftverfahren | `domain_shared.kunden_bankverbindungen` (vorh.) |
| **Zahlung/Abrechnung** | zahlungsbedingungen_tage, skonto, netto_kasse, mahnwesen, kontonutzung_rechnung, kontoauszug_gewuenscht, saldo_druck_rechnung, druck_verbot_rechnung, druck_werbetext, versandpauschalen_berechnen, einzel_abrechnung, sammel_abrechnung, sammel_abrechnung_ohne_einzel, sammel_abrechnungskennzeichen, bonus_berechtigung, bonus_rechnungsempfaenger_id, bemerkenswerte_forderung, selbstabrechnung_durch_kunden, selbstabrechner_verkauf_zukauf, direktes_konto, rabatt_verrechnung, selbstabholer_rabatt, direktabzug, wochenpreis_ec_basis, verrechnung_automatisch, offene_posten_nicht_aufrufen, rechnungs_sammeldruck, nachkalkulation, formular_id, preisermittlung_sorten | `kunden_lieferung_zahlung` (vorh., Teil) + **NEU** `kunden_zahlung` (Kredit/Mahn/Abrechnungs-Flags) |
| **Steuer** | (keine direkten Spalten in kunden) | `kunden_allgemein_erweitert.ust_id_nr/steuernummer` (vorh.) — bereits ausgelagert |
| **Währung/Zins** | umrechnung_euro, umrechnungskurs, waehrung, zinstabelle_id, letzter_zinstermin, saldo_letzte_zinsabrechnung | **NEU** `kunden_zins` / Teil `kunden_aggregates` |
| **CRM-Profil/Statistik** | statistik_kennzeichen, marktpreis_auswertung, schwellenwert, selektion_schluessel, selektion_berechnung, versicherung, lade_information, allgemeine_angaben, kunden_zusatz | `kunden_profil` (vorh.) bzw. **NEU** `kunden_crm_profile` |
| **Versand/EDI** | edifact_invoic, edifact_orders, edifact_desadv | `kunden_versand` (vorh.) |
| **Webshop** | webshop_kunde, webshop_bezeichnung | `kunden_profil`/Webshop-Projektion |
| **Agrar/Genossenschaft** | landwirtschaftsamt_betriebsnummer (↔ BP.farm_number) | `kunden_genossenschaft` (vorh.) + BP-Identität |
| **External Refs** | legacy_kunden_nr, webshop_kunden_nr, tankkarte_ean_code, kundenkarten_kennzeichen | **NEU** `kunden_external_refs` (typ, wert) |
| **Aggregate** | (keine in kunden — kommen aus Verkauf/FiBu) | **NEU** `kunden_aggregates` (Umsatz/letzter Auftrag/OP) |

**Fazit:** Von ~12 Domänen sind **8 bereits als Tabellen vorhanden**; NEU anzulegen sind v.a. `kunden_adressen`, `kunden_zahlung`, `kunden_external_refs`, `kunden_aggregates` (+ optional `kunden_crm_profile`). Steuer ist bereits in `kunden_allgemein_erweitert` ausgelagert (public.kunden hat keine USt-Spalte — deckt sich mit dem Reconciliation-Befund).

## 9. `kunden_lookup` — Entwurf für schnelle Kundenauswahl

Such-/Listen-View mit **nur** den auswahlrelevanten Feldern; Detaildaten werden erst beim Öffnen über die Domänen-Methoden der Zugriffsschicht nachgeladen.

```sql
CREATE OR REPLACE VIEW public.kunden_lookup AS
SELECT
    k.business_partner_id,
    k.kunden_nr,
    k.name1                                   AS name,
    -- Matchcode suchoptimiert; bis Kernspalte existiert aus name1 abgeleitet:
    lower(regexp_replace(coalesce(k.name1, ''), '[^a-zA-Z0-9]', '', 'g')) AS matchcode,
    (NOT coalesce(k.geloescht, FALSE))        AS aktiv,
    a.plz, a.ort, a.strasse,                  -- Übergang: aus public.kunden, Ziel: kunden_adressen
    ae.ust_id_nr,
    ae.kundengruppe,
    ae.vertriebsbeauftragter                  AS betreuer,
    ae.sperrgrund
FROM public.kunden k
LEFT JOIN public.kunden_adressen a            -- Ziel; Übergangsversion liest plz/ort/strasse direkt aus k
       ON a.kunden_nr = k.kunden_nr AND a.adresstyp = 'hauptadresse'
LEFT JOIN public.kunden_allgemein_erweitert ae
       ON ae.kunden_nr = k.kunden_nr
WHERE coalesce(k.geloescht, FALSE) = FALSE;
```

- **Übergangsvariante (vor 2D-Migration):** `plz/ort/strasse` direkt aus `public.kunden` (statt `kunden_adressen`-Join) — sonst identisch.
- **Performance:** bei Bedarf als **Materialized View** + Refresh (nach Stammdaten-Mutationen / nächtlich) und Index auf `matchcode`, `(plz, ort)`, `name`.
- **Felder Schnellauswahl:** Kundennummer, Name, Matchcode, PLZ, Ort, Status/aktiv, Betreuer, Sperrstatus — exakt der vom UI bei der Suche benötigte Satz.
- **Zugriffsschicht:** `BusinessPartnerService` bekommt `search_lookup(query)` (liest `kunden_lookup`) für Listen/Autocomplete; `get_full(business_partner_id)` lädt Detail aus den Domänentabellen.

## 10. Phase 2D Schritt 2 — Domänentabellen angelegt (2026-06-02)

Migration `alembic/versions/kunden_domain_tables_20260602.py` (head, down_revision `perf_indexes_apply_20260602`) legt die 4 NEU-Tabellen **additiv + leer** an (CREATE TABLE IF NOT EXISTS, idempotent, KEIN Datenumzug):

| Tabelle | Kardinalität | Inhalt | FK |
|---|---|---|---|
| `kunden_adressen` | 1:n | adress_typ (haupt/liefer/postfach/rechnung), strasse/plz/ort/land, postfach* , ist_standard | kunden_nr → public.kunden ON DELETE CASCADE |
| `kunden_zahlung` | 1:1 | zahlungsbedingungen/skonto/mahnwesen/sepa/abrechnungs-flags (23 Sp.) | kunden_nr PK→FK |
| `kunden_external_refs` | 1:n | (ref_typ, ref_wert, quelle) für legacy_kunden_nr/webshop_kunden_nr/tankkarte_ean/kundenkarte; UNIQUE(kunden_nr,ref_typ,ref_wert) | kunden_nr → FK |
| `kunden_aggregates` | 1:1 | abgeleitete Kennzahlen (umsatz_ytd/vorjahr, letzter_auftrag, offene_posten, saldo) — **Performance-/Temp-Schicht**, refresh aus Verkauf/FiBu | kunden_nr PK→FK |

Verifiziert: 4 Tabellen, je 1 FK, 0 Zeilen, `alembic current == head`, re-upgrade no-op.

### Schritt 3 — Backfill + Lookup-Repoint UMGESETZT (2026-06-02)

- **Backfill** `app/services/kunden_backfill.py` (Dry-Run/`--apply`, idempotent, reversibel — schreibt nur in Satelliten, `public.kunden` unberührt): Adresse→`kunden_adressen` (haupt/postfach), Zahl-/Abrechnungs-Flags→`kunden_zahlung` (Upsert), Altnummern→`kunden_external_refs` (legacy/webshop/tankkarte/kundenkarte), 1:1-Platzhalter→`kunden_aggregates`. **Wichtig:** Satellitenspalten spiegeln die *inkonsistenten Legacy-Typen* (mahnwesen/sepa_verfahren/mandat=boolean, lastschriftverfahren/einzel_abrechnung=varchar) für verlustfreien Lift-and-Shift; Normalisierung später.
- **`kunden_lookup` repointet** (Migration `kunden_lookup_adressen_20260602`, head): plz/ort/strasse jetzt `COALESCE(kunden_adressen.haupt, public.kunden)`. DROP+CREATE statt REPLACE (COALESCE über verschieden lange varchar ändert Spaltentyp → REPLACE verweigert). Bewiesen: Satellit-Update schlägt in View durch, `public.kunden` bleibt Quelle nur als Fallback.

### Schritt 3b — Konsumenten auf Satelliten umgehängt (2026-06-02)

- **Zugriffsschicht satelliten-aware**: `build_customer_match_lookup` liest PLZ jetzt via `LEFT JOIN kunden_adressen (haupt)` mit COALESCE-Fallback auf `public.kunden`.
- **Neue Domänen-Detail-Leser** in `BusinessPartnerService` (Satellit bevorzugt, Übergangs-Fallback auf public.kunden-Altspalten): `get_customer_address(kunden_nr, typ)`, `get_customer_payment(kunden_nr)`, `get_customer_external_refs(kunden_nr)` und aggregierend `get_customer_detail(kunden_nr)`.
- **Endpoint**: `GET /api/v1/customers/lookup/{kunden_nr}/detail` (Gegenstück zu `/lookup`) → lädt Adresse/Zahlung/Refs on-demand aus den Satelliten.
- **Dead-Code-Bereinigung**: `lkv_pipeline` — letzte env-konfigurierte Direkt-SQL-Reste auf `public.kunden` (`KUNDEN_TABLE/_KEY/_NAME/_PLZ/_DELETED_COL`, `_table_parts`, `_column_exists`) entfernt; Match läuft ausschließlich über die kanonische Schicht.
- **Befund**: Das `Kunde`-ORM-Model in `app/verkauf/models.py` (Tabelle `kunden`) wird **nirgends importiert** → kein aktiver Direktkonsument; backendseitig lesen sonst nur Zugriffsschicht/Reconciliation/Backfill `public.kunden`.

### Schritt 3c — Frontend-Schnellauswahl auf Satelliten (2026-06-02)

- **API-Client** `lib/api/kunden-lookup.ts`: `useKundenLookup(q,limit)` → `/customers/lookup`, `useKundenDetail(kunden_nr)` → `/customers/lookup/{kunden_nr}/detail`.
- **Maske** `pages/crm/kunden-schnellauswahl.tsx`: zweispaltig (Suche+Trefferliste links, Satelliten-Detail Adresse/Zahlung/Refs rechts, on-demand). Reine Lese-/Auswahlmaske. Nav-Eintrag „Kunden-Schnellauswahl" (commercial.tsx) + Route `/crm/kunden-schnellauswahl` (auto-groups/generated/crm.ts).
- **Bewusst additiv statt Produktivmaske umgebogen**: `CustomerCombobox`/`kunden-liste` tragen die crm-customer-id-Identität (Aufträge/Rechnungen); Satelliten sind kunden_nr-basiert → hartes Umbiegen würde die Identität brechen. Die neue Maske demonstriert den Satelliten-Pfad end-to-end risikofrei.
- **Nebenbei behoben**: `components/ui/native-select.tsx` — `NativeSelect` leitete `ref` nicht weiter (RHF `register()` defekt) + `value` war required → auf `forwardRef` + Standard-Select-Props (uncontrolled-fähig) umgestellt. tsc 0 Fehler, ESLint sauber.

### Schritt 4 — Altspalten deprecaten UMGESETZT (2026-06-02)

**Voraussetzung verifiziert:** Backfill vollständig für alle nicht-gelöschten Kunden (0 fehlende Adress-/Zahlungs-/Ref-Satelliten).

- **Migration `kunden_deprecate_legacy_cols_20260602`** (head): `COMMENT ON COLUMN` auf **30 Altspalten** von `public.kunden` (DEPRECATED-Marker + Pointer auf den Satelliten). Rein Metadaten, reversibel (downgrade setzt Kommentare auf NULL). **KEIN Drop** — Spalten bleiben als Fallback funktional.
  - Adresse (7) → `kunden_adressen`; Zahlung/Abrechnung (20) → `kunden_zahlung`; External Refs (3: webshop_kunden_nr/tankkarte_ean_code/kundenkarten_kennzeichen) → `kunden_external_refs`.
  - **Nicht** deprecated: Kern (kunden_nr/name*/gueltig_*/geloescht/sprachschluessel/Zeitstempel), Brücke (`business_partner_id`, `legacy_kunden_nr`), sowie noch nicht migrierte Domänen (Bank/Profil/Versand/Genossenschaft → vorhandene Satelliten, eigener Strang).
- **Beobachtbarkeit:** `BusinessPartnerService.get_customer_address/_payment/_external_refs` loggen `logger.warning(... deprecated)`, wenn sie auf `public.kunden` zurückfallen (Satellit fehlt) — bewiesen: feuert bei fehlendem Satelliten, schweigt bei vorhandenem.

### Schritt 5 — Vorbereitung: Identitätsbrücke business_partner_id ↔ kunden_nr (2026-06-02)

Brücke ist `public.kunden.business_partner_id` (per `kunden_merge --apply` gefüllt) + `domain_crm.customers`. Plumbing additiv aufgebaut (ohne Produktivmasken zu ändern, ohne FK zu aktivieren):

- **Resolver in `BusinessPartnerService`** (bidirektional, graceful): `partner_id_for_kunden_nr`, `kunden_nr_for_partner`, `kunden_nr_for_crm_customer` (via bp_id, sonst customer_number==kunden_nr), `resolve_customer_identity(*)` → Tripel `{kunden_nr, business_partner_id, partner_number, crm_customer_id}`.
- **Endpoints**: `GET /customers/lookup/resolve?kunden_nr=|business_partner_id=|crm_customer_id=` (Tripel) und `GET /customers/by-partner/{business_partner_id}/detail` (Brücke → kunden_nr → Satelliten-Detail; 404 wenn unverbrückt) — Enabler für die BP-keyed Kundenstamm-Maske.
- **Frontend-Hooks** (`lib/api/kunden-lookup.ts`): `useKundenIdentity`, `useKundenDetailByPartner`.
- **Readiness-Diagnostik**: `kunden_merge.bridge_status()` + CLI `python -m app.services.kunden_merge --bridge-status` → Abdeckung (bp_id gesetzt), per Match auflösbar, Orphans, FK-Orphans, `fk_ready`.

**Befund DEV:** Brücken-Abdeckung 0 % (Testdaten ohne Overlap: kunden_nr `K0000x` vs customer_number `KD-1000x` vs partner_number `BP-1000x`) → in Prod über `kunden_merge --apply` füllen.

**Noch offen (Schritt 5 Ausführung, separat mit DB-Backup + Freigabe):** `kunden_merge --apply` auf Prod (Brücke füllen) → `bridge_status` bis `fk_ready=True` → FK `public.kunden.business_partner_id → business_partners.partner_id` aktivieren → Produktivmasken (Combobox/Stamm) auf `resolve`/`by-partner/detail` umstellen → Reader-Fallback entfernen (0 Deprecation-Warnungen) → Altspalten **droppen**.

> **Prod-Ausführung:** vollständiges, phasenweises Runbook (Backup, Dry-Run-Review-Gates, `--apply`, FK-Aktivierung, Masken, Fallback-Entfernung, Drop, Rollback/Abbruch je Phase) in [`docs/runbooks/kunden-konsolidierung-schritt5.md`](runbooks/kunden-konsolidierung-schritt5.md).

**Funktionaler Durchstich (DEV, 2026-06-02):** Pfad `Dry-Run → --apply → --bridge-status` end-to-end fehlerfrei; auf Testdaten 0 geschrieben (kein Overlap), DB unverändert — Mechanik validiert.

## 7. Offen

- GAP `run_match`/`run_hydrate_customers` zeigen noch auf unqualifiziertes `customers` (skippen via Guard) → in Phase 2 auf die Schicht/`business_partner_id` umstellen.
- `domain_erp.business_partners` (8 Sp.) vs. `domain_crm.business_partners` (149) — Verhältnis klären (Fragment/Alt?).
- FK `public.kunden.business_partner_id → business_partners.partner_id` erst nach Backfill (Phase 2) aktivieren.
