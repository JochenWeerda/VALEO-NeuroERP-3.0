# VK-019 - Queue-Repair historische `article_id`

**Slice:** VK-019 | **Status:** abgeschlossen | **Owner:** Codex  
**Datum:** 2026-03-28

## A - Workflow-Uebersicht

Historische Queue-Eintraege aus der Annahmekette koennen noch ohne `article_id` existieren. `VK-019` fuehrt einen konservativen Repair-Pfad ein, der vorhandene Freitext-Artikel nur dann aufloest, wenn die Zuordnung eindeutig ist. Ziel: kein Blind-Mapping, kein Medienbruch.

Entscheidung `Standardmaske vor Spezialmaske`:

- Repair erfolgt in der bestehenden Warteschlange.
- Kein separater Repair-Dialog, nur CTA + Ergebnis-Toast.

## B - Vollstaendige Card-Liste

1. `VK-019-C1` Repair-CTA fuer Queue-Eintraege ohne `article_id`
2. `VK-019-C2` Konservativer Repair-Endpoint mit eindeutiger Aufloesung
3. `VK-019-C3` Ergebnisfeedback + Refresh der Queue-Liste

## C - Mermaid-Diagramm

```mermaid
flowchart TD
    A[Queue-Eintrag ohne article_id] --> B[CTA Artikel reparieren]
    B --> C[POST /annahme/warteschlange/{id}/repair-article]
    C --> D{Eindeutiger Treffer?}
    D -->|ja| E[Queue-Update article_id + artikel]
    D -->|nein| F[Kein Update, Hinweis/Toast]
    E --> G[Queue-Refresh]
    F --> G
```

## D - Soll-Ist-Abweichungen

| ID | Soll | Ist vor VK-019 | Bewertung |
|---|---|---|---|
| D-01 | Alt-Queue-Eintraege sollen eine echte `article_id` erhalten | Nur neue Eintraege haben `article_id`; Alt-Eintraege bleiben Freitext | offen |
| D-02 | Repair darf nur bei eindeutiger Zuordnung schreiben | Kein Repair-Pfad vorhanden | offen |

## E - UI-/CRUD-Befunde

- Warteschlange braucht einen CTA fuer Eintraege ohne `article_id`.
- Repair muss Rueckmeldung geben, ohne den Operator zu blockieren.

## F - Risiken

### mittel

- Falsche Zuordnung bei Mehrdeutigkeit. Muss durch konservative Regeln verhindert werden.

## G - Konkrete Empfehlungen

1. Repair nur fuer eindeutige `article_number` oder exakten Namen erlauben.
2. Keine Blindmigration, keine Batch-Updates ohne Fachfreigabe.
3. Toast mit Grund, wenn Repair nicht moeglich ist.

## Annahmen

- Alt-Eintraege besitzen zumindest `artikel` mit exakter `article_number` oder Name.
- Kein weiterer Prozess haengt an einem automatischen Repair-Lauf.

## Status

**Abgeschlossen** â€” Repair-CTA und Endpoint implementiert, Doku nachgezogen.
