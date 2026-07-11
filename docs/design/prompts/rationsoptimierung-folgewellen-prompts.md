# Ausführbare Slice-Prompts — Folgewellen Rationsoptimierung

Stand: 2026-07-11 · Grundlage: `docs/design/rationsoptimierung-folgewellen-masterplan.md`,
DLG Information 01|2025, GfE 2023, DLG-Futterwerttabellen 2025.

Jeder Prompt ist self-contained und folgt dem AI-Harness-Workflow: **Claim → YAML → Code →
Abschluss**, mit lokaler Verifikation vor Push und Governance-Checks
(`node scripts/docs-governance-check.cjs`, `node scripts/ai-slice-readiness-check.cjs --slice <ID>`).
Backend: `pytest` (nutze bei conftest-Hang `--noconftest -p no:cacheprovider --no-cov -o addopts=""`).
Frontend: `pnpm --filter frontend-web exec tsc --noEmit`, `eslint`, `pnpm run build`; danach
`docker compose build frontend-web && docker compose up -d frontend-web` für Live-Verifikation.

Nach jedem Slice: commit + `git push origin main`, dann CI-Gates via `gh run list --commit <sha>`
abwarten (grün).

---

## Prompt F7 — ECM-Formel-Präzisierung + Formel-Audit

**Slice-ID:** `RATIONS-SCI-ECM-006` · **Prio P0** · **Aufwand S** · **Typ Backend**

> Setze die energiekorrigierte Milch (ECM) im Rations-Backend auf die exakte DLG-01|2025-Formel
> um: `ECM[kg] = kg Milch • (38,5•Fett% + 24,2•Protein% + 16,5•Laktose%) ÷ 3,15 ÷ 100`
> (Protein = Protein-N • 6,38; Milch-Energiegehalt 3,15 MJ/kg). Betroffen:
> `rationsoptimierung/app/nutrition/gfe2023.py` (`energy_corrected_milk_kg`) und die ECM-Nutzung
> im Backend-Modul `app/agrar/rations` bzw. `app/api/v1/endpoints/rations_optimization.py`.
> Ersetze die alte Näherung `0,337 + 0,116•Fett% + 0,06•Eiweiß%` (ohne Laktose). Erweitere
> `CowProfile` um optionales `milk_lactose_pct` (Default 4,8). Lege eine **Formel-Audit-
> Regression** an (`rationsoptimierung/tests/test_formula_audit_dlg2025.py`), die ECM, ME-
> Erhaltung (0,64•KM^0,75), sidP-Näherung und DCAB gegen die DLG-01|2025-Referenzwerte prüft
> (ECM-Beispiel: 4,0% Fett / 3,4% Protein / 4,8% Laktose). Halte alle bestehenden Rations-Tests
> grün. Dateibesitz: `rationsoptimierung/app/nutrition/gfe2023.py`,
> `rationsoptimierung/app/schemas/`, `rationsoptimierung/tests/test_formula_audit_dlg2025.py`,
> ggf. `app/api/v1/endpoints/rations_optimization.py`. Abnahme: neuer Audit-Test + bestehende
> Suite grün; ECM reproduziert die DLG-Definition.

---

## Prompt F2 — Effizienz-Cockpit

**Slice-ID:** `RATIONS-SCI-EFF-007` · **Prio P1** · **Aufwand M** · **Typ Backend+Frontend**

> Ergänze die vier DLG-01|2025-Effizienzkennzahlen (Kap. 10) im Rations-Endpoint und zeige sie
> als Cockpit in der Workbench. Berechne aus vorhandenen Feldern (`ecm_supply_kg_day`,
> `nutrient_supply.me_mj`, `nutrient_supply.cp_g`, `total_cost_eur_day`, `dmi_kg`, Milchprotein,
> KM): **Futtereffizienz** = kg ECM/kg TM; **Energieeffizienz** = MJ Milchenergie/MJ ME sowie
> kg ECM/10 MJ ME; **Proteineffizienz** = g Milchprotein/kg CP-Aufnahme (%); **Körpermasse-
> effizienz** = kg ECM/kg KM. Gib sie als `efficiency`-Block in `OptimizationResult` aus.
> Frontend: Effizienz-Panel/Kacheln in der Workbench (neben dem Kennzahlen-Trio) mit
> Orientierungs-Ampel; in Review/Export einbinden. Verifiziere den DLG-Beispiel-Datensatz
> (700 kg, 23 kg TM, 32 kg ECM, 10,3 vs. 10,8 MJ ME/kg → Futtereffizienz 1,4; Energieeffizienz
> 1,35 vs. 1,29 kg ECM/10 MJ ME). Dateibesitz: `app/api/v1/endpoints/rations_optimization.py`
> (oder `app/agrar/rations/response/aggregator.py`), `packages/frontend-web/src/lib/api/
> rations-optimization.ts`, `packages/frontend-web/src/pages/futtermittel/rationsoptimierung.tsx`.
> Abnahme: Endpoint-Test reproduziert das DLG-Beispiel; Frontend `tsc`/`eslint`/`build` grün.

