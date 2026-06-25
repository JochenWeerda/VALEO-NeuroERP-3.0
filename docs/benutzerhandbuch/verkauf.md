---
title: Vom Auftrag zur Rechnung
type: how-to
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Vom Auftrag zur Rechnung

Der Verkaufsprozess folgt der Belegkette **Auftrag → Lieferschein → Rechnung**.
Die Belege teilen dasselbe Layout (Gewohnheits-Prinzip), sodass Sie sich überall
sofort zurechtfinden.

## Voraussetzungen

- Modul **Verkauf** ist freigeschaltet.
- Kunde und Artikel sind als Stammdaten vorhanden.

## 1. Auftrag anlegen

1. Bereich *Verkauf* → *Aufträge* → *Neu*.
2. Kunde wählen (Kundenauswahl), Lieferbedingungen prüfen.
3. Positionen erfassen (Artikel, Menge, Preis).
4. **Speichern**. Der Auftrag erhält eine Auftragsnummer.

## 2. Lieferschein erzeugen

1. Auftrag öffnen → Aktion **Lieferschein erstellen**.
2. Liefermengen und Gewichte prüfen (ggf. Gefahrgutpunkte/Gewicht beachten).
3. **Speichern**. Der Lieferschein referenziert den Auftrag.

## 3. Rechnung erstellen

1. Lieferschein öffnen → Aktion **Rechnung erstellen**.
2. Rechnungsdatum und Positionen prüfen (Netto, MwSt).
3. **Speichern/Freigeben**. Die Rechnung geht in die Offene-Posten-Verwaltung.

**Ergebnis:** Eine durchgängige, nachvollziehbare Belegkette vom Auftrag bis zur
Rechnung.

## Häufige Fehler

- **Kunde nicht gefunden:** über die Kundenauswahl suchen oder Stammdaten anlegen.
- **Aktion „Folgebeleg" fehlt:** Vorbeleg ist nicht im passenden Status
  (z. B. Auftrag nicht freigegeben).
- **Preis weicht ab:** Konditionen/Preisliste am Kunden prüfen.
