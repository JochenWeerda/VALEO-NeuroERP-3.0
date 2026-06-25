---
title: Finanzbuchhaltung – Offene Posten, Mahnwesen, Zahlungen
type: how-to
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Finanzbuchhaltung – Offene Posten, Mahnwesen, Zahlungen

Behalten Sie Forderungen und Verbindlichkeiten im Blick, mahnen Sie überfällige
Posten an und verbuchen Sie Zahlungen.

![Hauptbuch mit Journalverlauf, Objektkontext und Wirtschaftslage](img/finanzbuchhaltung-hauptbuch.png)

## Offene Posten prüfen

1. Bereich *Finanzen* → *Offene Posten*.
2. Nach Typ (Forderung/Verbindlichkeit) und Fälligkeit filtern.
3. Beleg öffnen für Details und Mahnstatus.

## Mahnlauf durchführen

1. *Finanzen* → *Mahnwesen* → *Neuer Mahnlauf*.
2. Stichtag und Mahnstufen wählen.
3. Vorschlagsliste prüfen (Kunden, Beträge, Stufe).
4. **Mahnlauf freigeben**. Mahnungen werden erzeugt und der Mahnstatus erhöht.

## Zahlung verbuchen

1. *Finanzen* → *Zahlungen* → *Zahlungseingang erfassen*.
2. Kunde/Beleg zuordnen, Betrag erfassen.
3. **Buchen**. Der offene Posten wird ausgeglichen (oder teilausgeglichen).

!!! note "Zahllauf-Rückläufer"
    Rückläufer aus einem Zahllauf werden als Ereignis verbucht und der offene
    Posten wieder geöffnet.

**Ergebnis:** Offene Posten, Mahnstatus und Zahlungen sind konsistent und
GoBD-konform dokumentiert.

## Häufige Fehler

- **Zahlung nicht zuordenbar:** Verwendungszweck/Belegnummer prüfen.
- **Mahnung trotz Zahlung:** Zahlungseingang war zum Stichtag noch nicht gebucht.
- **Falsche Mahnstufe:** Mahnhistorie des Kunden prüfen.
