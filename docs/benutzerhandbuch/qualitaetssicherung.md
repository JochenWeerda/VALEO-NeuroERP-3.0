---
title: Qualitätssicherung – Proben, Freigabe, Reklamation
type: how-to
audience: [endnutzer, power-user]
owner: Claude Code
status: aktiv
last_reviewed: 2026-06-26
version: 3.0.0
---

# Qualitätssicherung – Proben, Freigabe, Reklamation

Der QS-Leitstand steuert den Qualitätsprozess von der Probe-Entnahme über die
Laboranalyse bis zur Chargen-Freigabe oder -Sperrung.

## Voraussetzungen

- Modul **Qualitätssicherung** ist für den Mandanten freigeschaltet.
- Laborparameter und Prüfpläne sind als Stammdaten vorhanden.

## 1. QS-Probe anlegen

1. *Lager → QS-Leitstand* → **Neue Probe**.
2. Charge/Partie auswählen, Probenanzahl und Entnahmepunkt erfassen.
3. Zuständiges Labor und Prüfplan wählen.
4. **Speichern** — Probe erhält Status *In Prüfung*.

## 2. Laborergebnis erfassen

1. Probe öffnen → *Ergebnis erfassen*.
2. Messwerte je Parameter eingeben (z. B. Feuchte, Protein, Mykotoxine).
3. Abgleich mit Grenzwerten erfolgt automatisch.
4. Bei Überschreitung: Warnung erscheint, Freigabe-Button gesperrt.

## 3. Charge freigeben oder sperren

| Situation | Aktion | Folge |
|---|---|---|
| Alle Grenzwerte eingehalten | **Freigeben** | Charge disponierbar |
| Einzelne Überschreitung | **Bedingt freigeben** + Kommentar | Charge mit Vermerk |
| Kritische Überschreitung | **Sperren** | Charge nicht disponierbar |

## 4. Reklamation anlegen

1. *QS-Leitstand → Reklamationen* → **Neue Reklamation**.
2. Betroffene Charge/Lieferant angeben, Fehlerart und Menge erfassen.
3. Maßnahmen festlegen (Rücksendung, Gutschrift, Nachlieferung).
4. **Abschließen** sobald Maßnahmen erledigt.

## QS im Agrar-Kontext

Bei Ernte-Annahme wird die Probe direkt am **Wiegeschein** angelegt.
Ergebnisse beeinflussen automatisch die **Abrechnungsgrundlage** (Zu-/Abschläge
für Qualitätsparameter wie Feuchte, Protein, Hektolitergewicht).

## Häufige Fehler

- **Freigabe-Button grau:** Laborergebnis noch nicht vollständig erfasst.
- **Charge trotz Freigabe nicht disponierbar:** Bestandsbuchung prüfen (Einlagerung?).
- **Reklamation ohne Lieferantenbezug:** Lieferanten-Stammdaten prüfen.
