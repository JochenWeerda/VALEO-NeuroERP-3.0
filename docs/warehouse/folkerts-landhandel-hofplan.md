# Referenz-Hofplan: Folkerts Landhandel

**Zweck:** Orientierung fÃ¼r **statische Silo-Lage**, **Lager-/Logistik-Zonen** und **Verkehrs- bzw. Materialfluss** beim Modellieren in NeuroERP (WM-AGRI-SILO-001, spÃ¤ter WM-AGRI-MAP-001 Bird-View).

**Bilddatei (Repo):**

- `docs/warehouse/references/folkerts-landhandel-hofplan.png` (Archiv-/Doku-Kopie)
- `packages/frontend-web/public/warehouse/folkerts-landhandel-hofplan.png` (Auslieferung unter `/warehouse/folkerts-landhandel-hofplan.png` im Frontend)

## Ãœberblick (annotiertes Luftbild)

Das GelÃ¤nde zeigt einen typischen **Landhandels-Standort** mit getrennten Funktionsbereichen (Farblegende im Plan).

### Anlage / Technik (grÃ¼n)

- **Metall-Siloreihe:** ca. **sieben** hohe zylindrische Silos **am linken Rand** des Kernareals.
- **Annahme / Verladung:** GebÃ¤ude am **Ende der Siloreihe** bzw. angebunden an die Silolinie â€” Ein-/Ausgang von SchÃ¼ttgut und Verkehr.
- **Siloanlage (hexagonal):** markanter **weiÃŸer Turm mit rotem Dach**, zentral nahe den Silos â€” oft Ã¤ltere oder Sonderkammer; im Datenmodell als eigenes `silo_system` / Zellen denkbar.

### Lager / Logistik (blau)

- **Sackwarenlager:** groÃŸes zentrales GebÃ¤ude (Dach teils PV), **Sackware** im Schnitt dargestellt.
- **Regale / Hochregal:** angrenzender Hochregalbereich fÃ¼r Palettenware.
- **SchÃ¼ttgutlager (Amazone):** sehr groÃŸe **offene Halle rechts** mit sichtbaren SchÃ¼ttguthaufen; Dach rot, PV.

### Verwaltung (orange)

- **BÃ¼ro / Verwaltung:** Backsteinensemble mit orangefarbenem Dach, **unteres Zentrum** des Plans.

### Verkehr / FlÃ¤chen (grau)

- **Hof / Fahrwege:** asphaltierte Verbindungen zwischen allen Bereichen.
- **Verkehrsfluss:** **weiÃŸe Pfeile** auf dem Hof â€” Einfahrt unten rechts, im Wesentlichen **Umlauf** um die Kernbebauung, Anbindung LKW-Bereich, SchÃ¼ttguthalle, Zentrallager, Silo-/Annahmebereich.
- **LKW-Bereich:** StellflÃ¤chen (z. B. unten links im Bild) fÃ¼r Zubringer.

### Kompass

Kompassrose im Plan: **Norden** etwa nach **oben links** (fÃ¼r spÃ¤tere geo-Ausrichtung / MapLibre-Overlay).

## Nutzung in VALEO

| Thema | Umsetzung |
|--------|-----------|
| Silozellen | `silo_cells` mit `layout_x` / `layout_y` â€” Werkstatt-Layout auf Seite **Materialfluss â€” Visualisierung** |
| Prozessknoten | `material_flow_nodes` / `edges` â€” gleiche Layout-Koordinaten oder separates Graph-Layout |
| Bird-View / Luftbild | WM-AGRI-MAP-001: MapLibre, `geo_lat` / `geo_lng` an Knoten/Zellen |

Hinweis: Der Plan ist ein **konkreter Referenzstandort**; Mandantenfremde Nutzung nur mit RechteklÃ¤rung / Einwilligung des Betriebs.
