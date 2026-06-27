---
title: Rationsoptimierung GfE-2023 / FAN1-FANi Spezifikation
type: reference
audience: [entwickler, product]
owner: Claude Code
status: umgesetzt
last_reviewed: 2026-06-27
version: 3.0.0
description: Freigegbene V1-Spezifikation fuer Rationsoptimierung auf GfE-2023-Basis — FAN1/FANi-Proteinbewertung, DLG-Referenzwerte und Fruehjahrsweidekorrekturen (Stand 2026-04-21, Slice RAT-OPT-001).
---

# Rations-Optimierung auf GfE-2023 / FAN1 ⇄ FANi

Stand: `2026-04-21`
Status: **freigegeben für Umsetzung V1** (§11.1)
Autor: Codex
Kontext: Folgt auf `RAT-OPT-001` und schließt die Fruehjahrsweide-Praxisprobe (`PMR+Weide`) inhaltlich ab. Basis ist die GfE-2023-Proteinbewertung und die DLG-Umsetzungen (DLG 01|2025, DLG 443, DLG 444, DLG 417, DLG 503, DLG 504, GfE-Workshop „Digitale Umsetzung zifo2" Rauch 2026).

## Bestätigte V1-Defaults (Stand 2026-04-21)

Diese Werte sind freigegeben und gelten als Default für alle folgenden Slices:

```text
fan_mode                   default = auto_iterative
fan_reference_presets              = [2.5, 3.0, 3.5]  (+ Freiwert 2.0–5.0)
fan_tolerance              default = 0.05
fan_tolerance_warn         default = 0.10
fan_max_iterations         default = 5
relaxation_policy          default = standard          (strict ×3 / standard ×1 / soft ×0.3)
penalty_base_cost                  = 1.0 EUR/normierte Einheit
penalty_class_weights              = { A: 10, B: 3, C: 1 }
season_profile             default = null              (Vorschlag mit Bestätigungs-Klick im UI)
block_policy_profiles              = tmr_standard | pmr_standard | pmr_pasture_spring
fan_slope_catalog                  = app/config/fan_slope_catalog.json (flags: exact | mapped | fallback)
```

## 1. Ziel

Die Rationsoptimierung soll fachlich sauber, aber numerisch robust sein.
Der bisherige einstufige LP-Ansatz mit fixen DLG-Richtwerten ist dafür zu starr:

- Futterwerttabellen führen Energie auf **FAN1**; reale Aufnahme ist aber **FANi** (Vielfaches des Erhaltungsbedarfs)
- GfE-2023 führt FAN zusätzlich über die Passagerate `k` in die Proteinbewertung ein (DLG 504)
- Weide- und PMR-Systeme haben strukturell andere Leitplanken als Stall-TMR (DLG 417/443)
- Starre Hart-Grenzen erzeugen `infeasible`, wo fachlich nur eine Toleranzabweichung vorliegt

Der neue Stand trennt daher sauber:

1. **FAN1 als Futterwert-Anker** — der Wert bleibt im Futtermittel fix
2. **FANi als Rations-Anker** — wird je Tier/Leistungsgruppe festgelegt und wirkt auf ME- und Protein-Koeffizienten
3. **Solver-Modus** — entweder iterativ (FAN wird aus Ergebnis zurückgerechnet) oder mit fixiertem Referenz-FAN
4. **Harte vs. weiche Constraints** — nur echte Sicherheitsgrenzen hart, alle Komfortbänder weich mit Strafkosten

## 2. Fachliche Grundlagen (kurz, mit Referenzen)

| Thema | Quelle | Kerninhalt |
|---|---|---|
| FAN1-Ausweisung in Futterwerttabellen | DLG-Futterwerttabelle 2023, DLG 503 | Energie- und Proteinwerte sind auf FAN1 bezogen |
| FAN → Passagerate `k` → sidP | DLG 01|2025, DLG 504, GfE-Workshop 2026 | `k` = f(FAN, Futterart); wirkt auf UDP / sidP |
| Grundration → Ergänzung → Mineral | DLG 01|2025 | Planungs-Reihenfolge: erst GF, dann KF, dann Mineral, dann Prüfung |
| peNDF-, Strukturindex-, RMD-Kontrolle | DLG 01|2025 Tab. 14, DLG 443 | Struktur- und N-Effizienz sind Toleranzbänder, nicht Harte Grenzen |
| K:Mg-Antagonismus bei Weide | DLG 417, GfE-Workshop 2023 | Grastetanie-Risiko; Mg/Na-Ausgleich im Frühjahr |
| Saisonale Weideprofile | DLG-Futterwerttabelle 2023 | Frühjahr jung / mittel / älter / Sommer jung / älter |

Wo die DLG keine 1:1-Formel vorgibt (z. B. Abbruchschwelle für FAN-Iteration, konkrete Straftermhöhen), ist die Software-Implementierung explizit als **Näherung** zu kennzeichnen.

## 3. Datenvertrag

### 3.1 `CowProfile` (Erweiterung, abwärtskompatibel)

| Feld | Typ | Pflicht | Default | Bedeutung |
|---|---|---|---|---|
| `feeding_type` | `TMR` \| `PMR` \| `PMR+Weide` | nein | `TMR` | unverändert |
| `season_profile` | `spring_young` \| `spring_mid` \| `spring_late` \| `summer_young` \| `summer_late` \| `autumn` \| `winter` \| `null` | nein | `null` | steuert Weidekatalog-Default bei `PMR+Weide` |
| `fan_mode` | `auto_iterative` \| `reference` \| `evaluation_only` | nein | `auto_iterative` | neu |
| `fan_reference` | `number (2.0–5.0)` \| `null` | nein | `null` | bei `reference` verpflichtend |
| `fan_tolerance` | `number` | nein | `0.05` | erlaubte Abweichung (FANi_start ↔ FANi_out) für Abbruch der Auto-Iteration (freigegeben 2026-04-21) |
| `fan_tolerance_warn` | `number` | nein | `0.10` | UI-Warnschwelle: Hinweis, wenn die letzte Iteration noch > 0.10 lag |
| `fan_max_iterations` | `int` | nein | `5` | harter Iterationsdeckel (freigegeben 2026-04-21) |

Validierung:
- `fan_mode == "reference"` ohne `fan_reference` → `HTTP 422`
- `fan_reference` außerhalb [2.0, 5.0] → `HTTP 422`
- `season_profile` nur wirksam bei `feeding_type == "PMR+Weide"` (wird sonst ignoriert, kein Fehler)

### 3.2 Request-Erweiterung `/optimize`, `/optimize/from-profile`

- zusätzlich `relaxation_policy`: `"strict"` \| `"standard"` \| `"soft"` (default `"standard"`) — steuert, welche Constraints als weich laufen.
- zusätzlich `objective_strategy`: `"balance_then_cost"` (default) \| `"cost_only"` \| `"balance_only"` — entspricht Stufen im Solver.

### 3.3 Response-Erweiterung

Zusätzlich zu `ration_items`, `nutrient_supply`, `forage_performance`, `pasture_risk`:

```json
"fan_calibration": {
  "mode": "auto_iterative",
  "iterations": 3,
  "fan_start": 2.4,
  "fan_final": 2.58,
  "converged": true,
  "tolerance": 0.2,
  "warnings": []
},
"constraint_status": {
  "hard_violations": [],
  "soft_violations": [
    {"name": "pendf_min", "gap": 8.2, "unit": "g/kg TM", "penalty_cost": 0.12}
  ]
}
```

## 4. Betriebsarten / UI-Modi

### 4.1 `auto_iterative` (Standard)

1. Schätze Start-FAN aus `milk_kg_day`, `body_weight_kg`, `lactation_stage_days`.
2. Leite FAN-abhängige Koeffizienten ab (ME-Anpassung, k-Passagerate für UDP/sidP).
3. Löse LP (Stage 1 Balance → Stage 2 Kosten).
4. Berechne effektives FANi_out aus Ergebnis-DMI und Tier-Erhaltungsbedarf.
5. Bei `|FANi_out − FANi_in| > fan_tolerance` → FAN_in := FANi_out, zurück zu 2.
6. Abbruch bei Konvergenz oder `fan_max_iterations`; bei Nicht-Konvergenz: letzte gültige Lösung + Warnung.

### 4.2 `reference`

FAN wird aus `fan_reference` fix übernommen, keine Iteration. Verwendet für Beratung, Fehlersuche und stabile LP-Rechnungen. Ergebnis ist deterministisch.

Im UI stehen drei schnell wählbare Referenzstufen zur Auswahl, plus Freiwert (freigegeben 2026-04-21):

| Stufe | FAN-Wert | Einsatzprofil |
|---|---|---|
| niedrig | 2,5 | Spätlaktation, Trockensteher-nah, leichte Herden |
| mittel | 3,0 | Mittellaktation, mittlerer Leistungsstand |
| hoch | 3,5 | Frühlaktation, hohe Leistung |
| frei | 2,0 – 5,0 | Beratung / Kalibrierung |

Begründung (aus DLG 503 / 504): Der praxisrelevante Bereich liegt etwa zwischen FANi 2,5 und 4,0; dort ändert sich ME um bis zu 0,44 MJ/kg TM, und die Passagerate `k` verschiebt die Proteinbewertung linear. Drei grobe Stufen decken diesen Bereich ab, ohne die UI zu überladen; feinere Kalibrierung geschieht über den Freiwert.

### 4.3 `evaluation_only`

Keine Optimierung. Die übergebene Feed-Liste wird mit den angegebenen Mengen (aus `fixed_amounts_kg_tm`) bewertet. Output enthält `nutrient_supply`, `constraint_status`, aber kein LP-Ergebnis. Wird für „rechne durch, was der Bruder heute füttert" genutzt.

## 5. Solver-Stufen und Constraint-Klassifikation

### 5.1 Stufen

- **Stage A** — **hart feasible**: nur die Sicherheitsgrenzen (siehe 5.2).
- **Stage B** — **balance**: zusätzlich alle weichen Constraints als Zielfunktion mit ℓ1-Straftermen; minimiere Σ penalty_i × slack_i.
- **Stage C** — **cost**: bei `objective_strategy == "balance_then_cost"` wird das balance-Optimum als zusätzliche Hart-Obergrenze eingefroren (Slack ≤ balance_opt × 1.05) und jetzt Kosten minimiert.

Dieser Aufbau ersetzt die jetzige 2-stufige `_run_lp`. Die bestehenden Regressionstests bleiben stabil, weil `balance_then_cost` Default bleibt.

### 5.2 Klassifikation

Fachliches Leitprinzip (freigegeben 2026-04-21):

- **Immer hart** bleiben: echte Unterdeckungen bei Energie/Protein, absolute Sicherheitsgrenzen, maximale Einsatzmengen, klare Ausschlussregeln.
- **Über Strafkosten relaxiert** werden: Zielkorridore (statt Mindest-/Maximalwerte mit Puffer), Struktur-Nähe, RMD-/Balance-Nähe, Komfortbereiche bei Mineralstoffen (sofern keine echte Mangelsituation entsteht), weidespezifische Anpassungskorridore.

#### 5.2.1 Normierung und Strafgewichts-Klassen (freigegeben 2026-04-21)

Die DLG-Unterlagen geben Zielgrößen und einen Regelkreis vor, aber keine Euro-Strafterme; deshalb sind die Strafterme eine Softwareentscheidung. Weil GfE/DLG parallel mit sehr unterschiedlichen Größen arbeitet (ME, sidP, RMD, aNDFom, ADFom, DNDF, FIKH, peNDF), wäre ein einheitlicher Rohwert-Preis numerisch zu grob.

**Vorgehen in V1**:

1. Jede Abweichung wird zuerst **auf den Zielkorridor normiert** (dimensionslos):

   ```text
   deviation_norm = abs(actual - target_point) / corridor_halfwidth
   ```

   - `target_point` = Mitte des Zielkorridors (z. B. RMD-Ziel 0 g N/kg TM)
   - `corridor_halfwidth` = fachliche Toleranzbreite (z. B. RMD-Toleranz 1,5 g N/kg TM)
   - `deviation_norm` = 1,0 entspricht „genau am Rand des DLG-Toleranzbands"

2. Auf diese normierte Abweichung wirkt die **Basisstrafe 1,0 €/Einheit**, multipliziert mit dem Klassengewicht:

   | Klasse | Gewicht | Inhalt |
   |---|---|---|
   | **A (hoch)** | ×10 | Pansen- und versorgungsnahe Balancegrößen: ME-/sidP-Korridore, Mg/K-Risiko (Grastetanie), RMD-Nähe |
   | **B (mittel)** | ×3 | Struktur- und Kohlenhydrat-Zielkorridore: peNDF, aNDFomGF, pabKH, Grobfutteranteil |
   | **C (niedrig)** | ×1 | Komfort- und Schönheitsziele: CP-Obergrenze, XL-Obergrenze, feinere Block-Limits |

3. Der effektive Strafterm ist dann:

   ```text
   penalty = base_cost(1.0) × class_weight × relaxation_factor × deviation_norm
   ```

   wobei `relaxation_factor` aus §5.3 stammt (strict ×3 / standard ×1 / soft ×0.3).

#### 5.2.2 Constraint-Tabelle

| Constraint | Klasse | Klassen­gewicht | Normierungs­basis | Quelle |
|---|---|---|---|---|
| DMI_min / DMI_max (physiologisch) | **hart** | — | — | DLG 01|2025 |
| ME_min (echte Energie-Unterdeckung) | **hart** | — | — | GfE 2023 |
| sidP_min (echte Protein-Unterdeckung) | **hart** | — | — | GfE 2023 / DLG 504 |
| Ca, P, Na, Mg min (Gesundheits-Minimum) | **hart** | — | — | DLG 01|2025 |
| max_kg je Futtermittel (Einsatzobergrenzen) | **hart** | — | — | DLG-Futtertabelle / Hygiene |
| Mg-Supplement min 0,05 kg TM (nur PMR+Weide) | **hart** | — | — | Sicherheit Grastetanie |
| ME-Zielkorridor (Über-/Unterversorgung innerhalb Komfortband) | **weich A** | ×10 | ±5 % des Tagesbedarfs | DLG 01|2025 Tab. 14 |
| sidP-Zielkorridor | **weich A** | ×10 | ±8 % des Tagesbedarfs | DLG 504 |
| K_max bzw. K:Mg-Risiko | **weich A** | ×10 | K_max-Limit bzw. K:Mg-Zielwert ≤ 4 | DLG 417 |
| RMD-Nähe (modus-abhängig) | **weich A** | ×10 | rmd_max-Toleranz (TMR 1,5 / PMR 3,0 / PMR+Weide 8,0) | DLG 01|2025 + DLG 417 |
| peNDF_min | **weich B** | ×3 | peNDF-Mindestwert (stärkeabhängig) | DLG 443 |
| aNDFomGF_min (Grundfutter-NDF-Dichte) | **weich B** | ×3 | aNDFomGF-Mindestwert modusabhängig | DLG 01|2025 Tab. 14 |
| pabKH_max | **weich B** | ×3 | pabKH-Obergrenze modusabhängig | DLG 01|2025 |
| Grobfutter-Anteil ≥ 40 % DMI | **weich B** | ×3 | 40 % DMI | DLG 01|2025 |
| CP_max | **weich C** | ×1 | CP-Obergrenze modusabhängig | DLG 504 |
| XL_max | **weich C** | ×1 | 40–48 g/kg TM modusabhängig | DLG-Grenze |
| Block-Limits (KF ≤ 55 %, MIN 0,05–0,4 kg TM) | **weich C** | ×1 | Jeweiliger Policy-Profil-Korridor (§6) | Policy-Profil |

Strafterme werden global über `relaxation_policy` skaliert (5.3); Hart-Constraints sind nicht betroffen.

### 5.3 `relaxation_policy` – Strafterm-Skalierung

Freigegeben 2026-04-21:

| Policy | Skalierungsfaktor | Einsatzprofil | Infeasible-Risiko |
|---|---|---|---|
| `strict` | ×3 | Test, Debug, Gutachten, Beratungsdokumentation | hoch (nur für PMR/Weide bedingt geeignet) |
| `standard` | ×1 | **Default** – fachliche Balance mit weichen Zielkorridoren | niedrig |
| `soft` | ×0.3 | schwierige Praxisrationen, Frühjahrsweide, enge Futterauswahl | sehr niedrig, Warnkennzeichnung im Ergebnis |

Implementierung: die Default-Strafsätze aus 5.2 werden mit dem Policy-Faktor multipliziert. Hart-Constraints sind nicht betroffen.

UI-Hinweis (verbindlich):
- Bei `soft` muss das Ergebnis-Panel eine sichtbare Kennzeichnung tragen („Ration mit erweiterter Relaxation – Zielkorridore weicher bewertet").
- Bei `strict` wird ein Hinweis angezeigt, wenn `infeasible` zurückkommt, dass ein Wechsel auf `standard` plausibel ist.

## 6. Drei-Block-Struktur und Policy-Profile

Die Feed-Liste wird intern in drei Blöcke partitioniert:

- **GF** (Grundfutter) — `forage=True`
- **KF** (Ergänzung) — Kraftfutter / Mischfutter / Nebenprodukte / Compound-Uploads
- **MIN** (Mineral) — `_special`-Flag oder `group startswith "Mineral"`

Die DLG trennt diese drei Ebenen inhaltlich sehr klar (Grundfutterleistung in DLG 443, Ergänzungsfutter in DLG 01|2025, Mineralergänzung in DLG 417). Die konkreten Prozentgrenzen sind jedoch **keine offiziellen DLG-Pflichtzahlen**, sondern Betriebslogik. Deshalb wird die Konfiguration versioniert und **nicht** im Standard-Wizard frei veränderbar (freigegeben 2026-04-21):

### 6.1 Policy-Profile im Backend

Drei versionierte Policy-Profile als JSON unter `app/config/rations_block_policies.json`:

| Profil | GF-Anteil | KF-Anteil | MIN-Anteil | Einsatz |
|---|---|---|---|---|
| `tmr_standard` | ≥ 50 % DMI | ≤ 50 % DMI | 0,05–0,35 kg TM/d | Stall-TMR, Hochleistung |
| `pmr_standard` | ≥ 40 % DMI | ≤ 55 % DMI | 0,05–0,40 kg TM/d | PMR ohne Weide |
| `pmr_pasture_spring` | ≥ 50 % DMI (davon ≥ 60 % Weide/Gras) | ≤ 35 % DMI | 0,10–0,50 kg TM/d (Mg/Na erhöht) | PMR+Weide Frühjahr |

Jedes Profil trägt ein Feld `version` und ein Feld `source` (Referenz auf das fachliche Dokument, das die Werte trägt). Änderungen erfordern einen neuen Versionsstand + Review.

### 6.2 Zuordnung zur Ration

- `feeding_type + season_profile` → Policy-Profil wird **automatisch** gewählt:
  - `TMR` → `tmr_standard`
  - `PMR` → `pmr_standard`
  - `PMR+Weide` + `season_profile ∈ {spring_young, spring_mid, spring_late}` → `pmr_pasture_spring`
  - `PMR+Weide` + andere Jahreszeiten → `pmr_standard` (bis dedizierte Profile existieren)

### 6.3 Sichtbarkeit im UI

- Standard-Wizard: **nur Info-Anzeige** des aktiven Profils („Policy: `pmr_pasture_spring` v1.0").
- Expertenmodus: **Override einzelner Limits** zulässig; jede Abweichung vom Profil wird im Response als `policy_overrides` dokumentiert und im UI mit Warn-Badge markiert.
- Normale Anwender können die Grundlogik nicht versehentlich „kaputtklicken".

### 6.4 Solver-Umsetzung

Die Blöcke werden im Solver explizit als Gruppenbedingungen eingezogen (weiche Constraints, Klasse B für GF-/KF-Anteil, Klasse C für MIN-Korridor). In der Ergebnis-UI bleiben die drei Spalten-Darstellungen (Grundfutter / Ergänzung / Mineral) erhalten.

## 7. Saisonale Weideprofile

Die DLG-Tabelle liefert schon heute saisonale IDs (`dlg_10180010` Frühjahr jung … `dlg_10220010` Sommer älter). Neu ist:

- `season_profile` im Profil ist **kein** neuer Feed, sondern ein **Default-Katalog**, der im Wizard die passende Weide-ID vorauswählt.
- Bei `feeding_type == "PMR+Weide"` ohne `season_profile` bleibt die UI-Auswahl offen.
- Die Nährwerte der Feeds bleiben unverändert; nur die UX-Vorauswahl ändert sich.

## 8. FAN-Iteration: Formeln und Kennzahlen

### 8.1 Schätzung Start-FAN

```text
FAN_start = max(2.0, min(5.0,
    1.0
    + 0.5 × (milk_kg_day / 20)        # Milchleistung
    + 0.2 × (lactation_stage_days < 60)  # Frischmelker-Boost
    − 0.1 × (parity == 1)                # Färsen haben geringeren relativen FAN
))
```

Dokumentierte Näherung. Alternative: aus `dmi_observed / dmi_maintenance`.

### 8.2 FAN-Wirkung auf Koeffizienten

- **ME-Anpassung**: `ME_effective = ME_FAN1 + slope_ME × (FANi − 1)` mit `slope_ME` je Futterart.
- **sidP-Anpassung**: `k = k_FAN1 × f(FANi)`; daraus folgt UDP/sidP pro Futter (DLG 504 Formel).

Implementierung als dedizierte Funktion `_apply_fan_effect(feed, fan) → feed'` — die FAN1-Tabellenwerte bleiben in `_get_feeds()` unverändert, die Umrechnung geschieht pro LP-Lauf.

#### 8.2.1 Katalog mit Herkunftsflag (freigegeben 2026-04-21)

Keine freien Fantasie-Interpolationen aus Deklarationen. Stattdessen versionierter JSON-Katalog `app/config/fan_slope_catalog.json` mit drei Herkunftsstufen pro Eintrag:

| Flag | Bedeutung | Zulässig wenn |
|---|---|---|
| `exact` | direkter DLG-/Laborwert | in DLG-Futterwerttabelle 2023 / DLG 503 / DLG 504 exakt gelistet |
| `mapped` | nächstpassende DLG-Futtergruppe | Futtermittel nicht exakt gelistet, aber eindeutig einer DLG-Hauptgruppe GF / KF / SF zuordenbar |
| `fallback` | konservativer Gruppenstandard | weder exakt noch belastbar gemappt; konservativ = niedrigere FAN-Sensitivität |

DLG 504 unterscheidet die Passagerate `k` nur auf Ebene der Hauptgruppen GF / KF / SF — die Mapping-Hierarchie ist entsprechend:

1. **Exakter Eintrag** nach DLG-Futterart-ID
2. **Gruppen-Mapping** auf GF / KF / SF (ggf. mit saisonaler/Nutzungsstadium-Untergruppe)
3. **Konservativer Fallback** pro Hauptgruppe

Für Weide-/Grasfutter wird der Katalog zusätzlich **saisonal** geführt (Frühjahr jung / mittel / älter / Sommer jung / älter), weil die DLG-Futterwerttabelle bereits diese Kategorien ausweist und die FAN-Wirkung bei Jungweide (hoher N-Umsatz) anders wirkt als bei älterer Weide.

#### 8.2.2 Katalog-Struktur (JSON-Schema, skizziert)

```json
{
  "version": "1.0",
  "source": "DLG 503/504 + DLG-Futterwerttabelle 2023 (Näherung)",
  "groups": {
    "GF/Gras/spring_young":    { "slope_me": 0.29, "k_fan1": 0.045, "flag": "mapped" },
    "GF/Gras/spring_mid":      { "slope_me": 0.27, "k_fan1": 0.048, "flag": "mapped" },
    "GF/Silage/Gras":          { "slope_me": 0.25, "k_fan1": 0.050, "flag": "mapped" },
    "GF/Heu":                  { "slope_me": 0.22, "k_fan1": 0.055, "flag": "fallback" },
    "GF/Maissilage":           { "slope_me": 0.30, "k_fan1": 0.040, "flag": "mapped" },
    "KF/Getreide":             { "slope_me": 0.18, "k_fan1": 0.080, "flag": "mapped" },
    "KF/Mischfutter":          { "slope_me": 0.20, "k_fan1": 0.075, "flag": "mapped" },
    "KF/Nebenprodukt":         { "slope_me": 0.15, "k_fan1": 0.070, "flag": "fallback" },
    "SF/Saftfutter":           { "slope_me": 0.25, "k_fan1": 0.060, "flag": "fallback" },
    "MIN":                     { "slope_me": 0.00, "k_fan1": 0.000, "flag": "exact" }
  }
}
```

Zahlen sind Initialnäherungen (DLG 503 Beispielkurve: ME-Delta 0,44 MJ/kg TM zwischen FANi 2,5 und 4,0 → slope ≈ 0,29; Nachkalibrierung im Live-Betrieb vorgesehen).

#### 8.2.3 Transparenz in der Response

Jeder Feed-Eintrag in `ration_items` bekommt ein neues Feld `fan_slope_source: "exact" | "mapped" | "fallback"`. Aggregiert zusätzlich:

```json
"fan_calibration": {
  "catalog_version": "1.0",
  "feeds_exact": 3,
  "feeds_mapped": 5,
  "feeds_fallback": 1,
  "fallback_warning": "Feed X, Y: fallback — Werte konservativ, Beratung empfohlen."
}
```

Das macht im UI sichtbar, wie belastbar die FAN-Anpassung für die konkrete Ration ist.

### 8.3 FANi aus Ergebnis

```text
FANi_out = DMI_result / DMI_maintenance
DMI_maintenance = 0.02 × body_weight_kg   # GfE 2023 Näherung
```

### 8.4 Konvergenz

Abbruch wenn `|FANi_out − FANi_in| ≤ fan_tolerance` oder `iterations == fan_max_iterations` (freigegeben 2026-04-21):

- `fan_tolerance` Default = **0.05** (entspricht bei 650 kg KM nur ≈ 0,33 kg TM/d Differenz → ME-Änderung ≈ 0,015 MJ/kg TM)
- `fan_tolerance_warn` = **0.10** → UI-Hinweis „letzte Iteration noch über Warnschwelle"
- `fan_max_iterations` = **5**

Nicht-Konvergenz liefert letzte gültige Lösung + Warnung „FAN nicht konvergiert; Beratung empfohlen".

## 9. UI-Flow

Leitlinie (freigegeben 2026-04-21): FAN ist im GfE-2023-System zentral (Tabellenwerte beruhen auf FAN1, reale Bewertung auf FANi). Deshalb **sichtbar, aber kompakt** — nicht komplett versteckt und auch kein überladenes Detailformular.

### 9.1 Wizard-Erweiterungen

Im Wizard (`rationsoptimierung.tsx`) kommt ein neuer kompakter Block dazu:

1. **Block „Bewertungsmodus (GfE 2023)"** — in Schritt 1 oder 2, direkt sichtbar:
   - Default sichtbar: `Auto iterativ` (entspricht `fan_mode = auto_iterative`)
   - Darunter einklappbar („Weitere Bewertungsmodi"): `Referenz-FAN manuell` und `Nur Bewertung`
   - Bei `Referenz-FAN manuell`: drei Presets **2,5 / 3,0 / 3,5** als Buttons + Freifeld (2,0–5,0)
   - Bei `Auto iterativ`: Toleranz-Input mit Default `0.05`, kollabiert unter „Details"

2. **Schritt „Systemtyp & Weideprofil"** — TMR / PMR / PMR+Weide. Bei PMR+Weide erscheint das Weideprofil-Dropdown mit Saison-Vorschlag (Klick-Übernahme, nicht automatisch).

### 9.2 Ergebnis-Anzeige

- **FAN-Badge** im Kopf der Ergebnisansicht: immer sichtbar, z. B. „bewertet bei FAN 3,1 (konvergiert, 3 Iterationen)".
- Zusätzliches Panel `FAN-Kalibrierung`: Iterationskurve, Konvergenz-Status, Hinweis auf `fan_tolerance_warn` falls überschritten.
- Panel `Constraint-Status`: Hart/Weich-Verletzungen, Strafkosten pro Position, Ampel, je Constraint die benutzte Klasse (A/B/C) und das aktive `relaxation_policy`.
- Panel `FAN-Katalog-Transparenz`: Anzeige, wie viele Feeds `exact` / `mapped` / `fallback` bewertet wurden (siehe §8.2.3).
- Bei `relaxation_policy = soft`: sichtbare **Warn-Kennzeichnung** („Soft-Mode: erweiterte Toleranzen, Beratung prüfen").
- Bestehende Panels (`ForagePerformance`, `PastureRisk`) bleiben unverändert.

## 10. Migrationspfad, Rückwärtskompatibilität und Abnahmekriterien

### 10.1 Bruder-Regression als Abnahmekriterium (freigegeben 2026-04-21)

Fachlich saubere Formulierung (kein „muss immer sofort lösbar"):

- **Ohne erlaubtes Mineralsupplement** darf die Ration scheitern, aber **nicht pauschal als `infeasible` wegen PMR-/Weide-Fehlmodellierung**. Stattdessen muss der Response eine klare Diagnose enthalten (z. B. Mg/K-Risiko, Unterdeckung im Balancebereich).
- **Mit erlaubtem Weidemineral (`special_weide_mg_mineral` als Option)** muss der Solver eine fachlich ausgeglichene Lösung **vor dem Kostenoptimum** finden oder, falls weiter unlösbar, die verbleibende Engstelle **explizit benennen**.
- **Nicht akzeptabel** ist jedes Scheitern aus technischen Fehlannahmen (pauschales Weide-Cap, falsche TMR/PMR-Behandlung, falsche FM→TM-Konvertierung, off-by-one im Compound-Parser).

Konkrete Gate-Tests:

- `tests/test_rations_optimization_spring_pasture_case.py::test_optimize_brother_spring_case_with_mg_supplement_is_optimal` — muss grün sein (Status = `optimal`, Mg-Supplement enthalten, K:Mg-Warnung gesetzt).
- Neuer Test `test_brother_spring_case_without_mg_supplement_reports_diagnosis` (FAN-MODE-002): wenn `special_weide_mg_mineral` nicht in der Feedliste ist, muss die Response entweder `optimal` sein oder `infeasible` **mit** `diagnosis.reason ∈ {"mg_deficit", "k_mg_antagonism", …}` — **nicht** ohne Begründung.
- Jeder Slice, der diese Tests rot macht, wird rejectet.

### 10.2 Rückwärtskompatibilität

- Default-Werte der neuen Felder sind so gewählt, dass **bestehende Clients ohne Änderung** dasselbe Verhalten bekommen wie heute (`fan_mode=auto_iterative`, `relaxation_policy=standard`, `objective_strategy=balance_then_cost`).
- Response bleibt **additiv**: `fan_calibration`, `constraint_status`, `fan_slope_source` je Feed und `policy_overrides` kommen dazu, nichts wird entfernt.
- Bestehende Tests (`test_rations_optimization_pasture.py`, `test_rations_optimization_spring_pasture_case.py`, `test_rations_optimization_compound_feed.py`) müssen **unverändert grün bleiben**.

### 10.3 Neue Tests pro Slice

- `test_fan_iteration_converges_on_practice_case`
- `test_reference_fan_is_deterministic`
- `test_evaluation_only_does_not_optimize`
- `test_soft_constraint_violation_is_not_infeasible`
- `test_hard_constraint_violation_stays_infeasible`
- `test_block_policy_profile_is_loaded_from_json`
- `test_fan_catalog_flag_is_reported_in_response`
- `test_relaxation_policy_soft_triggers_ui_warning_marker`
- `test_brother_spring_case_without_mg_supplement_reports_diagnosis`

## 11. Freigabestand

### 11.1 Alle V1-Entscheidungen freigegeben (2026-04-21)

Für V1 gibt es keine offenen Entscheidungen mehr. Der folgende Block dokumentiert vollständig, welche Festlegungen das Fundament für die Slices FAN-MODE-001 … 006 (siehe §12) bilden:


- **FAN-Iteration Stoppkriterium**: `fan_tolerance = 0.05`, Warnschwelle `0.10`, max. Iterationen `5`. Fachliche Begründung aus DLG 503 (ME-Sensitivität ca. 0,015 MJ/kg TM bei 0,05 FAN-Schritt) und DLG 504 (lineare k-Abhängigkeit).
- **FAN-Referenzstufen im UI**: drei schnell wählbare Stufen 2,5 / 3,0 / 3,5 plus Freiwert 2,0–5,0. Deckt den praxisrelevanten DLG-Bereich ab.
- **Saisonale Weideprofil-Auswahl**: Vorschlag mit Bestätigungs-Klick (keine automatische Übernahme).
- **`relaxation_policy`**: drei Stufen `strict` / `standard` / `soft` mit Skalierungsfaktoren ×3 / ×1 / ×0.3. Default `standard`. Hart-Constraints sind nicht betroffen. `soft` trägt im UI eine sichtbare Kennzeichnung.
- **Hart/Weich-Kategorisierung in §5.2**: hart = echte Unterdeckungen, Sicherheitsgrenzen, max. Einsatzmengen, Ausschlussregeln. Weich = Zielkorridore, Struktur-/RMD-Nähe, Komfort-Mineralstoffe, Weidekorridore.
- **Strafterm-Modell (§5.2.1)**: keine rohen Euro-Rohwerte; stattdessen **dimensionslose Normierung** auf Zielkorridor-Breite, Basisstrafe 1,0 €/Einheit, drei Klassengewichte A ×10 / B ×3 / C ×1. Klassenzuordnung folgt der fachlichen Priorität (Pansen/Versorgung > Struktur > Komfort).
- **Drei-Block-Limits (§6)**: **Policy-Profile** im Backend (`tmr_standard`, `pmr_standard`, `pmr_pasture_spring`) als versionierte JSON-Konfig. Im Standard-Wizard nur als Info sichtbar, Override nur im Expertenmodus mit `policy_overrides`-Markierung im Response. Auswahl automatisch aus `feeding_type + season_profile`.
- **FAN-Formel-Katalog (§8.2.1)**: versionierter JSON-Katalog mit **Herkunftsflag** pro Eintrag (`exact` / `mapped` / `fallback`). Mapping-Hierarchie: DLG-Eintrag → DLG-Hauptgruppe GF/KF/SF (ggf. saisonal) → konservativer Fallback. Herkunft wird pro Feed und aggregiert im Response transparent gemacht; Fallback triggert einen Beratungs-Hinweis.
- **Wizard-Sichtbarkeit FAN-Modus (§9.1)**: sichtbarer, aber kompakter Block „Bewertungsmodus (GfE 2023)" in Schritt 1/2. Default `auto_iterative` direkt sichtbar; `reference` und `evaluation_only` einklappbar. Ergebnis trägt immer ein FAN-Badge.
- **Bruder-Regression als Abnahmekriterium (§10.1)**: fachlich differenziert. Nicht „muss immer sofort lösbar sein", sondern **kein technisches False-Infeasible**: Ohne Mg-Supplement ist klare Diagnose (z. B. Mg/K-Risiko) akzeptabel; mit erlaubtem Weidemineral muss eine ausgeglichene Lösung vor Kostenoptimum gefunden werden oder die verbleibende Engstelle explizit benannt sein. Umsetzung siehe §10.1.

## 12. Umsetzungsreihenfolge (Vorschlag, jeweils ein Slice)

1. `FAN-MODE-001`: Datenvertrag + Request/Response-Erweiterung, ohne Solver-Änderung (Backend liefert aktuelle Lösung + gefüllte `fan_calibration`/`constraint_status`).
2. `FAN-MODE-002`: Hart/Weich-Refaktoring des Solvers (`_run_lp` → dreistufig), alle bestehenden Tests müssen grün bleiben.
3. `FAN-MODE-003`: FAN-Iteration (auto_iterative, reference, evaluation_only) im Solver.
4. `FAN-MODE-004`: UI-Schritt „Leistungsgruppe & FAN" im Wizard, Ergebnis-Panels.
5. `FAN-MODE-005`: Saisonale Weideprofil-Vorauswahl.
6. `FAN-MODE-006`: Strafsatz-Konfiguration (`relaxation_policy` voll aktiviert).

Jeder Slice ist einzeln lauffähig und testbar. Abbruch nach jedem Slice ist gefahrlos möglich.

## 13. Risiken

- **Numerische Stabilität**: Die FAN-Iteration kann oszillieren, wenn die LP-Lösung nahe mehreren Ecken liegt. Mitigation: FAN-Iterationen gedämpft (`FAN_new = 0.5 × FAN_out + 0.5 × FAN_in`), harter Iterationsdeckel.
- **UX-Komplexität**: Drei neue Modi + Weideprofil + Relaxation-Policy könnten den Wizard überladen. Mitigation: Standardwerte so setzen, dass 90 % der Nutzer den „Advanced"-Block nie öffnen.
- **Rückwärtskompatibilität**: Additive API hält bestehende Clients stabil, aber die internen Solver-Ergebnisse könnten marginal abweichen (Stage-B-Balance-Minimum statt direktem Stage-1). Mitigation: bestehende Tests als harte Gates.
- **DLG-Tabellenpflege**: `slope_ME` und `k_FAN1` brauchen pro Futterart-Gruppe einen Katalog. Mitigation: Näherungswerte als erste Iteration, konfigurierbar via JSON.

## 14. Nicht Teil dieses Slices

- Integration in ERP-weite Bewertungslogik (Controlling / Einkauf)
- Historisierung / Versionierung der Referenzkennzahlen (separates Thema)
- Mehrtiergruppen-Optimierung (Herde statt Einzeltier)
- On-Farm-Kalibrierung über Futter-Aufnahme-Messungen

Diese Punkte sind in `open-gaps-and-known-issues.md` zu ergänzen, sobald die Basis-Umsetzung steht.
