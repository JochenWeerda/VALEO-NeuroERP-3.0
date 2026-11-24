---
title: Bestandsbuchung - Wege, Konsolidierung und LVS-Verantwortung
type: reference
audience: [entwickler, fachbereich]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-24
version: 1.0.0
description: Analyse aller Schreiber ins Bestandsjournal, Zielbild ein Buchungsdienst mit Buchungsschluessel, LVS-Relevanz 0/1/2 nach Nutzerentscheid, Reihenfolge der Konsolidierung.
---

# Bestandsbuchung - Wege, Konsolidierung und LVS-Verantwortung

Nutzerentscheid 24.11.2026: Alle bestandswirksamen Bewegungen laufen in **einem** zentralen Bestandsjournal
zusammen; LVS und ERP fuehren keine konkurrierenden Bestaende. Vor der Umsetzung die vorhandenen Buchungswege
analysieren und konsolidieren - keine parallele Bestandsfuehrung.

## 1. Zentrales Bestandsjournal (vorhanden)

`domain_inventory.inventory_stock_movements` ist das Bestandsjournal. Seit PR #194 verhindert
`domain_inventory.bestandsbuchung_schluessel` doppelte Bewegungen je fachlichem Vorgang. Der kanonische
Buchungsdienst ist `InventoryService.process_stock_movement`
(`app/domains/inventory/application/services/inventory_service.py`): Mandant, Richtung
(`inventory_movement_direction`), Unterdeckung, Kommissionsware, Artikelbestand.

## 2. Befund: Schreiber am Buchungsdienst vorbei (Stand 24.11.2026)

| Schreiber | Artikelbestand mitgefuehrt | Richtungstabelle | Buchungsschluessel |
|---|---|---|---|
| `domains/inventory/api/stock_movements.py` -> `InventoryService.process_stock_movement` | ja | ja | nein |
| `services/warehouse_service.py` (Lagerplatz/LVS) | ja | ja | **ja** (#194) |
| `services/docflow_lagerzugang.py` (Wareneingang/Storno) | ja | - | **ja** (#194) |
| `endpoints/inventory_operations.py` (Korrektur, Schwund, MHD) | ja | ja | nein |
| `services/inventory_correction_service.py` | ja | ja | nein |
| `endpoints/inventory_counts.py` (Inventur) | ja | nein | nein |
| `services/feed_inventory_link_service.py` | ja | nein | nein |
| `services/inventory_auxiliary_service.py` | ja | nein | nein |
| `endpoints/compat.py` (2 Stellen) | **nein** | ja | nein |
| `endpoints/pos_retoure.py` | **nein** | nein | nein |
| `endpoints/warehouse_transfers.py` (2 Stellen) | **nein** | nein | nein |
| `services/agri_flush_booking.py` | **nein** | nein | nein |
| `services/agri_lot_link_booking_service.py` | **nein** | nein | nein |
| `services/agri_silo_material_flow_service.py` (2 Stellen) | **nein** | nein | nein |
| `services/inventory_count_close_service.py` | **nein** | nein | nein |
| `services/mobile_sync_service.py` | **nein** | nein | nein |

Folge: Bei neun Schreibern laufen Journal und `articles.current_stock` auseinander; ohne Buchungsschluessel kann ein
wiederholtes Ereignis doppelt buchen. Ob ein Weg den Artikelbestand bewusst nicht fuehrt (z. B. Silo-Materialfluss
mit eigener Silobestandsfuehrung), ist je Weg zu pruefen - nicht pauschal anzunehmen.

## 3. Zielbild

1. **Ein Buchungsdienst:** `InventoryService.process_stock_movement` (erweitert um Buchungsschluessel, Transaktion
   beim Aufrufer, Lagerplatz) ist der einzige Weg ins Journal. Die Schreiber oben rufen ihn auf, statt SQL zu
   schreiben. Eine Ratsche verbietet neue direkte `INSERT INTO domain_inventory.inventory_stock_movements`.
2. **Buchungsschluessel Pflicht** fuer jeden Weg mit fachlichem Vorgang (`<quelle>:<beleg>:<position>:<art>`).
3. **LVS-Relevanz der Mengeneinheit** (`artikel_mengeneinheiten.lvs_relevanz`, PR #191), Nutzerentscheid:
   - **0 nicht relevant:** ERP-Bestandsfuehrung, sofern der Artikel bestandsgefuehrt ist.
   - **1 relevant:** LVS-Information (Lagerplatz, Lokalitaet) ohne zusaetzliche bestandswirksame Buchung.
   - **2 buchend:** die **bestaetigte Lagerplatzbewegung** ist die bestandswirksame Buchung. Der Belegweg
     (Wareneingang, Lieferschein) bucht dann nicht selbst, sondern erzeugt einen Einlager-/Auslagerauftrag; beide
     tragen denselben Buchungsschluessel, eine Bewegung je Vorgang.
4. Teillieferung (Schluessel je Teilmenge), Teilbuchung, Lagerplatzumbuchung (ein Schluessel je Ab-/Zugang),
   Retoure und Storno (eigener Schluessel, Grundlage Abbild bzw. Originalbewegung) laufen ueber denselben Dienst.

## 4. Reihenfolge

1. Buchungsdienst um Schluessel und Aufrufer-Transaktion erweitern; Ratsche "kein neuer Direktschreiber"
   (Baseline = heutige 13).
2. Wege mit Artikelbestand zuerst umstellen (Korrektur, Inventur, Futter, Hilfsdienst) - Verhalten gleich, nur
   ueber den Dienst.
3. Wege ohne Artikelbestand je Weg fachlich klaeren und umstellen (Umlagerung, POS-Retoure, Agrar/Silo, Mobil,
   Kompatibilitaet).
4. LVS 2 "buchend": Belegweg erzeugt Lagerauftrag statt Buchung; Lagerplatzbestaetigung bucht mit dem
   Belegschluessel.
