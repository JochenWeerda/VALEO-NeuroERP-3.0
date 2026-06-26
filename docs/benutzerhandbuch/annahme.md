---
title: Ernteannahme durchführen
type: how-to
audience: [endnutzer, power-user]
owner: Cursor
status: aktiv
last_reviewed: 2026-06-25
version: 3.0.0
---

# Ernteannahme durchführen

So nehmen Sie eine Anlieferung (z. B. Getreide) vollständig an – von der
LKW-Registrierung bis zur abgeschlossenen Annahme mit Qualitätsdaten.

![Leitstand Rohware-Annahme mit Vorgangslage, Kontext und nächster Aktion](img/annahme-rohware.webp)

## Voraussetzungen

- Modul **Agrar/Annahme** ist für den Mandanten freigeschaltet.
- Stammdaten (Lieferant, Artikel/Frucht, Silozellen) sind gepflegt.
- Sie haben die Rolle für die Annahme.

## Schritte

1. **Annahme öffnen:** Bereich *Annahme* → *Neue Annahme*.
2. **LKW registrieren:** Kennzeichen, Lieferant und Frucht erfassen.
3. **Erstwiegung:** Bruttogewicht von der Waage übernehmen.
4. **Probe & Qualität:** Qualitätswerte (z. B. Feuchte, Besatz, Protein)
   erfassen. Trocknungs-/Abzugsregeln werden automatisch angewendet.
5. **Zielzelle wählen:** passende Silozelle zuweisen (QS-Status beachten).
6. **Zweitwiegung:** Taragewicht erfassen → Nettomenge wird berechnet.
7. **Annahme abschließen:** Beleg prüfen und **Speichern/Abschließen**.

**Ergebnis:** Die Annahme ist gebucht, die Menge der Silozelle zugeordnet und
für Folgeprozesse (Kontrakt-Erfüllung, Abrechnung) verfügbar.

## Trocknungs- und Abzugsregeln

Feuchte über dem Grenzwert führt zu einem Mengen-/Wertabzug gemäß hinterlegter
Trocknungsregel. Die angewandte Regel und der Abzug sind im Beleg nachvollziehbar
ausgewiesen.

## Häufige Fehler

- **Silozelle gesperrt / falscher QS-Status:** andere Zelle wählen oder QS
  freigeben lassen.
- **Qualitätswert fehlt:** Pflichtfelder vor dem Abschluss vollständig erfassen.
- **Waage liefert keinen Wert:** Gewicht manuell erfassen und Grund dokumentieren.

## Quellen und Reverse-Pflege

- `packages/frontend-web/src/app/navigation/domains/operations.tsx`: Annahme & Waage.
- `docs/benutzerhandbuch/agrar-kontrakte.md`: Kontrakt-Erfüllung nach Annahme.
- `docs/benutzerhandbuch/qualitaetssicherung.md`: Probe und Qualitätsabschläge.
- `docs/agent-ops/slices/WM-AGRI-SILO-001.yaml`: Zielzellen/Silo-Zuordnung.

Reverse-Pflege: Bei Trocknungsregeln, Waagen-Integration oder Zielzellenlogik
diese Seite und Agrar-Workflow-Doku aktualisieren.
