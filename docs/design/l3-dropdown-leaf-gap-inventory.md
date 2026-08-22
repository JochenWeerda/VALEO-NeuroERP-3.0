---
title: L3 Dropdown-Leaf Gap-Inventur
type: reference
audience: [product, fachbereich, entwickler]
owner: Cursor Agent
status: verifiziert
last_reviewed: 2026-08-22
version: 1.0.0
description: Funktionsabgleich der L3-Dropdown-Untermenues (Leaf-Ebene) gegen VALEO NeuroERP 3.0.
---

# L3 Dropdown-Leaf Gap-Inventur

## Ergebnis

Die Tiefenpruefung der L3-Dropdown-Baeume (read-only, August 2026) ergab **14 neue
repo-seitige Gaps** (4× P2, 8× P3, 2× P2-Buendel mit Unterpunkten). Die zuvor
geschlossenen P1-Gaps (Belegkontrolle-Worklist, MDE, Produktion usw.) bleiben
gueltig; die Dropdown-Leaf-Analyse schaerft **fehlende Spezialmasken und
Auswertungen**, die in der Ribbon-Icon-Erfassung nicht sichtbar waren.

**Kein neuer P0-Gap.**

## Methode

- **Evidenz:** OCR unter `C:\Users\Jochen\Pictures\L3-Capture-2026-08-19\ocr\`
  (F02, F06, F07, F11, C02, E05), Dropdown-Screenshot
  `final_aw_01_belegkontrolle.png`, Vollmasken-Log `full-mask-final.txt`.
- **Miss-Evidenz:** `submenu_beleg_*`, `submenu_mde_*`, `final_fav_03_artikel_konto`,
  `final_all_05_weitere` oeffneten faelschlich **PRODUKTION → Chargen-Nummern
  bearbeiten** (falsche Menue-Y-Koordinaten). Diese PNGs sind **keine**
  Belegkontrolle-/Weitere-Evidenz.
- **Positiv-Evidenz in VALEO:** aktuelle Seite, API oder kanonische Doku — nicht
  Archiv allein.
- **RDP 22.08.2026:** Sitzung `10.200.1.3` zum Capture-Zeitpunkt nicht aktiv;
  Leaf-Liste aus OCR + Code-Abgleich. Nachfolge-Capture:
  `scripts/l3-dropdown-leaf-capture.ps1`.

## Dropdown-Baeume (Leaf-Katalog)

### AUSWERTUNGEN → Beleg-Kontrolle (F02)

| L3-Leaf | VALEO | Bewertung |
|---|---|---|
| Unerledigte Bestellungen | `document_control` / `open_purchase_order` | vorhanden |
| Eingangslieferschein-Kontrolle | `missing_inbound_document` | vorhanden |
| Auftrags-Kontrolle ▶ | gefilterte Worklist moeglich | teilweise → L3-GAP-BELEGCHECK-SUB-030 |
| Lieferschein-Kontrolle ▶ | `blocked`/`uninvoiced` Typen | teilweise → L3-GAP-BELEGCHECK-SUB-030 |
| Gesperrte Lieferscheine | `blocked_delivery_note` | vorhanden |
| Nicht fakturierte Artikel | `uninvoiced_delivery_note` | vorhanden |

### AUSWERTUNGEN → Weitere (F11)

| L3-Leaf | VALEO | Gap |
|---|---|---|
| Volltextsuche Dokumentenverwaltung | `dms-service.search()` ohne Auswertungs-Maske | L3-GAP-DMS-FULLTEXT-025 |
| Fracht | `logistik/frachtbriefe`, Frachtauftraege | vorhanden |
| Bonus-Berechnung | nur Stammdaten-Flags (`bonus_eligible`) | L3-GAP-BONUS-021 |
| Genossenschaften | `genossenschaft/mitglieder` | vorhanden |
| Terrorschutzprüfung Personal | generische `compliance/sanktionspruefung` | L3-GAP-TERROR-SPLIT-029 |
| Terrorschutzprüfung Kunden | generische `compliance/sanktionspruefung` | L3-GAP-TERROR-SPLIT-029 |
| Änderungshistorie | Vertrag/Finance-Audit teilweise | L3-GAP-AUDIT-HIST-024 |
| Düngemittelmengen | `agrar/duenger/liste` ohne Mengen-Auswertung | L3-GAP-DUENG-MENGEN-022 |

### AUSWERTUNGEN → Artikel → Weitere (F06)

| L3-Leaf | Gap-ID |
|---|---|
| Chefauswertung Artikel-Gruppen | L3-GAP-ART-AUSW-027 |
| Verrechnungspreis-Lagerauswertung | L3-GAP-ART-AUSW-027 |
| Änderungen Einkaufspreise | L3-GAP-ART-AUSW-027 |
| Aktions-Auswertung | L3-GAP-ART-AUSW-027 |
| Übersicht Artikelbewegungen | L3-GAP-ART-AUSW-027 |
| Artikel-Umsätze | teilweise (`sales-by-article` Report) | Komfort in 027 |
| Artikel-Konto / Artikel-Konto drucken | L3-GAP-ARTKONTO-020 |
| Lager-Dispo | L3-GAP-ART-AUSW-027 |
| Suche/Biete | L3-GAP-ART-AUSW-027 |
| Getreidemeldung | L3-GAP-ART-AUSW-027 |
| MVO-Meldung | L3-GAP-ART-AUSW-027 |
| Tagesabschluss-Journal | L3-GAP-ART-AUSW-027 |

### AUSWERTUNGEN → Lager → Weitere (F07)

| L3-Leaf | Gap-ID |
|---|---|
| Auswertung Chargen-Nummern | L3-GAP-CHARGEN-AUSW-026 |
| Bestandsbewertung pro Chargen-Nummer | L3-GAP-CHARGEN-AUSW-026 |
| Rückverfolgung Chargen: Verwendung | L3-GAP-CHARGEN-AUSW-026 (Teil: `charge_lineage`, `futtermittel/charge-verfolgung`) |

### PRODUKTION → Chargen (E05)

| L3-Leaf | Gap-ID |
|---|---|
| Chargen-Nummern bearbeiten (Freigabe, Anerkennungs-Nr., Lief.-Charge) | L3-GAP-CHARGEN-EDIT-019 |

### ABRECHNUNG → Faktura Verkauf (C02)

| L3-Leaf | Gap-ID |
|---|---|
| EB Lieferschein-Kontrolle | L3-GAP-EB-LS-023 |

### FAVORITEN → Artikel-Konto

Icon vorhanden; Live-Klick oeffnete faelschlich Chargen-Maske. Fachinhalt =
Artikel-Konto → **L3-GAP-ARTKONTO-020** (unabhaengig vom Klickfehler).

## Priorisierte neue Gaps

### P2 — hohe Fachparitaet

| ID | Gap | Belegter Ist-Stand | Abnahmekriterium |
|---|---|---|---|
| L3-GAP-CHARGEN-EDIT-019 | Chargen-Nummern bearbeiten / Massenfreigabe | Einzel-`POST /charges/{id}/freigabe`; Saatzucht-Anerkennungsnr. separat | Operator-Maske: Filter Artikel/Charge/Lief.-Charge, Grid mit Freigabe-Status und Anerkennungs-Nr., Massenfreigabe, Audit |
| L3-GAP-ARTKONTO-020 | Artikel-Konto Sicht und Druck | Bewegungs-/Bestandssichten verstreut | Periodisches Artikel-Konto je Artikel/Niederlassung mit Saldo, Bewegungen, Druck/Export |
| L3-GAP-BONUS-021 | Bonus-Berechnung (Auswertung) | `bonus_eligible`/`allow_bonus` in Stammdaten/Abrechnung | Berechnungslauf je Periode/Kunde/Artikelgruppe mit Nachweis, Korrektur und Export |
| L3-GAP-DUENG-MENGEN-022 | Düngemittelmengen-Auswertung | Düngemittel-Stamm, keine Mengenmeldung | Tenant-Report N/P/K-Mengen je Kunde/Fläche/Periode, Export fuer Behoerdenformat |
| L3-GAP-EB-LS-023 | EB Lieferschein-Kontrolle vor Faktura | Verkaufsfaktura ohne EB-Vorpruefung | Worklist/Dialog „EB Lieferschein-Kontrolle“ mit Biomasse-/Nachhaltigkeitsregeln vor Rechnungslauf |
| L3-GAP-AUDIT-HIST-024 | Bereichsuebergreifende Änderungshistorie | Vertrags-Amendments, Finance-Audit-Trail | Einheitliche Historien-Maske fuer Stammdaten/Belege mit Feld-, User- und Zeitstempel |
| L3-GAP-CHARGEN-AUSW-026 | Chargen-Lager-Auswertungen (3 Reports) | `inventory-by-batch` im Report-Katalog | Drei feste Auswertungen: Chargen-Nummern, Bewertung pro Charge, Rueckverfolgung Verwendung |
| L3-GAP-ART-AUSW-027 | Artikel-Weitere-Auswertungen (Buendel) | Umsatz-Report einzeln | Mindestens: Verrechnungspreis-Lager, Einkaufspreis-Aenderungen, Artikelbewegungen, Lager-Dispo, Getreide-/MVO-Meldung, Tagesabschluss-Journal, Suche/Biete |

### P3 — Gewohnheit / Spezial

| ID | Gap | Abnahmekriterium |
|---|---|---|
| L3-GAP-DMS-FULLTEXT-025 | DMS-Volltext als Auswertungs-Einstieg | Navigierbare Maske unter Auswertungen mit Volltext, Filtern, Vorschau, Deep-Link zum Beleg |
| L3-GAP-TERROR-SPLIT-029 | Terrorschutz Personal vs. Kunden | Zwei gefuehrte Prueflaeufe mit getrennten Listen/Scopes neben generischer Sanktionspruefung |
| L3-GAP-BELEGCHECK-SUB-030 | Dedizierte Auftrags-/LS-Kontrolle-Submasken | Vordefinierte Filter/Layouts je Submenue oder equivalente gespeicherte Worklist-Ansichten |
| L3-GAP-KUND-AUSW-028 | Kunden-Weitere-Auswertungen | Auftrag-Disposition, Angebots-/Auftrags-Uebersicht, Kunden-Artikel, Bescheinigungen, Praesente |

## Bereits abgedeckt (kein neuer Gap)

Belegkontrolle-Kernfaelle (vier Exception-Typen), Fracht/Logistik, Genossenschaft,
Abfrage-Center, Dokumenten-Ruecklauf, MDE-Inbox, Standard-Schnittstellen-Rahmen,
Report-Katalog (7 Basisberichte), Sanktionspruefung (generisch).

## Evidenz und Capture-Nachzug

- Kalibrierte Dropdown-Y-Werte: [`l3-rdp-navigation-drill.md`](l3-rdp-navigation-drill.md)
- Capture-Skript: [`scripts/l3-dropdown-leaf-capture.ps1`](../../scripts/l3-dropdown-leaf-capture.ps1)
- Zielordner (lokal, nicht in Git): `C:\Users\Jochen\Pictures\L3-Capture-2026-08-22-dropdown-leaves`
