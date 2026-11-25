---
title: M6 Spiegelbetrieb L3 -> VALEO
type: plan
audience: [entwickler, fachbereich, betrieb]
owner: Claude Code
status: aktiv
last_reviewed: 2026-11-25
version: 1.0.0
description: Plan und Stand des Spiegelbetriebs - vorhandene Strecke, Uebernahme mit Quellreferenz und Differenzbericht, L3-Tabellen je Objektart, Abnahmekriterien, Blocker.
---

# M6 Spiegelbetrieb L3 -> VALEO

Nutzerauftrag 25.11.2026; Fahrplan `docs/roadmap/fahrplan-verkaufsprodukt.md` (M6). L3 bleibt fuehrend. VALEO
vollzieht nach und weist die fachliche Gleichwertigkeit nach. Rueckwirkungen auf L3 sind ausgeschlossen.

## 1. Strecke

Es gibt keine zweite Importstrecke. Die vorhandene Adapterstrecke (`app/services/legacy_interface_adapter_service.py`,
Tabellen `domain_integration.legacy_adapter_*`, RLS) wird fortgesetzt:

| Schritt | Wirkung | Stand |
|---|---|---|
| Profil | Formatvertrag und Feldzuordnung L3-Spalte -> kanonisches Feld; Profil `l3_spiegel` (Datenbankabzug) | vorhanden, `l3_spiegel` neu |
| Annahme | Abzug als Batch; gleiche `external_id` mit anderem Inhalt wird abgewiesen | vorhanden |
| Staging | kanonische Zeilen mit `record_type` und `source_ref` | vorhanden |
| Abgleich | Menge Quelle = Staging, ungueltige Zeilen -> Quarantaene | vorhanden |
| Freigabe | nur abweichungsfreie Batches | vorhanden |
| **Uebernahme** | in die Fachtabellen, je Zeile mit Quellreferenz und Protokoll | **neu** (`app/services/spiegel_uebernahme.py`) |
| **Differenzbericht** | Summen, Fehlerzeilen, geaenderte Felder (L3 gegen VALEO) | **neu** |

Uebernahmeregeln:

- **Idempotent.** `domain_integration.spiegel_quellreferenzen` bildet (Quellsystem, Objektart, Quellschluessel) auf
  genau ein Zielobjekt ab und speichert die Pruefsumme des Inhalts. Ein wiederholter Abzug ergibt "unveraendert".
- **Nachvollziehbar.** `spiegel_protokoll` haelt je Zeile und Lauf "neu", "geaendert", "unveraendert" oder "fehler"
  mit den Felddifferenzen fest. Die Tabelle wird nur fortgeschrieben, Korrekturen sind neue Laeufe. Dazu kommt das
  Adapter-Audit.
- **Nichts erfinden.** Unbekannte Artikelgruppe oder Mengeneinheit, ein VALEO-Objekt ohne Quellreferenz mit gleicher
  Nummer oder eine nicht freigegebene Objektart erzeugen jeweils eine Fehlerzeile. Keine Annahme, keine stille
  Zusammenfuehrung.
- **Zeilenweise.** Jede Zeile laeuft in einem eigenen Sicherungspunkt. Eine fehlerhafte Zeile bricht den Lauf nicht ab.
- **Keine Rueckwirkung.** Das Modul liest nur das VALEO-Staging und hat keinen Weg zu L3. Die Abzuege erstellt eine
  Person aus L3 (Export). Ein Datenbankzugang mit Schreibrecht auf L3 wird nicht eingerichtet.

## 2. L3-Tabellen je Objektart

Quelle: `L3_Uebersicht Tabellen und Spalten.csv` (Repository und Desktop byte-gleich, Stand 21.07.2025, vom Nutzer
am 25.11.2026 als L3 bestaetigt). Die Datei umfasst 2.158 Tabellen. Die Warenwirtschaft liegt unter `WWS_*` (764
Tabellen); Tabellen ohne Praefix stammen grossteils aus weiteren zvoove-Modulen (z. B. Personal). Die Zuordnung
unten beruht auf Tabellen- und Spaltennamen, die **Bedeutung der Spalten ist am Abzug zu bestaetigen**.

