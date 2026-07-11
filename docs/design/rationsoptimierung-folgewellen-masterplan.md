# Masterplan Folgewellen — Rationsoptimierung & Fütterungscontrolling

Stand: 2026-07-11 · Autor: Codex · Fachliche Grundlage: **DLG Information 01|2025**
„Rationsoptimierung und Fütterungskontrolle bei Milchkühen" (DLG-Arbeitskreis Futter &
Fütterung + GfE-Ausschuss für Bedarfsnormen, Stand 12/2025) sowie GfE 2023 / DLG-2025-
Futterwerttabellen. Aufsetzend auf den umgesetzten P0/P1/P2-Slices (siehe
`rationsoptimierung-usability-plan.md`).

Dieses Dokument plant **alle** Folgewellen vollständig: je Welle fachlicher Kontext mit
DLG-Referenz, Ziel, Datenmodell/API, UI, Abnahme und Aufwand. Die ausführbaren
Slice-Prompts liegen in `docs/design/prompts/rationsoptimierung-folgewellen-prompts.md`.

## Leitlinie

Das Tool ist fachlich bereits auf GfE-2023-/DLG-2025-Stand (ME-System, sidP, sidAA, RMD,
Strukturindex, HiGHS-Solver). Die Folgewellen heben es vom reinen **Rationsplaner** zum
vollständigen **Fütterungscontrolling-System** (DLG-Regelkreis Planung→Füttern→Kontrolle→
Anpassung) und schließen die letzten Fodjan-Lücken (Mischwagen/Ist-Erfassung, Mobil,
Effizienz-Cockpit) — mit fachlichem Vorsprung durch die exakte DLG-01|2025-Umsetzung.

Priorität: **Landhandel-/Genossenschaftsnutzen zuerst** (Berater + Landwirt), Medienbruch-
Reduktion (Ist-Daten automatisch), dann reine Maskenarbeit.

---

## Wellenübersicht

