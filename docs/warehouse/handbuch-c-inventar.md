---
title: Inventar — Externes Handbuch C-Laufwerk
type: reference
audience: [entwickler]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-27
version: 3.0.0
description: Rekursive Durchsuchung und Inventarisierung des externen Handbuch-Verzeichnisses (Warenfluss-Stichworte, Stand 2026-06-13).
---

# Inventar: externes Handbuch `C:\Handbuch`

**Stand:** 2026-06-13 (rekursive Durchsuchung, Dateinamen + Stichwort-Strings in der Warenfluss-`.doc`)
**Hinweis:** Originaldateien verbleiben auf `C:\Handbuch`; **nicht** ins Repo kopiert. Nutzung nur im Rahmen der Betriebs-/Lizenzregeln.

## Bezug NeuroERP

| Slice / Thema | Repo |
|----------------|------|
| Agrar-Silo, Materialfluss-Knoten/Kanten, Route | [WM-AGRI-SILO-001](../agent-ops/slices/WM-AGRI-SILO-001.yaml) |
| UI Materialfluss + Layout-Werkstatt | `packages/frontend-web/src/pages/lager/materialfluss.tsx`, `materialfluss-visualisierung.tsx` |
| Referenz-Hofplan (Beispiel) | [folkerts-landhandel-hofplan.md](./folkerts-landhandel-hofplan.md) |

---

## Warenflussdiagramm (Haupttreffer)

| Datei | Pfad unter `C:\Handbuch` |
|--------|---------------------------|
| **D-10-01-02 Warenflussdiagramm-Brandhub.doc** | `Diverse Dokumente\` â€” **bevorzugt** |
| D-10-HACCP-01 Warenflussdiagramm-Brandhub.doc | `UngÃ¼ltige Dateien\` â€” Ã¤ltere/ersetzte Variante |

**Auszug aus lesbaren Textfragmenten** (Diagramm-Inhalt grob): Warenflussdiagramm; **3 Flachlager**; **6 Silozellen**; Wareneinkauf (Mais, Getreide, Mischfuttermittel, Getreide/Ã–lsaaten); Warenannahme; Lagerkontrolle; Einlagerung in Verladetanks / Verladesilos; Silo/Boxen; Aspekte bei Verladung; Stichworte wie Sensorik, HL-Gewicht, Feuchte (evtl. PrÃ¼f-/CCP-Kontext).

FÃ¼r vollstÃ¤ndige Grafik und FlieÃŸtext: Datei in Word Ã¶ffnen oder nach PDF exportieren und mit dem digitalen Modell (`material_flow_*`, `silo_cells`) abgleichen.

---

## Weitere verwertbare Dokumente (Namens-/Themenfit)

### Lager, Einlagerung, RÃ¼ckruf, Einkauf, Transport

- `F und L neu\F-6-01-01 Nachweis Ã¼ber Einlagerung.doc`
- `F und L neu\F-6-03-01 Lagerkontrolle.xls`
- `F und L neu\F-7-01-01 Notfallplan fÃ¼r WarenrÃ¼ckruf.doc`
- `VA und AA neu\V-7-02-01 Lieferantenbewertung, Wareneinkauf und Einkaufsabw.doc`
- `VA und AA neu\V-7-05-02 Transportabwicklung und Verladung.doc`

### Getreide / Futtermittel / Risiko

- `F und L neu\L-10-02-01 Risikoanalyse Getreide- u. Futtermittelhandel.xlsm`
- `F und L neu\L-10-03-02 Risikoanalyse Ã–lmÃ¼hle.xlsm`
- `VA und AA neu\V-7-04-01 Aufbereitung von Getreide.doc`

### HACCP / Hygiene / ISO

- `F und L neu\F-3-01-01 HACCP Team.xls`
- `F und L neu\F-6-07-01 Personalhygiene.doc`
- `VA und AA neu\V-6-02-02_Betriebs- und Lagerhygiene.DOC`
- `Diverses fÃ¼r lfd. Arbeiten\ISO-Ãœberwachung2010.xls`
- Unter `Diverse Dokumente\` / `Diverses fÃ¼r lfd. Arbeiten\`: QS-/Hygiene-Unterweisungen (Dateinamen mit â€žHygieneâ€œ, â€žQSâ€œ)

### Warenspezifikationen (Rohware / Ã–l)

Ordner `Spezifikationen\` u. a.:

- F-9-01-01 Weizen â€¦ bis F-9-07-01 Hafer (Word)
- F-9-08-02 Rapsexpeller.docm, F-9-09-01 RapsÃ¶l.docm
- `Warenbegleitpapier Rapsexpeller.doc` (sehr groÃŸe Datei; evtl. eingebettete Medien)

### Sonstiges

- `Diverses fÃ¼r lfd. Arbeiten\Monatliche Bestandsaufnahme â€¦ PSM-Lager.xls` â€” PSM-Lager (nicht Agrar-Hauptlager), dennoch fÃ¼r Bestands-/Listen-Pattern referenzierbar.

---

## OrdnerÃ¼bersicht `C:\Handbuch` (oberste Ebene)

- Diverse Dokumente
- Diverses fÃ¼r lfd. Arbeiten
- F und L neu
- Spezifikationen
- UngÃ¼ltige Dateien
- VA und AA neu

---

## Mapping-Idee (optional, fÃ¼r spÃ¤tere Modellierung)

| Handbuch-Thema | mÃ¶gliche ERP-/Slice-AnknÃ¼pfung |
|------------------|--------------------------------|
| Warenflussdiagramm (Silos/Flachlager/Verladung) | `material_flow_nodes` / `edges`, `silo_cells`, Visualisierung |
| Einlagerung / Lagerkontrolle | WMS-Bestand, Chargen, Inventur |
| WarenrÃ¼ckruf | Compliance / RÃ¼ckverfolgbarkeit (z. B. DOM-SUPPLY-004) |
| Risikoanalyse Getreide | QS-Stufen, `qs_status` Silozellen |
| Warenspezifikationen | Artikel-/QualitÃ¤tsstamm, Einkauf |

Bei Ã„nderungen am Ordner `C:\Handbuch` dieses Inventar manuell ergÃ¤nzen oder erneut scannen.
