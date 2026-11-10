---
title: Belegvertrag
type: reference
audience: [entwickler, integrator, agent]
owner: Codex
status: aktiv
last_reviewed: 2026-10-15
version: 1.0.0
description: Eine Form fuer alle Belegarten — Varianten, Bausteine und Abbildung der bisherigen Feldnamen.
---

# Belegvertrag

Erzeugt von `scripts/generate_belegvertrag.py` aus `app/core/belegvertrag.py`. Nicht von Hand ändern.

Version 1.0. Die Form steht in `contracts/belegvertrag.schema.json`.

## Varianten

| Belegart | Bezeichnung | Partner | Steuerrichtung | Preise | Finance bucht | Folgebelege |
|---|---|---|---|---|---|---|
| `sales_offer` | Angebot | kunde | verkauf | ja | nein | `sales_order` |
| `sales_order` | Auftrag | kunde | verkauf | ja | nein | `sales_delivery`, `sales_invoice` |
| `sales_delivery` | Lieferschein | kunde | verkauf | nein | nein | `sales_invoice` |
| `sales_invoice` | Rechnung | kunde | verkauf | ja | ja | `sales_credit_memo` |
| `sales_credit_memo` | Gutschrift | kunde | verkauf | ja | ja | — |
| `purchase_order` | Bestellung | lieferant | einkauf | ja | nein | `goods_receipt`, `purchase_invoice` |
| `goods_receipt` | Wareneingang | lieferant | einkauf | nein | nein | `purchase_invoice` |
| `purchase_invoice` | Eingangsrechnung | lieferant | einkauf | ja | ja | `purchase_credit_memo` |
| `purchase_credit_memo` | Einkaufsgutschrift | lieferant | einkauf | ja | ja | — |

Ohne Preise heißt: Der Server liefert weder die Preisfelder der Position (`einzelpreis`, `rabatt_prozent`, `steuerschluessel`, `steuersatz`, `netto`, `steuer`, `brutto`, `aufwandskonto`) noch `summen`. Dasselbe gilt für Leser ohne Preisrecht.

## Bausteine

Fachliche Sonderteile, die eine Variante einhängt; sie gehören nicht zum Grundgerüst.

| Baustein | Inhalt |
|---|---|
| `lieferung` | Liefer- und Ladetermine, Versandart, Incoterms, Lieferadresse, Selbstabholung, Fahrzeug |
| `zahlung` | Zahlungsbedingung, Faelligkeit, Skonto, Fremdwaehrung |
| `texte` | Betreff, Kopf- und Fusstext, Notizen |
| `kontakt` | Ansprechpartner beim Partner |
| `organisation` | Niederlassung, Kostenstelle, Kommission, Bearbeiter |
| `referenzen` | Eigene und fremde Referenzangaben |
| `kontierung` | Kreditoren- bzw. Debitorenkonto des Partners |
| `gebinde` | Gebindemenge und -einheit, Preiseinheit, Gewicht |
| `lager` | Lager, Halle, Fach |
| `kontrakt` | Bezug auf einen Kontrakt |
| `bestellfall` | Bestellfall mit Bedarfs-, Mindest- und Hoechstmengen |
| `einkauf` | Artikelnummer des Lieferanten |

## Abbildung der bisherigen Feldnamen

Je Beleg-ScreenDefinition: Feld im Reiter `kopf` und Spalte der Tabelle `positionen`.

### `einkauf/purchase-order`

| Bereich | Bisher | Im Vertrag |
|---|---|---|
| kopf | `bestellnummer` | `beleg_nr` |
| kopf | `status` | `status` |
| kopf | `lieferant_nr` | `partner.nummer` |
| kopf | `lieferant_name` | `partner.name` |
| kopf | `bestelldatum` | `belegdatum` |
| kopf | `waehrung` | `waehrung` |
| kopf | `netto_summe` | `summen.netto` |
| kopf | `brutto_summe` | `summen.brutto` |
| kopf | `bestellfall` | `baustein:bestellfall` |
| kopf | `kreditor_konto` | `baustein:kontierung` |
| kopf | `ansprechpartner` | `baustein:kontakt` |
| kopf | `niederlassung_name` | `baustein:organisation` |
| kopf | `kostenstelle` | `baustein:organisation` |
| kopf | `kommission` | `baustein:organisation` |
| kopf | `erstellt_von` | `baustein:organisation` |
| kopf | `lieferdatum_wunsch` | `baustein:lieferung` |
| kopf | `lieferdatum_zugesagt` | `baustein:lieferung` |
| kopf | `ladetermin_ab` | `baustein:lieferung` |
| kopf | `ladetermin` | `baustein:lieferung` |
| kopf | `lade_datum` | `baustein:lieferung` |
| kopf | `incoterms` | `baustein:lieferung` |
| kopf | `versand_art` | `baustein:lieferung` |
| kopf | `lieferadresse` | `baustein:lieferung` |
| kopf | `unsere_referenz` | `baustein:referenzen` |
| kopf | `ihre_referenz` | `baustein:referenzen` |
| positionen | `pos_nr` | `positionen[].pos_nr` |
| positionen | `artikel_nr` | `positionen[].artikel_nr` |
| positionen | `bezeichnung` | `positionen[].bezeichnung` |
| positionen | `menge` | `positionen[].menge` |
| positionen | `menge_geliefert` | `positionen[].menge_uebernommen` |
| positionen | `menge_offen` | `positionen[].menge_offen` |
| positionen | `einheit` | `positionen[].einheit` |
| positionen | `einzelpreis` | `positionen[].einzelpreis` |
| positionen | `betrag` | `positionen[].netto` |
| positionen | `lieferanten_artnr` | `baustein:einkauf` |
| positionen | `gebinde_menge` | `baustein:gebinde` |
| positionen | `gebinde_einheit` | `baustein:gebinde` |
| positionen | `preis_einheit` | `baustein:gebinde` |
| positionen | `gewicht_kg` | `baustein:gebinde` |
| positionen | `kontrakt_nr` | `positionen[].kontrakt` |
| positionen | `lager` | `baustein:lager` |
| positionen | `lagerhalle` | `baustein:lager` |
| positionen | `lagerfach` | `baustein:lager` |
| positionen | `mindestmenge` | `baustein:bestellfall` |
| positionen | `maximalmenge` | `baustein:bestellfall` |

### `finance/ap-invoice`

| Bereich | Bisher | Im Vertrag |
|---|---|---|
| kopf | `beleg_nr` | `beleg_nr` |
| kopf | `kreditor` | `partner.name` |
| kopf | `datum` | `belegdatum` |
| kopf | `status` | `status` |
| kopf | `brutto` | `summen.brutto` |
| kopf | `mwst` | `summen.steuer` |
| kopf | `faellig_am` | `baustein:zahlung` |
| positionen | `pos_nr` | `positionen[].pos_nr` |
| positionen | `bezeichnung` | `positionen[].bezeichnung` |
| positionen | `menge` | `positionen[].menge` |
| positionen | `betrag` | `positionen[].netto` |