---

## Prompt F3 — Trockensteher/Transit + DCAB-Aggregat + Mineralbilanz

**Slice-ID:** `RATIONS-SCI-DRYCOW-008` · **Prio P1** · **Aufwand L** · **Typ Backend+Frontend**

> Setze die DLG-01|2025-Trockensteherversorgung (Kap. 9.2.2) exakt um. (1) **Trockensteher-
> Profile** far-off (6.–4. Wo) und close-up/Transit (3. Wo–Kalbung) mit gestaffeltem ME/sidP-
> Bedarf nach Tab. 11 (far-off ≈ 115 MJ ME/1.050 g sidP bei KM 760; close-up ≈ 126 MJ ME/
> 1.177 g sidP bei KM 790) und Toleranzbändern (10 MJ ME, 100–150 g sidP); Mineralstoffaufschlag
> +10–15 % in NEB/Frühlaktation. (2) **DCAB-Rations-Aggregat**: `DCAB = (Na+ + K+) − (Cl− + S2−)`
> [meq/kg TM] aus Na/K/Cl/S je Futtermittel; als Kennzahl + optionale Restriktion (close-up
> anionisches Zielband, K möglichst < 12 g/kg TM, steigende Ca bei sinkender DCAB); Hinweis
> Harn-pH < 6,5 als Kontrolle. (3) **Mineralbilanz** Ca/P/Mg/K/S/Na/Cl aus den DLG-2025-
> Futterwerten statt der Näherung `minerals_ca_p_na_g`; Anzeige als Bilanz-Panel. Nutze die
> vorhandenen DLG-Felder (`dcab`, `mg`, `k`, `s`, `cl`, `ca`, `p`, `na` je Feed). Dateibesitz:
> `app/api/v1/endpoints/rations_optimization.py`, `app/agrar/rations/`, `rationsoptimierung/`
> (falls dort gespiegelt), Frontend api-lib + Page. Abnahme: Endpoint reproduziert Tab.-11-
> Bedarfe im Toleranzband; DCAB-Aggregat gegen Handrechnung; Frontend zeigt DCAB + Mineralbilanz
> + Harn-pH-Hinweis für die Trockensteher-Gruppe.

---

## Prompt F1 — Fütterungscontrolling & Rationskontrolle (Regelkreis)

**Slice-ID-Familie:** `RATIONS-CTRL-009..012` · **Prio P1** · **Aufwand XL** · **Typ Backend+Frontend**
> Große Welle — in vier Sub-Slices abarbeiten, je eigener Claim/YAML/Push.

**F1a `RATIONS-CTRL-009` Datenmodell Ist-Fütterung.**
> Lege ein Fütterungsprotokoll-Datenmodell an (`feeding_log`): Gruppe, Datum, Referenz auf die
> berechnete Soll-Ration, geladene Ist-Mengen je Komponente, Restfutter (kg), Tierzahl,
> gemessene TM% der Vorlage, optional Schüttelbox-Siebanteile und Futtertisch-Temperatur.
> Alembic-Migration (Single-Head je Slice), SQLAlchemy-Modell, CRUD-Endpoints unter
> `/api/v1/agrar/rations-optimization/feeding-control`. Abnahme: `pytest` CRUD-Roundtrip grün.

**F1b `RATIONS-CTRL-010` SOLL/IST-Abgleich (DLG Kap. 11).**
> Read-Model `feeding_control`: **TM-Verzehr/Kuh** = (vorgelegt − Restfutter)•TM% ÷ Tierzahl;
> **Mischgenauigkeit** je Komponente + gesamt (Abweichung Ist vs. Soll, Ampel bei > 5 %);
> Delta zur berechneten Ration. Endpoint + Frontend-Panel „Rationskontrolle" (SOLL vs. IST).
> Abnahme: Mischgenauigkeit/TM-Verzehr gegen Handrechnung; Ampel < 5 %.

**F1c `RATIONS-CTRL-011` Schüttelbox-/peNDF-Ist-Abgleich (DLG Kap. 8.2/11).**
> Erfassung 3-/4-stufige PennState-Siebanteile (Siebe 19+8 mm); strukturwirksam = Anteil > 8 mm;
> peNDF-Ist vs. peNDF-Soll aus der Rationsberechnung; Obersieb-Anteil als Entmischungs-/
> Selektionsrisiko-Hinweis; optional Futterrest-Schüttelung. Abnahme: peNDF-Ist/Soll-Vergleich
> mit Ampel; Selektionshinweis korrekt.

**F1d `RATIONS-CTRL-012` Controlling-Dashboard (DLG Kap. 12).**
> IOFC-Zeitreihe (`IOFC = Milchmenge•Milcherlös − Futterkosten` je Kuh), Futterkosten/kg Milch,
> Konzentrataufwand g/kg ECM, Nacherwärmungs-Log. Frontend-Dashboard mit Verlauf. Abnahme:
> Kennzahlen reproduzieren Handrechnung; Verlauf rendert; `tsc`/`eslint`/`build` grün.

