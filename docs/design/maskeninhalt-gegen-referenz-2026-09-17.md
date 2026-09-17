---
title: Maskeninhalt gegen Referenz
type: reference
audience: [design, entwickler, agent]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-17
version: 1.0.0
description: Was in den Masken fachlich fehlt, gemessen an der L3-Tabellenreferenz im Repo — und warum kein Gate das sieht.
---

# Maskeninhalt gegen Referenz

## Warum das kein Gate gefunden hat

Drei Gates laufen über die Masken, und alle drei sind blind für diese Frage:

| Gate | Prüft | Sieht **nicht** |
|---|---|---|
| `check_frontend_api_calls` | Gibt es die Route? | ob sie das Richtige liefert |
| `check_field_contracts` | Heißen die Schlüssel gleich? | ob die *richtigen* Felder da sind |
| `check_table_references` | Gibt es die Tabelle? | ob die Maske ihre Spalten nutzt |

Ein Feld, das **fehlt**, ist in keinem dieser Verträge ein Fehler: Die Maske
fragt es nicht an, der Endpunkt liefert es nicht, beide sind sich einig. Genau
so blieb am Kundenstamm die Bankverbindung jahrelang unsichtbar, obwohl Spalte,
Schreibpfad und sogar eine eigene Tabelle vorhanden waren.

**Fachliche Vollständigkeit lässt sich nur gegen eine Referenz messen, nicht
gegen sich selbst.**

## Welche Referenz im Repo liegt

- **`docs/data/l3/raw_tables.json`** — 2.158 L3-Tabellen mit ihren Feldern.
  Das ist der belastbare Maßstab für Feldvollständigkeit und liegt seit
  Oktober 2025 im Repo.
- **Nicht vorhanden:** die 5.118 L3-Hilfeseiten unter `docs/amic-reference/`.
  Der Ordner existiert nicht (mehr). Wer Masken*layouts* vergleichen will,
  braucht eine neue Quelle — Screenshots, SAP- oder Odoo-Referenzen.

Die Tabellenreferenz beantwortet „welches Feld fehlt", nicht „wie ist es
angeordnet". Für die zweite Frage fehlt das Material.

## Befund 1 — Kundenstamm

**Drei Masken nebeneinander** für dasselbe Objekt:
`verkauf/kunden-stamm` (2.394 Zeilen, 10 Reiter), `crm/kunden-stamm` (789),
`crm/kim/index` (1.182).

**Bankverbindung** war in keiner eintragbar — behoben (Commit `8774c9a92`).
Die Maske schickte `banking` als Rumpf aus lauter `null`. Vorhanden waren die
ganze Zeit: die Spalten an `domain_crm.business_partners`, der Schreibpfad in
`business_partners.py`, und `domain_shared.kunden_bankverbindungen` für mehrere
Konten je Kunde — das Gegenstück zu L3 `KUNDEN_BANKEN`.

**Ansprechpartner** gibt es — in `verkauf/kunden-stamm`, Reiter 4. In den
beiden anderen Kundenmasken nicht. Wer über `/crm` einsteigt, findet sie nicht.

**Interne Nummern als Beschriftung:** Die Reiter heißen „Tab 23 Anschriften",
„Tab 24 Rechnung/Kontoauszug", „Tab 25 CPD-Konto". Das sind L3-Reiternummern,
die in die Oberfläche durchgeschlagen sind. Ein Anwender, der L3 nicht kennt,
liest dort eine Nummer ohne Bedeutung.

**Offen gegen L3:** `RUECKLASTSCHRIFT_*` (6 Tabellen) — Rücklastschriften sind
im Landhandel Alltag und haben bei uns keinen Ort.

## Befund 2 — Einkaufsbestellung

**Vier Masken:** `bestellung-anlegen` (771 Zeilen), `bestellung-native` (7),
`bestellung-stamm` (870), `bestellungen-liste`.

Die Erfassungsmaske führt **neun Felder**: Lieferant, Lieferdatum,
Zahlungsbedingungen, Incoterms, Lieferadresse, Artikel, Menge, Einheit, Preis.

L3 führt im Bestellkopf (`WWS_BESTELLUNG1`) **52**, in der Position
(`WWS_BESTELLUNG2`) **53**. Was davon im Landhandel gebraucht wird und bei uns
fehlt:

| Feld (L3) | Wofür |
|---|---|
| `ANSPRPARTNER` | Ansprechpartner beim Lieferanten — dieselbe Lücke wie beim Kunden |
| `ANFRAGENR` / `ANGNRLIEF` | Bezug auf Anfrage und Lieferantenangebot; ohne das ist die Kette gerissen |
| `KONTRAKTNR` / `KONTRAKTPOS` | Kontraktabruf an der Position — im Verkauf haben wir das Mengenmodell, im Einkauf nicht |
| `LADETERMIN` / `LADEDATUM` | Ladetermin getrennt vom Liefertermin — Disposition hängt daran |
| `LAGER` | Welches Lager oder Silo die Ware annimmt |
| `SKONTO1TG/PR`, `SKONTO2TG/PR`, `NETTOTG` | Skontostaffel; wir haben ein pauschales „Zahlungsbedingungen" |
| `LIEFARTNR` | Artikelnummer des Lieferanten — steht auf seiner Rechnung |
| `GEBINDEMG/SCHL/EINH`, `PREISEINH` | Gebinde und Preiseinheit; ohne sie ist ein Tonnenpreis nicht von einem Sackpreis zu unterscheiden |
| `GEWICHT` | Gewicht zur Frachtdisposition |
| `FREMDWAEHRUNG`, `UMRFAKTOR` | Fremdwährungsbestellung |
| `KOSTENST`, `KOMMISSION` | Kontierung und Kommissionsbezug |

Das ist kein Feinschliff. Ohne Kontraktbezug und Ladetermin ist die Maske für
den Agrarhandel nicht benutzbar — sie beschreibt eine allgemeine Bestellung,
nicht die des Hauses.

## Befund 3 — Maskenvermehrung

Drei Kundenmasken, vier Bestellmasken. Das ist die Ursache hinter „überfrachtet":
Nicht eine Maske trägt zu viel, sondern mehrere tragen je einen Teil, und keine
ist vollständig. Wer sie zusammenführt, muss vorher entscheiden, welche die
führende ist.

## Wie weitergearbeitet werden kann

Ein Feldabgleich je Maske gegen `raw_tables.json`, in der Reihenfolge der
Belegkette, und je Maske eine Entscheidung: welche Felder kommen, welche
bleiben bewusst weg. Das ist Fachentscheidung, keine Fleißarbeit — die 52
L3-Felder sind nicht alle sinnvoll, und L3 ist nicht in allem Vorbild.

Was dafür fehlt: eine Layout-Referenz. Die Tabellen sagen, *welches* Feld,
nicht *wo*. Dafür braucht es Screenshots oder eine benannte Vorlage.
