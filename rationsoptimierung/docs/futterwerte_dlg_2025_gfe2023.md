# Futtermittelreferenz: DLG 2025 / LKV Ernte 2025 (GfE-2023-kompatibel)

## Einordnung

- **GfE 2023** (AfBN) liefert die **Bedarfslogik** (ME, ECM, sidP-Näherungen etc.) im Code unter `app/nutrition/gfe2023.py`.
- **DLG-Futterwerttabellen Wiederkäuer 2025** sind eine gängige **Standardquelle für Futtermittelbewertung** im zum GfE-2023-System passenden Rahmen.
- **Energie im LP:** NEL vs. ME siehe Abschnitt [NEL vs. ME](#nel-vs-me).

## NEL vs. ME

Im **GfE-2023-System** (Arbeitsgemeinschaft für Bedarf und Nährstoffe) werden Tierbedarf und Rationsbewertung über **einheitliche energetische Größen** geführt, wobei **umsetzbare Energie (ME)** und die daraus abgeleiteten Milchleistungsbezüge (z. B. über **ECM**) die zentrale Rolle für die bilanzielle Zuordnung von Bedarf und Aufnahme spielen; **Nettoenergie-Laktation (NEL)** ist eine **eigenständige** energetische Größe mit anderer Definition und Umrechnungslogik und **kein** direkter Ersatz für Futtermittel-ME in Tabellenwerken.

**Konsequenz für dieses LP:**

- **NEL wird im linearen Programm nicht als Futtermittel-Energie verwendet** (keine NEL-Spalte als LP-Koeffizient für Futtermittel).
- **Futtermittel-Energie im LP:** **ME in MJ/kg TM** (trockenmassebezogen), wie in den mitgelieferten Referenz-CSVs (`me_mj_kg_tm` → `me_mj_kgdm`).
- **Keine 1:1-Substitution:** Werte aus NEL-Spalten oder fremden Umrechnungsfaktoren **nicht** pauschal auf ME übertragen; immer die **ME-Bewertung** der gewählten Quelle (DLG/LKV/Analyse) verwenden.

## Mitgelieferte CSV-Dateien (nur Analytik, wie übernommen)

| Datei | Inhalt |
|-------|--------|
| `data/reference/lkv_sachsen_getreide_ernte_2025_tabelle1.csv` | Getreide – **LKV Sachsen**, Ergebnisse Getreideernte 2025 (Tabelle 1) |
| `data/reference/dlg_2025_kraftfutter_wiederkauer_tabelle2.csv` | Konzentrate/Rohstoffe – **DLG** Wiederkäuer 2025 (Tabelle 2) |

**Spaltenbedeutung (einheitlich):**

- `tm_g_kg_fm`: Trockenmasse **g/kg Frischmasse** → im LP-Schema `dm_frac = tm_g_kg_fm / 1000`.
- `ra_g_kg_tm`, `rp_g_kg_tm`, `rf_g_kg_tm`: Rohasche, Rohprotein, Rohfett **g/kg TM**.
- `starch_g_kg_tm`, `sugar_g_kg_tm`, `andfom_g_kg_tm`: **g/kg TM**.
- `ge_mj_kg_tm`, `me_mj_kg_tm`: Bruttoenergie / umsetzbare Energie **MJ/kg TM**.

## Mapping → `FeedIngredient` (Rationsoptimierung)

| CSV / Analytik | `FeedIngredient`-Feld |
|----------------|------------------------|
| `tm_g_kg_fm` | `dm_frac = tm_g_kg_fm / 1000` |
| `me_mj_kg_tm` | `me_mj_kgdm` (identisch, MJ/kg TM) |
| `andfom_g_kg_tm` | `andfom_g_kgdm` |
| `starch_g_kg_tm` | `starch_g_kgdm` |
| `sugar_g_kg_tm` | `sugar_g_kgdm` |
| `rf_g_kg_tm` | `fat_g_kgdm` (Rohfett) |

### sidP und Mineralien (Quellenpflicht)

**sidP** (`sidp_g_kgdm`) und **Mineralstoffe** (`ca_g_kgdm`, `p_g_kgdm`, `na_g_kgdm`) müssen **sachlich belegt** sein:

- **Primärquelle:** passende **Zeile im DLG-Tabellenwerk** zur Futtermittelgruppe (nXP/sidP-Systematik laut DLG) **oder** **Laboranalyse** (Charge/Betrieb).
- **Nicht ausreichend für verbindliche Angaben:** **sidP allein aus Rohprotein (RP)** per pauschalem Faktor ableiten – das ist für **Deklarationen, Prüfungen oder verbindliche Rationsdokumentation** ungeeignet; RP und sidP sind im System verschiedene Größen.

**Silagen und feuchte Nebenprodukte:** wie von der DLG üblich stark von Charge/Betrieb abhängig → **Analyse** statt allein Tabellenmittel.

**Weitere LP-Felder** (`price_eur_kgdm`, `min_kgdm`, `max_kgdm`, `group`): betriebs-/marktabhängig, für das LP nötig.

#### Checkliste: `dlg_2025_lp_import_filled_sourced` befüllen

Dateien: `data/reference/dlg_2025_lp_import_filled_sourced.xlsx` / `.csv` (Blatt `lp_import_filled`). Ziel: jede Zeile ist **nachvollziehbar** und **quellenbasiert** (Spalten `source_*`).

1. **Futtermittelzeile wählen:** DLG-Kategorie/Tabellenzeile oder Analysenbericht eindeutig zuordnen; bei Abweichung zur Kurz-Referenz-CSV **nicht** stillschweigend „schätzen“.
2. **sidP:** Wert aus **derselben DLG-Zeile** wie die stoffliche Einordnung **oder** aus Analyse; **kein** sidP nur aus RP-Faktor, wenn die Nutzung **verbindlich** sein soll.
3. **Ca, P, Na:** aus **DLG-Zeile** oder **Labor**; bei Mischungen/Beigaben dokumentieren.
4. **Quellen-Spalten setzen:** `source_sidp`, `source_minerals`, `source_group`, `source_price`, `source_limits` mit PDF-/URL-/Kurzverweis (z. B. DLG-Ausgabe, Analysennummer).
5. **`group`:** DLG-Kategorie wie in der Vorlage; für API/Import später ggf. Mapping auf `FeedGroup` (`forage` / `concentrate` / …).
6. **Review:** Nach Merge (`merge_dlg_reference_to_lp_csv.py`) Zeilen mit `no_analytic_match` prüfen – ggf. Aliase oder Referenz-CSV ergänzen (siehe [Regression: Merge-Report und Aliases](#regression-merge-report-und-aliases)).

### Noch zu ergänzen (Kurzüberblick)

- **`sidp_g_kgdm`**, **`ca_g_kgdm`, `p_g_kgdm`, `na_g_kgdm`:** siehe [sidP und Mineralien](#sidp-und-mineralien-quellenpflicht).
- **`price_eur_kgdm`, `min_kgdm`, `max_kgdm`, `group`:** betriebs-/marktabhängig; Quelle in `source_*` festhalten.

## Abgleich: Sample-`weizen` vs. LKV Ernte 2025 (Referenz)

Im Demo-`FeedService` ist `weizen` mit `dm_frac=0.88`, `me_mj_kgdm=13.0`, `starch_g_kgdm=600`, `andfom_g_kgdm=25` hinterlegt (vereinfachtes Schulungsbeispiel).

Referenz **LKV Ernte 2025 Weizen** (`weizen_ernte2025`):

- `dm_frac`: **0,864** (vs. 0,88)
- `me_mj_kgdm`: **13,2** (vs. 13,0)
- `starch_g_kgdm`: **652** (vs. 600)
- `andfom_g_kgdm`: **121** (vs. 25) → **große Abweichung**; das alte Sample unterschätzt aNDFom für Weizen deutlich.

Damit ändern sich **Stärke- und Faserrestriktionen** im LP spürbar gegenüber dem Demo-Datensatz.

## Quellen (extern)

- DLG: *Futterwerttabellen für Wiederkäuer* (PDF/Fachinfos auf dlg.org).
- LKV Sachsen: *Ergebnisse der Getreideernte 2025* (Blog/Fachartikel).

## LP-Import-Vorlage (Excel + CSV im Repo)

| Datei | Zweck |
|-------|--------|
| `data/reference/dlg_2025_lp_import_template.xlsx` | Original-Vorlage (Blätter `lp_import_template`, `README`) |
| `data/reference/dlg_2025_lp_import_template.csv` | Dasselbe Blatt `lp_import_template` als UTF-8-SIG (Excel-tauglich) |

Spalten der Vorlage: `feed_id`, `feed_name`, `source_set`, `sidp_g_kgdm`, `ca_g_kgdm`, `p_g_kgdm`, `na_g_kgdm`, `price_eur_kgdm`, `group`, `min_kgdm`, `max_kgdm`, `notes` — LP-Felder sind bewusst leer bis zur Befüllung aus DLG/Analyse.

**Aktualisieren aus lokalem Pfad** (z. B. `Documents`):

```bash
python scripts/import_dlg_lp_template_from_xlsx.py
# oder:
python scripts/import_dlg_lp_template_from_xlsx.py "C:\Pfad\dlg_2025_lp_import_template.xlsx"
```

## Nächster Schritt (Import ins Tool)

1. Referenz-CSVs (`lkv_*`, `dlg_2025_kraftfutter_*`) bleiben **rein analytisch** (ME, Faser, Stärke, …).
2. **`dlg_2025_lp_import_template`**: sidP, Mineralien, Preis, `group`, min/max ergänzen.
3. **Merge (implementiert):** `python scripts/merge_dlg_reference_to_lp_csv.py` erzeugt:
   - `data/reference/dlg_merged_feeds_lp.csv` – Zeilen mit Analytik (LKV Ernte 2025 / DLG Kraftfutter-Referenz) + sidP/Mineralien aus `dlg_2025_lp_import_filled_sourced.csv`; Silagen/Heu zusätzlich über `dlg_forage_merge_overlay.json`
   - `data/reference/dlg_merge_report.csv` – pro `feed_id` aus der LP-Datei Status `merged` oder `no_analytic_match`
   - Zuordnung erweiterbar in `data/reference/feed_analytic_aliases.json` (explizite IDs, Getreide → `*_ernte2025`, Raps-Varianten → Basis-DLG-Zeile mit Hinweis)

**Python:** `from app.utils.dlg_merged_csv import load_merged_feed_ingredients` → `list[FeedIngredient]` (ohne `merge_*`-Spalten).

Futtermittel ohne Eintrag in den **kurzen** Referenz-CSVs (z. B. Spezial-Schrote) bleiben `no_analytic_match`, bis Aliase oder Referenzzeilen ergänzt werden; **Silagen/Heu** aus der befüllten LP-Datei sind über das **Overlay** (siehe [Silagen und Heu im Merge](#silagen-und-heu-im-merge-overlay-lkvdlg-spaltenlogik)) gemerged.

## Regression: Merge-Report und Aliases

Nach **Änderungen** an:

- `data/reference/feed_analytic_aliases.json`, und/oder
- `data/reference/dlg_forage_merge_overlay.json`, und/oder
- den **Referenz-CSVs** (`lkv_sachsen_getreide_ernte_2025_tabelle1.csv`, `dlg_2025_kraftfutter_wiederkauer_tabelle2.csv`), und/oder
- den **LP-Ergänzungsdaten** (`dlg_2025_lp_import_filled_sourced.csv` / Import aus XLSX),

sollte der Merge **erneut** ausgeführt und der Report geprüft werden.

**Ablauf:**

1. **Merge ausführen:**
   ```bash
   python scripts/merge_dlg_reference_to_lp_csv.py
   ```
2. **Report öffnen:** `data/reference/dlg_merge_report.csv`.
3. **Zeilen `status = no_analytic_match` sichten:** fehlende oder nicht gematchte `feed_id` gegen Referenz-CSVs und befüllte LP-Datei abgleichen.
4. **Aliases pflegen:** in `data/reference/feed_analytic_aliases.json` fehlende oder synonyme IDs auf die **kanonische** Referenz-ID abbilden (z. B. Getreide → `*_ernte2025`, Raps-Varianten → Basis-DLG-Zeile); Merge erneut ausführen, bis die erwarteten Futtermittel **`merged`** sind oder bewusst als ohne Analytik dokumentiert bleiben.
5. **Ergebnis-CSV:** `data/reference/dlg_merged_feeds_lp.csv` für Loader/Tests/API wie gewohnt verwenden.

## Optional: API/FeedService Tenant-Hook (DLG-Merge)

Der Microservice kann die gemergten Futtermittel **zusätzlich** zu den Demo-8 Futtermitteln laden – in einem eigenen Mandanten (Standard: `dlg`), damit der Demo-Mandant stabil bleibt.

- **Aktivieren**: `RATIONS_DLG_MERGED_ENABLE=1`
- **Tenant-ID**: `RATIONS_DLG_MERGED_TENANT_ID=dlg` (Default)
- **Aufruf**: Header `X-Tenant-Id: dlg` bei `/api/v1/feeds`, `/api/v1/optimize/*` etc.

Quelle der Daten ist `data/reference/dlg_merged_feeds_lp.csv` (Loader: `app/utils/dlg_merged_csv.py`).

### `POST /api/v1/optimize/demo` mit Mandant `dlg`

Die Demo nutzt ein festes Kuhprofil (u. a. **Mindest-Raufutteranteil**). Der DLG-Merge-Datensatz enthält **Raufutter** (`forage`), u. a. `grassilage`, `maissilage` und weitere Grobfutterzeilen aus dem Overlay (siehe unten).

- **Verhalten:** Enthält der Korb **kein** Raufutter (z. B. nur Konzentrate im Request), ergänzt die API **Grassilage und Maissilage** aus dem Mandanten **`default`** — wie bei anderen Nicht-`default`-Mandanten.
- **Transparenz:** Bei Ergänzung: `metadata.forage_supplement_from_default_tenant: true`, `metadata.supplement_tenant_id: "default"`, Hinweis in `warnings` (gleiches Schema bei Demo, `POST /optimize` und `POST /optimize/from-profile`).

Ohne aktive Futtermittel für den gewählten Mandanten liefert der Endpunkt **HTTP 400** mit erklärendem `detail`.

### Silagen und Heu im Merge (Overlay, LKV/DLG-Spaltenlogik)

Für Futtermittel ohne Zeile in `dlg_2025_kraftfutter_wiederkauer_tabelle2.csv` / `lkv_sachsen_getreide_ernte_2025_tabelle1.csv` liefert `scripts/merge_dlg_reference_to_lp_csv.py` zusätzliche Zeilen aus **`data/reference/dlg_forage_merge_overlay.json`**:

- **Spalten wie im übrigen Merge:** `me_mj_kgdm`, `andfom_g_kgdm`, `starch_g_kgdm`, `sugar_g_kgdm`, `fat_g_kgdm` sind **g/kg TM** wie bei DLG/LKV (identisch zu `FeedIngredient`-Feldern `*_g_kgdm`); `dm_frac` = TM-Anteil Frischmasse (wie `tm_g_kg_fm / 1000` bei Referenzzeilen).
- **sidP und Mineralien:** für gemappte LP-Zeilen (z. B. `maissilage`, `grassilage_1_schnitt`) aus **`dlg_2025_lp_import_filled_sourced.csv`**, sofern gesetzt; sonst Template-Default aus dem Overlay (Demo-Niveau, an `feed_service`-Defaults angelehnt).
- **`group`:** `forage` für Silagen/Heu; die DLG-Textkategorie „Grundfutter - Grobfutter“ aus der LP-Datei wird im Merge zusätzlich über Schlüsselwörter (`silage`, `heu`, …) abgesichert.

## Befüllte LP-Zeilen mit Quellen (Excel + CSV)

| Datei | Zweck |
|-------|--------|
| `data/reference/dlg_2025_lp_import_filled_sourced.xlsx` | Kopie der befüllten Datei; Blatt **`lp_import_filled`** (nicht `lp_import_template`) |
| `data/reference/dlg_2025_lp_import_filled_sourced.csv` | Export desselben Blatts |

Zusätzliche Spalten: `source_sidp`, `source_minerals`, `source_group`, `source_price`, `source_limits` (URLs/Hinweise zur DLG-PDF).  
Spalte `group` enthält DLG-Kategorien (z. B. „Konzentratfutter - Trockenkonzentrat“) – für das API-Modell `FeedGroup` ist bei einem späteren Import eine **Abbildung** auf `forage` / `concentrate` / `protein` / `mineral` / `other` nötig.

**Aktualisieren:**

```bash
python scripts/import_dlg_lp_filled_from_xlsx.py
python scripts/import_dlg_lp_filled_from_xlsx.py "C:\Pfad\dlg_2025_lp_import_filled_sourced.xlsx" lp_import_filled
```
