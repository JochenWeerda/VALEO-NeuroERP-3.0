---
title: Lieferschein-Statuswerte — drei Schreibweisen in einer Spalte
type: reference
audience: [entwickler, agent, fachbereich]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-29
version: 1.0.0
description: Welche Zustände ein Lieferschein annimmt, warum die Prüfbedingung sie nicht kannte, und welche Entscheidung offen bleibt.
---

# Lieferschein-Statuswerte

## Was gefunden wurde

`domain_sales.delivery_notes.status` trug eine Prüfbedingung mit fünf Werten
(`ck_delivery_notes_status`, aus der Tabellenanlage vom 16.02.):

    draft, printed, delivered, invoiced, cancelled

Der Code schreibt **neun**. Vier davon kannte die Bedingung nicht:

| Wert | geschrieben von |
|---|---|
| `posted` | `POST /sales/delivery-notes/{id}/post` |
| `shipped` | `POST /sales/delivery-notes/{id}/ship` |
| `BERECHNET` | `collective_documents.py` (Sammelrechnung) |
| `storniert` | `sales_storno_service` |

Auf einer frischen Datenbank liefen Buchen, Versenden, Sammelrechnung und
Storno damit jeweils in einen 500er — der Lieferschein kam über den Entwurf
nicht hinaus. Auf einer gewachsenen Entwicklungsdatenbank fiel das nie auf:
dort fehlt die Bedingung.

Behoben mit `lieferschein_status_bedingung_20260929`. Die Bedingung kennt
jetzt die neun Werte, die der Code schreibt — **und einen zehnten**:
`geliefert` liegt auf Bestandszeilen aus einem älteren Codepfad. Eine
Bedingung, die vorhandene Zeilen abweist, lässt sich nicht anlegen; und
Gebuchtes umzuschreiben, damit die Bedingung passt, wäre genau das, was die
GoBD verbieten (Rz. 107 ff.). Bestehende Zeilen sind nicht angefasst.

Das fiel erst beim Probelauf gegen die **gewachsene** Datenbank auf: Für das
*Schema* ist die frische Datenbank der Prüfstand, für die *Daten* die
gewachsene. Beide braucht es.

## Der Widerspruch, der dabei sichtbar wurde

In einer Spalte stehen drei Schreibweisen nebeneinander:

- englisch klein: `draft`, `printed`, `posted`, `shipped`, `delivered`,
  `invoiced`, `cancelled`
- deutsch klein: `storniert`, `geliefert` (nur noch im Bestand)
- deutsch groß: `BERECHNET`

Dabei gibt es zwei Paare, die dasselbe meinen könnten:
`cancelled` / `storniert` und `invoiced` / `BERECHNET`. Ob sie es tun, ist
nicht aus dem Code zu lesen — `invoiced` setzt der Einzelrechnungsweg,
`BERECHNET` der Sammelrechnungsweg. Zwei Namen für denselben Zustand bedeuten:
jede Auswertung über den Status ist nur so vollständig wie das Wissen
desjenigen, der die Abfrage schreibt.

## Was das kostet

Eine Liste „alle berechneten Lieferscheine" liefert je nach Filter die
Einzel- oder die Sammelrechnungen, nicht beide. Dasselbe gilt für Stornos.
Der Fehler ist leise: Das Ergebnis sieht vollständig aus.

## Offen — eine Entscheidung, keine Aufgabe

Drei Wege:

1. **Eine Schreibweise.** Alle Werte auf englisch klein; `BERECHNET` → `invoiced`,
   `storniert` → `cancelled`. Das ist eine Datenmigration auf gebuchten
   Belegen und braucht dieselbe Sorgfalt wie eine Umbuchung: Was ist der
   Beleg dafür, dass ein Wert geändert wurde?
2. **Zwei Zustände bleiben getrennt,** weil sie fachlich verschieden sind
   (Einzel- vs. Sammelrechnung). Dann brauchen sie Namen, die das sagen —
   `invoiced_single` / `invoiced_collective` — und keine zwei Sprachen.
3. **So lassen und dokumentieren.** Der jetzige Stand: Die Bedingung ist
   wahrheitsgemäß, dieses Dokument nennt die Fallstricke.

Der zweite Weg ist der wahrscheinlich richtige, wenn die Trennung
beabsichtigt war — das weiß der Fachbereich, nicht der Code.

## Für die nächste Prüfung

Dieselbe Lehre wie beim Kontenrahmen
(`docs/project-context/kontenrahmen-und-gobd-2026-09-29.md`):

**Eine gewachsene Entwicklungsdatenbank ist kein Prüfstand.** Sie hat
Bedingungen verloren, die eine frische Installation hat, und Tabellen und
Spalten gewonnen, die keine Migration anlegt. Beides verdeckt echte Fehler.

```bash
createdb valeo_probe
DATABASE_URL="postgresql://…/valeo_probe" python -m alembic upgrade head
DATABASE_URL="postgresql://…/valeo_probe" pytest tests/…
dropdb valeo_probe
```