| Objektart | L3-Tabellen (Kandidaten) | VALEO-Ziel | Stand Uebernahme |
|---|---|---|---|
| Artikel | `WWS_ARTIKEL` (180 Spalten, u. a. ARTIKELNR, ARTIKELGRP, BEZEICHN1/2, ME1, GESPERRT, BEWERTART, HAUPTARTIKELNR) | `domain_inventory.articles` | **umgesetzt** (Kernfelder) |
| Artikelgruppe | `WWS_ARTIKELGRP` (GRUPPE, BEZEICHNUNG, EINKKONTO, ERLKONTO, UMSATZGRP, ARTNRVON/ARTNRBIS/ARTNRLFD) | `domain_shared.warengruppen` (Hierarchie Haupt/Ober/Waren) | offen - Zuordnung zur dreistufigen Hierarchie ungeklaert |
| Alternativ-Einheiten | `WWS_ARTIKELEINH` (EINHSCHL, UMRECHNUNG, UMR_ZU_EINH, GEBINDE, RUNDEN) | Gebindefaktoren Stufe 3 (#191) | offen - Umrechnungsrichtung ungeklaert |
| Kunden | `KUNDEN` (KUNDENNR, KUNDNAME, USTID, SPERRE; Anschrift ueber ADRNR1 aus `ADRESSEN`, im Abzug verbunden) | `domain_crm.customers` (fuehrt die Debitoren im Uebergang) | **umgesetzt** (Kernfelder); DEBITORKTO ohne Ziel bis ADR Stufe 3b (`business_partners.debtor_account`), im Differenzbericht als nicht zugeordnet |
| Lieferanten | `KUNDEN` mit KREDITORKTO, `WWS_ARTLIEF`, `WWS_LIEFERANTEN_PREISE` | Lieferantenstamm, Ziel Geschaeftspartner | offen - Zielstamm im Partnermodell klaeren |
| Preise / Konditionen | `WWS_ARTPREIS1/2`, `WWS_PREISTAB1/2`, `WWS_KUNDEN_PREISE`, `WWS_PREISLISTE1-3`, `WWS_AKTIONSPREISE`, `KONDITIONEN`, `WWS_RABATTSTAFFEL1/2` | Preisfindung (pricing) | offen |
| Bestaende / Bewegungen | `WWS_ARTBESTAND`, `WWS_LAGERBESTAND`, `WWS_ARTBEWEGUNG*`, `WWS_LAGERPLATZ` | Bestandsjournal ueber den Buchungsdienst | offen - Anfangsbestand als Bestandsvortrag (#206) |
| Angebote | `WWS_ANGEBOT`, `WWS_ANGEBOT_POS`, `WWS_KAUFANGEBOT*` | DocFlow | offen |
| Auftraege | `WWS_VERKAUF1/2`, `AUFTRAG` | DocFlow | offen |
| Lieferscheine | `WWS_VLIEFER1/2` (Verkauf), `WWS_ELIEFER1/2` (Einkauf) | DocFlow | offen |
| Bestellungen | `WWS_BESTELLUNG1-3` | DocFlow | offen |
| Rechnungen | `WWS_ARECHNUNG1-5` (Ausgang), `WWS_EINKAUF1/2`, `RECHNUNG_EINGANG` | DocFlow, Buchung ueber Finance | offen |
| Offene Posten | `FIBU_OP1` (KONTONR, RECHNNR, RECHNBETRAG, KZSH, OFFEN, MAHNSTUFE); Kontensalden je Jahr/Monat in `DEBITOREN`/`KREDITOREN` (EBVORTRAG, SIST01-12) | `domain_erp.offene_posten` ueber das Partnerkonto | **Abgleich umgesetzt** (`app/services/spiegel_op_abgleich.py`, liest nur): gleich / Betrag abweichend / fehlt in VALEO / fehlt in L3, Salden je Konto. Uebernahme der Anfangs-OPs offen - gehoert zum Saldenvortrag unter Finance |
| Kontrakte | `WWS_KONTRAKT1-6`, `WWS_KS_KONTRAKT*` | Kontrakte (Agrar) | offen |
| Dokumente | `DOKUVERWALTUNG`, `DOKVERW_DOCS`, `WWS_ARTIKEL_UNTERLAGEN`, `*_UNTERLAGEN` | DMS (Paperless) mit Belegbezug | offen |

## 3. Reihenfolge

1. Stammdaten ohne Belegbezug: Mengeneinheiten, Artikelgruppen, Artikel, Partner.
2. Preise und Konditionen.
3. Anfangsbestaende als Bestandsvortrag ueber den Buchungsdienst (Schluessel `bestandsvortrag:`).
4. Offene Posten und Saldenvortrag (P0, nur mit Finanzabgleich).
5. Belege des Spiegelzeitraums: Angebot, Auftrag, Lieferschein, Rechnung, Bestellung, Kontrakt; je Beleg Quellreferenz
   und Belegkette.
6. Taeglicher Abgleich (Belege, Betraege, Bestaende) und monatlicher Abgleich (offene Posten, Journal, UStVA).

## 4. Abnahmekriterien (Nutzer 25.11.2026)

| Kriterium | Nachweis |
|---|---|
| Vollstaendiger Abgleich der Stammdaten | Differenzbericht ohne Fehlerzeilen je Objektart |
| Keine ungeklaerten Differenzen bei Finanzdaten | Monatsabgleich OP/Journal/UStVA = 0 offene Punkte |
| Konsistente Bestaende und Mengen | Tagesabgleich Bestand je Artikel/Lager |
| Vollstaendiger Belegfluss | Belegkette je Vorgang mit Quellreferenzen |
| Mandantentrennung | RLS auf allen Spiegeltabellen, Fremdmandanten-Probe |
| Reproduzierbarkeit | Wiederholter Abzug -> nur "unveraendert" (Test) |
| GoBD | nur fortgeschriebenes Protokoll, Audit, Quellreferenz je Objekt |
| E2E-Tests | Strecke Annahme bis Uebernahme gegen echte DB (`tests/test_spiegel_uebernahme.py`), je Objektart erweitert |
| Keine Schreibzugriffe auf L3 | kein Schreibweg vorhanden (Abschnitt 1) |
| Fachliche Abnahme | Abnahmeblatt `config/l3-cutover-uat.yaml` mit Rollenfreigaben |

## 5. Blocker

| Blocker | Art | Wer |
|---|---|---|
| L3-Abzug (Export der `WWS_*`-Tabellen, Format und Zeichensatz) | extern | Nutzer, Folkerts-IT |
| STAGING-Umgebung (Spiegelbetrieb laeuft nicht auf der Entwicklungsmaschine) | extern/Betrieb | Nutzer |
| Spaltenbedeutungen (z. B. ME1 = Mengeneinheiten-Nummer, BEWERTART-Schluessel) | fachlich, am Abzug zu bestaetigen | Claude mit Nutzer |
| Artikelgruppe -> dreistufige Warengruppen-Hierarchie | fachlich | Nutzer |
| Haupt-Artikel/Varianten | `WWS_ARTIKEL.HAUPTARTIKELNR` ist der einzige Verweis, eine Variantentabelle gibt es nicht; dass der Reiter VARIANTEN die verweisenden Artikel zeigt, ist **Annahme** | L3-Aufnahmen angekuendigt |

Intern umsetzbar ohne Blocker: Objektarten nach demselben Muster (Zielfunktion je Objektart), Tagesabgleich gegen
synthetische Abzuege und Abgleichsbericht als Maske.
