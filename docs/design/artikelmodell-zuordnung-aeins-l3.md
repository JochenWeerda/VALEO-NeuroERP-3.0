---
title: Artikelmodell - Zuordnung a.eins / L3 / VALEO
type: reference
audience: [entwickler, fachbereich]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-24
version: 1.0.0
description: Verbindliche Zuordnung der Artikelobjekte von a.eins (AMIC) und L3 (zvoove Handel) zu vorhandenen VALEO-Strukturen, mit Beleglage und offenen Punkten.
---

# Artikelmodell - Zuordnung a.eins / L3 / VALEO

Nutzerauftrag 24.11.2026: Vor weiterer Implementierung das vorhandene VALEO-Modell untersuchen, die a.eins-Ebenen
(Mengeneinheit, Artikelstamm, Artikel, Artikel-Auspraegung) verbindlich zuordnen, keine parallelen
Stammdatenstrukturen erfinden. Diese Datei trennt **belegt** (im Code/Schema oder in einer Referenz nachgewiesen)
von **offen** (fachlich zu klaeren).

## 1. Quellen

| Quelle | Inhalt |
|---|---|
| Schema `valeo_probe` / `valeo_neuro_erp` (24.11.2026) | Tabellen und Spalten, Schluessel, Bestand |
| Migrationen `fachliche_vertiefung_wave6/9/10_20260521` | Mengeneinheiten/-gruppen, Artikelverpackung; individuelle Artikelnummern; Haupt-/Ober-/Warengruppen |
| Skill `l3-stammdaten-referenz` (Live-Erkundung L3) | Artikel-Stamm-Maske (14 Reiter), Artikel-Gruppen, Mengen-/Gebinde-Einheiten, Haupt-Artikel-Nr., VARIANTEN |
| Nutzer-Recherche L3-Analysen 2025 (24.11.2026) | Artikelnummer-Konvention, ARTIKEL-GRP, Feldliste, Master-Nr. |
| a.eins-Hilfe (vom Nutzer eingefuegt) | Mengeneinheit, Gebinde, Gebindetypen, Faktorherkunft, LVS |

Die frueher erwaehnte lokale a.eins-Sammlung `docs/Referenz-ERP-reference/` ist im Repository nicht (mehr) vorhanden.

## 2. Zuordnung

