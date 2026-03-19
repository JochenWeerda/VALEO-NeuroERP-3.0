# Futtermittelreferenz: DLG 2025 / LKV Ernte 2025 (GfE-2023-kompatibel)

## Einordnung

- **GfE 2023** (AfBN) liefert die **Bedarfslogik** (ME, ECM, sidP-Näherungen etc.) im Code unter `app/nutrition/gfe2023.py`.
- **DLG-Futterwerttabellen Wiederkäuer 2025** sind eine gängige **Standardquelle für Futtermittelbewertung** im zum GfE-2023-System passenden Rahmen.
- **NEL und ME** sind **verschiedene Größen**; für das LP werden **ME-Werte (MJ/kg TM)** aus den Tabellen verwendet, **keine** 1:1-Übernahme von NEL.

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

### Noch zu ergänzen (stehen in den vollständigen DLG-Tabellen oder in der Analyse)

- **`sidp_g_kgdm`**: aus der **DLG-Zeile** zur jeweiligen Futtermittelgruppe (nXP/sidP-Systematik gemäß Tabellenwerk) – **nicht** durch einfachen Faktor aus RP ersetzen, wenn eine verbindliche Ration/Deklaration gewünscht ist.
- **`ca_g_kgdm`, `p_g_kgdm`, `na_g_kgdm`**: ebenfalls aus DLG oder **Laboranalyse**.
- **`price_eur_kgdm`, `min_kgdm`, `max_kgdm`, `group`**: betriebs-/marktabhängig, für das LP nötig.

**Silagen und feuchte Nebenprodukte:** wie von der DLG üblich stark von Charge/Betrieb abhängig → **Analyse** statt allein Tabellenmittel.

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
   - `data/reference/dlg_merged_feeds_lp.csv` – Zeilen mit Analytik (LKV Ernte 2025 / DLG Kraftfutter-Referenz) + sidP/Mineralien aus `dlg_2025_lp_import_filled_sourced.csv`
   - `data/reference/dlg_merge_report.csv` – pro `feed_id` Status `merged` oder `no_analytic_match`
   - Zuordnung erweiterbar in `data/reference/feed_analytic_aliases.json` (explizite IDs, Getreide → `*_ernte2025`, Raps-Varianten → Basis-DLG-Zeile mit Hinweis)

**Python:** `from app.utils.dlg_merged_csv import load_merged_feed_ingredients` → `list[FeedIngredient]` (ohne `merge_*`-Spalten).

Futtermittel ohne Eintrag in den **kurzen** Referenz-CSVs (z. B. viele Silagen, Spezial-Schrote) erscheinen bislang als `no_analytic_match` – Analytik später ergänzen oder Aliases anlegen.

## Optional: API/FeedService Tenant-Hook (DLG-Merge)

Der Microservice kann die gemergten Futtermittel **zusätzlich** zu den Demo-8 Futtermitteln laden – in einem eigenen Mandanten (Standard: `dlg`), damit der Demo-Mandant stabil bleibt.

- **Aktivieren**: `RATIONS_DLG_MERGED_ENABLE=1`
- **Tenant-ID**: `RATIONS_DLG_MERGED_TENANT_ID=dlg` (Default)
- **Aufruf**: Header `X-Tenant-Id: dlg` bei `/api/v1/feeds`, `/api/v1/optimize/*` etc.

Quelle der Daten ist `data/reference/dlg_merged_feeds_lp.csv` (Loader: `app/utils/dlg_merged_csv.py`).

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