| Welle | Titel | DLG-Kap. | Prio | Aufwand | Typ |
|-------|-------|----------|------|---------|-----|
| **F1** | Fütterungscontrolling & Rationskontrolle (Regelkreis SOLL/IST) | 11, 12 | P1 | XL | Backend+Frontend |
| **F2** | Effizienz-Cockpit (Futter-/Energie-/Proteineffizienz) | 10 | P1 | M | Backend+Frontend |
| **F3** | Trockensteher/Transit + DCAB-Aggregat + Mineralbilanz | 9.2.2 | P1 | L | Backend+Frontend |
| **F4** | FAN-abhängige Passagerate/OMD/ME-Präzisierung | 4.3, 6.2 | P2 | L | Backend |
| **F5** | Schnittstellen: agrirouter (Mischwagen) + ICAR-ADE (LKV/MLP) + Labor | — | P2 | XL | Backend |
| **F6** | Mobile Dokumentations-Ansicht („jetzt füttern" / Ist-Erfassung) | 11 | P2 | L | Frontend |
| **F7** | ECM-Formel-Präzisierung + Formel-Audit-Regression | 10 | P0 | S | Backend |

Empfohlene Reihenfolge: **F7 → F2 → F3 → F1 → F6 → F4 → F5**
(F7 als schneller Formel-Fix zuerst; F2/F3 bauen auf vorhandenen Ergebnisfeldern auf;
F1 ist das große Controlling-Fundament, F6 dessen mobile Erfassung; F4/F5 sind tiefe
Solver-/Integrations-Themen).

---

## F7 — ECM-Formel-Präzisierung + Formel-Audit (P0, S)

### Fachlicher Kontext (DLG 01|2025, Kap. 10 / Abkürzungen)
Die DLG definiert ECM präzise mit **Fett, Protein und Laktose**:

```
ECM [kg] = kg Milch • (38,5 • Fett% + 24,2 • Protein% + 16,5 • Laktose%) ÷ 3,15 ÷ 100
```

(Milch-Energiegehalt 3,15 MJ/kg; Protein = Protein-N • 6,38). Unsere Frontend-Näherung in
`rationsoptimierung/app/nutrition/gfe2023.py` nutzt `ECM ≈ Milch • (0,337 + 0,116•Fett% +
0,06•Eiweiß%)` — **ohne Laktose** und mit älteren Koeffizienten. Für Hochleistungstiere und
das Effizienz-Cockpit (F2) ist die exakte Formel relevant.

### Umfang
- ECM-Funktion in `gfe2023.py` (Standalone-Service) und im Backend-Modul `app/agrar/rations`
  auf die DLG-Formel umstellen; Laktose als Eingabe (Default 4,8 %, DLG-ECM-Referenz).
- **Formel-Audit-Regression:** Test, der die zentralen Formeln (ECM, ME-Erhaltung, sidP,
  DCAB) gegen die DLG-01|2025-Referenzwerte prüft; verhindert künftige Drift.
- CowProfile um optional `milk_lactose_pct` erweitern (Default 4,8).

### Abnahme
- `pytest` neuer Formel-Audit grün; ECM(4,0/3,4/4,8) reproduziert DLG-Referenz.
- Bestehende Rations-Tests bleiben grün (Regression).

---

## F2 — Effizienz-Cockpit (P1, M)

### Fachlicher Kontext (DLG 01|2025, Kap. 10)
DLG nennt vier State-of-the-Art-Effizienzkennzahlen (nur Energie-/Nährstoff-basiert sind
aussagekräftig, reine Futtereffizienz nicht):

- **Futtereffizienz** = kg ECM ÷ kg TM-Aufnahme
- **Energieeffizienz** = MJ Milchenergie ÷ MJ ME-Aufnahme (bzw. **kg ECM ÷ 10 MJ ME**)
- **Proteineffizienz** = g Milchprotein ÷ kg CP-Aufnahme (= % des Futter-CP in der Milch)
- **Körpermasseeffizienz** = kg ECM ÷ kg KM (bzw. kg^0,75)

Beispiel DLG: 700 kg, 23 kg TM, 32 kg ECM, FAN 3,4 → Futtereffizienz 1,4; Energieeffizienz
1,35 vs. 1,29 kg ECM/10 MJ ME zeigt, dass die Kuh mit niedrigerer Energiedichte effizienter ist.

### Umfang
- Backend liefert bereits `ecm_supply_kg_day`, `total_cost_eur_day`, `nutrient_supply`
  (me_mj, sidp_g, cp_g). Effizienzkennzahlen daraus im Endpoint berechnen und als
  `efficiency`-Block in die Antwort geben (Futter-, Energie-, Protein-, KM-Effizienz).
- Frontend: Effizienz-Panel/Kacheln in der Workbench (neben Kennzahlen-Trio), mit
  Orientierungswerten (Ampel), und Einbindung in Review/Export.

### Datenmodell/API
`OptimizationResult.efficiency = { feed_efficiency_kg_ecm_per_kg_dm, energy_efficiency_mj_per_mj,
energy_efficiency_kg_ecm_per_10mj, protein_efficiency_pct, bodymass_efficiency_kg_ecm_per_kg }`.

### Abnahme
- Endpoint-Test reproduziert DLG-Beispiel (1,4 / 1,35 / 1,29).
- Frontend `tsc`/`eslint`/`build` grün; Panel zeigt die vier Kennzahlen mit Ampel.

---

## F3 — Trockensteher/Transit + DCAB-Aggregat + Mineralbilanz (P1, L)

### Fachlicher Kontext (DLG 01|2025, Kap. 9.2.2)
- Trockensteher-Bedarf gestaffelt: **far-off** (6.–4. Wo, KM 760) ≈ 115 MJ ME / 1.050 g sidP;
  **close-up/Transit** (3. Wo–Kalbung, KM 790) ≈ 126 MJ ME / 1.177 g sidP. Toleranz 10 MJ ME
  und 100–150 g sidP/Tier/Tag. In NEB/Frühlaktation Mineralstoff **+10–15 %**.
- **DCAB** (Gebärpareseprophylaxe close-up): `DCAB = (Na+ + K+) − (Cl− + S2−)` [meq/kg TM];
  K/Na/Cl/S **müssen analysiert** sein. Konzepte: Ca-arm / K-arm / moderate DCAB-Absenkung /
  anionische Fütterung (saure Salze); K möglichst < 12 g/kg TM; steigende Ca bei sinkender
  DCAB. Kontrolle über **Harn-pH < 6,5**.
- Makroelemente in der DLG-Futterwerttabelle 2025 (Ca/P/Na/Mg/K/S/Cl, 0,01 % iTM) liegen vor
  → exakte Mineralbilanz statt Näherung.

### Umfang
- **DCAB-Rations-Aggregat** im Endpoint aus Na/K/Cl/S je Futtermittel berechnen und als
  Kennzahl + Restriktion (close-up-Zielband, z.B. negativ/anionisch) ausgeben; Harn-pH-Hinweis.
- **Trockensteher-Profile** far-off/close-up mit exaktem ME/sidP-Bedarf (Tab. 11) und
  Toleranzbändern; NEB-Mineralaufschlag +10–15 %.
- **Mineralbilanz** Ca/P/Mg/K/S/Na/Cl aus DLG-Werten statt Näherung
  (`minerals_ca_p_na_g` ablösen); Anzeige als Bilanz-Panel.

### Abnahme
- Endpoint reproduziert Tab.-11-Bedarfe im Toleranzband; DCAB-Aggregat gegen Handrechnung geprüft.
- Frontend zeigt DCAB + Mineralbilanz + Harn-pH-Hinweis für Trockensteher-Gruppe.

---

## F1 — Fütterungscontrolling & Rationskontrolle (P1, XL)

### Fachlicher Kontext (DLG 01|2025, Kap. 11 + 12)
Der **Regelkreis** Planung(SOLL) → Füttern → Kontrolle(IST) → Anpassung (Abb. 9) ist der
Kern der DLG-Empfehlung — und genau Fodjans „Fütterungscontrolling"-Stärke. Kontrollpunkte:

- **Kontrolle der Futtervorlage** über das tägliche **Mischwagenprotokoll** (geladene
  Ist-Mengen je Komponente).
- **TM-Verzehr je Kuh** = (vorgelegte Menge − Restfutter) • TM% ÷ Tierzahl der Gruppe.
- **Mischgenauigkeit** — Abweichung Ist-Ladung vs. Soll **< 5 %** je Komponente.
- **Homogenität/Strukturwirksamkeit** via **PennState-Schüttelbox** (3-/4-stufig, Siebe
  19+8 mm), mind. 3 Stellen; strukturwirksam = Anteil **> 8 mm**; Obersieb = Entmischungs-/
  Selektionsrisiko. Abgleich mit peNDF-Soll aus der Rationsberechnung.
- **Nacherwärmung** (Futtertisch-Temperatur) = Nährstoffverlust/Verzehrsminderung.
- **IOFC-Controlling** (Kap. 12): `IOFC = Milchmenge•Milcherlös − Futterkosten` je Kuh;
  Futterkosten/kg Milch; Konzentrataufwand g/kg ECM — als Zeitreihe.

### Umfang (mehrere Sub-Slices)
1. **Datenmodell Ist-Fütterung**: Fütterungsprotokoll je Gruppe/Tag (Soll-Ration-Ref,
   geladene Ist-Mengen je Komponente, Restfutter, Tierzahl, TM%-Messung).
2. **SOLL/IST-Abgleich**: Mischgenauigkeit je Komponente + gesamt (< 5 % Ampel), TM-Verzehr/
   Kuh, Delta zur berechneten Ration.
3. **Schüttelbox-Erfassung**: 3-/4-stufige Siebanteile eingeben, peNDF-Ist vs. Soll,
   Entmischungs-/Selektionshinweis; Futterrest-Schüttelung optional.
4. **Controlling-Dashboard**: IOFC-Zeitreihe, Futterkosten/kg Milch, Konzentrataufwand,
   Nacherwärmungs-Log.

### Datenmodell/API (neu)
`feeding_log` (Gruppe, Datum, ration_ref, geladene[], restfutter_kg, tierzahl, tm_pct_gemessen,
schuettelbox[], futtertisch_temp) → Read-Model `feeding_control` (mischgenauigkeit_pct,
tm_verzehr_kg, iofc_eur, peNDF_ist, warnungen[]). Neue Endpoints unter
`/api/v1/agrar/rations-optimization/feeding-control`.

### Abnahme
- Ist-Protokoll persistiert und liefert Mischgenauigkeit/TM-Verzehr/IOFC korrekt (Handrechnung).
- Schüttelbox-Abgleich peNDF-Ist vs. Soll mit Ampel.
- Regelkreis in der UI sichtbar (SOLL vs. IST vs. Anpassungsvorschlag).

---

## F6 — Mobile Dokumentations-Ansicht (P2, L)

### Fachlicher Kontext
Fodjan-App-Parität: On-farm-Erfassung ohne Solver. DLG Kap. 11: „nur die aufgenommene
Menge/Ist erfassen". Fressplatzbreite-Hinweis 80–85 cm (min 75) als Kontroll-Checkliste.

### Umfang
- Schlanke mobile Route: aktive Ration ansehen → „jetzt füttern" → Ist-Mengen erfassen
  (speist F1), Schüttelbox mobil, Restfutter/TM-Schnellmessung. Kein Solver am Handy.
- Baut auf F1-Datenmodell + der bereits umgesetzten responsiven Workbench (RESPONSIVE-004) auf.

### Abnahme
- Mobile Erfassung schreibt ins `feeding_log`; Kern-Flow auf Smartphone ohne horizontales Body-Scroll.

---

## F4 — FAN-abhängige Passagerate/OMD/ME-Präzisierung (P2, L)

### Fachlicher Kontext (DLG 01|2025, Kap. 4.3, 6.2, Tab. 6)
Das **Futteraufnahmeniveau (FAN)** senkt OMD/ME (schnellere Passage). Die **Passagerate k
[%/h]** steigt linear mit FAN und ist futtermittelgruppen-abhängig (Grobfutter < Misch/Saft
< Konzentrat; z.B. Grobfutter FAN1=2,6 / FAN3=4,4). Stufenlose k- und OMD/ME-FAN-Gleichungen
stehen in **DLG (2025c)** für die computergestützte Optimierung. EDG/UDP steigen mit Leistung.

### Umfang
- FAN-abhängige k je Futtermittelgruppe (Tab. 6 + DLG-2025c-Gleichungen) im Solver/Aggregator;
  OMD/ME-FAN-Korrektur der Rations-Energie; EDG/UDP FAN-abhängig.
- Bereits vorhandene FAN-Mode-Infrastruktur (`fanMode`, `FAN_REFERENCE_PRESETS`) nutzen.

### Abnahme
- k/OMD/ME reproduzieren DLG-2025c-Gleichungen für Referenz-FAN; Solver-Regression grün.

---

## F5 — Schnittstellen: agrirouter + ICAR-ADE + Labor (P2, XL)

### Fachlicher Kontext (Zukunftsrecherche 2026-07-10)
- **agrirouter** (DKE-Data; ISOXML, EFDI, MQTT/HTTP): herstellerübergreifender Import der
  **Mischwagen-Ist-Mengen** (BvL, Siloking, Strautmann, PTM) → speist F1-Controlling.
- **ICAR-ADE** (Animal Data Exchange, JSON/REST — Nachfolger ISOagriNET): **LKV/MLP-Daten**
  (Milchleistung, Milchharnstoff, Fett/Eiweiß/Laktose) → Kuhprofil + Effizienz (F2) + sidP-
  Kontrolle (Milchharnstoff, DLG Kap. 6.3/9.2.2).
- **Labor-Analyseformate** (LKS, LUFA, Eurofins): Futteranalysen je Charge/Silo (Compound-
  Upload existiert bereits, erweitern).

### Umfang
- Adapter-Muster (JSON/REST-first, ICAR-ADE-kompatibel); Import mündet in bestehende Modelle
  (`CowProfile`, `FeedIngredient`, `feeding_log`), kein paralleler Datenpfad.
- Reihenfolge: Labor-Import (kleinste) → Mischwagen via agrirouter (speist F1) → LKV/MLP via
  ICAR-ADE.

### Abnahme
- Je Adapter ein Import-Test mit Beispiel-Payload; importierte Werte landen korrekt im Zielmodell.

---

## Querschnitt: Governance & Qualität

Jede Welle wird in Sub-Slices nach AI-Harness-Workflow abgearbeitet (Claim → YAML → Code →
Abschluss; `docs/agent-ops/`). Invarianten aus `CLAUDE.md` (Mutation-Lifecycle, Async-Handler,
Fehlerbehandlung) gelten. Backend-Wellen mit `pytest`; Frontend mit `tsc`/`eslint`/`build` und
E2E-Smoke. Fachliche Formeln immer gegen DLG 01|2025 / GfE 2023 verankern (Formel-Audit aus F7).
