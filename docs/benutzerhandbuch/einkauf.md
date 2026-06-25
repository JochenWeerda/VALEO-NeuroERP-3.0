---
title: Einkauf – Bestellung, Wareneingang, Rechnungsabgleich
type: how-to
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Einkauf – Bestellung, Wareneingang, Rechnungsabgleich

Der Beschaffungsprozess folgt der Belegkette **Bestellvorschlag → Bestellung →
Wareneingang → Rechnungsabgleich (3-Wege-Match)**. Die Masken sind rollenfokus-
geführt und zeigen jederzeit die nächste nötige Aktion.

![Bestellübersicht mit Rollenfokus, Belegfähigkeits-Prüfung und Bestell-Follow-up-Plan](img/einkauf-bestellungen.webp)

## Voraussetzungen

- Modul **Einkauf** ist für den Mandanten freigeschaltet.
- Lieferant und Artikel sind als Stammdaten vorhanden.

## 1. Bestellvorschlag prüfen

1. Bereich *Einkauf* → *Bestellvorschläge* (Lager, Verkauf oder Rohware).
2. Vorschlagsmengen prüfen (Bedarf, Mindestbestand, offene Aufträge).
3. Vorschläge übernehmen oder anpassen.

## 2. Bestellung anlegen

1. *Einkauf* → *Bestellungen* → *Neue Bestellung*.
2. Lieferant wählen, Positionen erfassen (Artikel, Menge, Preis, Liefertermin).
3. **Speichern** und anschließend **Freigeben**.

## 3. Wareneingang buchen

1. Wareneingang zur Bestellung öffnen.
2. Gelieferte Mengen erfassen (Teil- oder Komplettlieferung).
3. **Buchen**. Der Bestand wird erhöht und die Bestellposition aktualisiert.

## 4. Rechnungseingang & 3-Wege-Match

1. *Einkauf* → *Rechnungseingang* → Rechnung erfassen.
2. Abgleich **Bestellung ↔ Wareneingang ↔ Rechnung** (Menge, Preis).
3. Bei Übereinstimmung freigeben; Abweichungen klären (Gutschrift/Belastung).

**Ergebnis:** Eine durchgängige, prüfbare Beschaffungskette mit korrekter
Bestandsführung und freigegebener Eingangsrechnung.

## Häufige Fehler

- **Wareneingang ohne Bestellbezug:** zuerst Bestellung freigeben.
- **Rechnung blockiert:** Mengen-/Preisabweichung im 3-Wege-Match prüfen.
- **Bestellvorschlag leer:** Mindestbestände/Bedarfe an den Artikeln prüfen.