---

## Prompt F6 — Mobile Dokumentations-Ansicht

**Slice-ID:** `RATIONS-UX-MOBILE-013` · **Prio P2** · **Aufwand L** · **Typ Frontend**
> Voraussetzung: F1a (feeding_log).

> Baue eine schlanke mobile Route (Fodjan-App-Parität) für die On-farm-Dokumentation, aufsetzend
> auf der bereits responsiven Workbench (RESPONSIVE-004): aktive Ration ansehen → „jetzt füttern"
> → Ist-Mengen je Komponente erfassen (nur aufgenommene Menge; Rest automatisch), Restfutter/
> TM-Schnellmessung, Schüttelbox mobil — schreibt ins `feeding_log` (F1a). Kein Solver am Handy.
> Fressplatzbreite-Checkliste (80–85 cm, min 75) als Kontroll-Hinweis. Mutation-Lifecycle-
> Invarianten beachten (Guard, disabled, finally-Reset, Toast). Dateibesitz: neue mobile
> Page/Route unter `packages/frontend-web/src/pages/portal/` + api-lib. Abnahme: Erfassung
> persistiert im feeding_log; Kern-Flow auf Smartphone ohne horizontales Body-Scroll;
> `tsc`/`eslint`/`build` grün.

---

## Prompt F4 — FAN-abhängige Passagerate/OMD/ME-Präzisierung

**Slice-ID:** `RATIONS-SCI-FAN-014` · **Prio P2** · **Aufwand L** · **Typ Backend**

> Präzisiere die Rations-Energie nach DLG 01|2025 (Kap. 4.3, 6.2, Tab. 6): FAN-abhängige
> **Passagerate k [%/h]** je Futtermittelgruppe (Grobfutter < Misch/Saft < Konzentrat; Tab. 6
> plus stufenlose Gleichungen aus DLG 2025c) und die **OMD/ME-FAN-Korrektur** (höheres FAN senkt
> Verdaulichkeit/ME); EDG/UDP FAN-abhängig. Nutze die vorhandene FAN-Mode-Infrastruktur
> (`fanMode`, `FAN_REFERENCE_PRESETS`, `fan_calibration`). Dateibesitz: `app/agrar/rations/solver/`,
> `app/agrar/rations/response/aggregator.py`, `app/api/v1/endpoints/rations_optimization.py`.
> Abnahme: k/OMD/ME reproduzieren die DLG-2025c-Referenz für definierte FAN-Stufen; Solver-
> Regression grün. Hinweis: DLG-2025c-Gleichungen beschaffen/verankern, keine freien Schätzungen.

---

## Prompt F5 — Schnittstellen (agrirouter + ICAR-ADE + Labor)

**Slice-ID-Familie:** `RATIONS-INT-015..017` · **Prio P2** · **Aufwand XL** · **Typ Backend**
> Drei Adapter, JSON/REST-first, Import mündet in bestehende Modelle — kein paralleler Datenpfad.

**F5a `RATIONS-INT-015` Labor-Analyse-Import.**
> Erweitere den bestehenden Compound-Feed-/Analyse-Import um Standard-Laborformate (LKS, LUFA,
> Eurofins) je Charge/Silo → `FeedIngredient`/Betriebsanalysen. Abnahme: Import-Test mit
> Beispiel-Payload; Werte korrekt gemappt (inkl. sidAA/DCAB-Felder wo geliefert).

**F5b `RATIONS-INT-016` Mischwagen-Import via agrirouter.**
> agrirouter-Adapter (DKE-Data; ISOXML/EFDI, MQTT/HTTP) für geladene Mischwagen-Ist-Mengen
> (BvL/Siloking/Strautmann/PTM) → speist das `feeding_log` aus F1a. Abnahme: Beispiel-ISOXML/
> EFDI-Payload landet als Ist-Ladung im feeding_log.

**F5c `RATIONS-INT-017` LKV/MLP-Import via ICAR-ADE.**
> ICAR-ADE-Adapter (Animal Data Exchange, JSON/REST — Nachfolger ISOagriNET) für Milchleistung/
> Milchharnstoff/Fett/Eiweiß/Laktose → `CowProfile` (speist F2-Effizienz und F7-ECM-Laktose)
> und sidP-Kontrolle über Milchharnstoff (DLG Kap. 6.3/9.2.2). Abnahme: Beispiel-ICAR-ADE-
> Payload aktualisiert Kuhprofil + Kontroll-Kennzahlen.

---

## Reihenfolge-Empfehlung

**F7 → F2 → F3 → F1(a–d) → F6 → F4 → F5(a–c).**
F7 liefert die korrekte ECM-Basis für F2/F3; F1 ist das Controlling-Fundament, das F6 (mobil)
und F5b (Mischwagen) füllt; F4/F5 sind die tiefen Solver-/Integrations-Themen zuletzt.