| Fachobjekt | a.eins | L3 | VALEO (vorhanden) | Stand |
|---|---|---|---|---|
| Mengeneinheit | Mengeneinheit (Grund-/Gebinde-ME) | Mengen-Einheiten, Gebinde-Einheiten | `domain_shared.artikel_mengeneinheiten` (Wave 6, erweitert #186/#191) | **belegt** |
| Mengeneinheitsgruppe | Zuordnung zum Artikel - ME-Gruppe | Alternativ-Einheiten am Artikel (Reiter EINHEITEN) | `domain_shared.artikel_mengeneinheitengruppen` (Wave 6); `domain_inventory.article_units` (nur `create_all`, 0 Zeilen) | belegt, **nicht mit `articles` verknuepft** |
| Artikelverpackung | Artikelverpackung | Gebinde / Gebinde-Nr. | `domain_shared.artikel_verpackungen` (Wave 6, 3 Stufen) | belegt, nicht verknuepft |
| Haupt-/Ober-/Warengruppe | Haupt-/Ober-/Warengruppen | Artikel-Gruppe (ARTIKEL-GRP) | `domain_shared.hauptwarengruppen` -> `oberwarengruppen` (`haupt_id`) -> `warengruppen` (`ober_id`) (Wave 10) | belegt; **`articles.warengruppe` ist Freitext ohne Fremdschluessel** |
| Artikel | Artikel | Artikel-Nr. (Artikel-Stamm F3) | `domain_inventory.articles` (Schluessel `(id, tenant_id)`) | **belegt** |
| Individuelle Artikelnummer | Individuelle Artikelnummern | Kunden-/Lieferanten-Art.-Nr. | `domain_shared.individuelle_artikelnummern` (Wave 9) | belegt |
| Artikelstamm | eigene Ebene ueber dem Artikel | Modul heisst "Artikel-Stamm", ist aber die Artikelmaske selbst | **kein Gegenstueck** | **offen** |
| Artikel-Auspraegung | eigene Ebene unter dem Artikel | Reiter VARIANTEN; Block "Haupt-Artikel-Nr." (Verknuepfung zu uebergeordnetem Artikel) | **kein Gegenstueck**; keine Haupt-Artikel-Spalte in `articles` | **offen** |
| Master-Nr. | - | Feld in Einkauf-Lieferschein-Positionen | `master_nr` nur im Schema `einkauf_lieferschein` (Position), ohne Fachbedeutung | **offen** |

Folgerung fuer die Gebinde-Faktorherkunft (unveraendert vier a.eins-Stufen):

- Stufe 1 Mengeneinheit -> Stammsatz der Mengeneinheit. **Pflegbar.**
- Stufe 3 Artikel -> `domain_inventory.articles`, Fremdschluessel `(artikel_id, tenant_id)`. **Pflegbar.**
- Stufe 2 Artikelstamm und 4 Auspraegung -> **nicht pflegbar (422)**, bis zugeordnet. Der Suchpfad laeuft ueber die
  vorhandenen Stufen nach unten.

## 3. Nicht gleichsetzen

- **Artikelgruppe ist nicht Artikelstamm.** In L3 ist die Artikel-Gruppe ein eigenes Objekt (ARTIKEL-GRP), auf das
  andere Bereiche verweisen; in VALEO entspricht ihr die Warengruppen-Hierarchie (Wave 10), nicht eine Gebindestufe.
- **L3 "Artikel-Stamm" ist nicht a.eins "Artikelstamm".** In L3 ist es der Name der Artikelmaske (Ebene Artikel).
- **L3 "Haupt-Artikel-Nr." / VARIANTEN ist ein Kandidat fuer a.eins "Auspraegung"** oder fuer "Artikelstamm"
  (der Haupt-Artikel als uebergeordnete Produktidentitaet). Welche Richtung gilt, ist nicht belegt.

## 4. L3-Nummernsystem (Migration, kein Systemzwang)

Bei Folkerts bilden die ersten drei Stellen der L3-Artikelnummer die Artikelgruppe (220050 -> Gruppe 220; Nutzer-
Recherche, Rennerlisten-Auswertung 03.09.2025). Das gehoert in die **L3-Uebernahme** (Ableitung der Warengruppe beim
Import), nicht als Pflichtregel in VALEO - andere Mandanten nummerieren anders. Im gewachsenen Bestand von
`valeo_neuro_erp` (Testdaten, 132 Artikel) kommt die Konvention nicht vor.

## 5. Offene Punkte (fachlich zu klaeren)

1. **Artikelstamm und Auspraegung in a.eins** - Bedeutung laut Hilfe ("Artikelstamm und Artikel - Uebersicht",
   Auspraegungsseite; beim Nutzer angefragt).
2. **L3 Haupt-Artikel-Nr. und VARIANTEN** - an einem Artikel der Art "Variante"/"Baugruppe" erkunden (Skill
   `l3-stammdaten-referenz`: Reiter nur bei typisierten Artikeln sichtbar).
3. **L3 Master-Nr.** - Bedeutung in der Einkauf-Lieferschein-Position.
4. **`articles.warengruppe`** - Freitext an die Warengruppen-Hierarchie binden (Fremdschluessel); Altwerte sind
   Testdaten. Eigener Schnitt.
5. **Mengeneinheitsgruppe und Artikelverpackung an den Artikel binden** - beide existieren (Wave 6), ohne Bezug zu
   `articles`; `article_units` existiert nur ueber `create_all`. Konsolidieren statt neu anlegen. Eigener Schnitt.

Gewuenscht vom Nutzer, um 1-3 zu schliessen: L3-Masken Artikel-Stamm (alle Reiter), Artikelgruppen-Stamm,
Gebindestamm, Mengeneinheiten-Stamm.
