# DOM-SALES-004 — Sales-Domäne Vertiefung
\
2026-06-23 | Owner: Claude Code | Slice: DOM-SALES-004

## Überblick

Drei Sales-Kernprozesse auf volle 004-Tiefe:

1. **Auftragsbestätigung-Lifecycle** (.2) — AB-Statusmaschine mit Audit-Log
2. **Lieferschein-Closing-Flow** (.3) — Kommissionierung → Versand → Quittierung
3. **Preisabweichungs-Eskalation** (.4) — Diff-Berechnung, Auto-Freigabe, Eskalation

---

## AB-Statusmaschine

```
DRAFT ──► VERSANDT ──► ANGENOMMEN
  │
  └──► ABGELEHNT (aus DRAFT oder VERSANDT)
```

- Jeder Übergang schreibt append-only in `sales_ab_status_log`
- Ablehnung: Begründungspflicht

---

## Lieferschein-Closing-Flow

```
OFFEN ──► KOMMISSIONIERT ──► VERSANDT ──► QUITTIERT
```

- Nur Vorwärts-Transitionen erlaubt (fail-closed)
- QUITTIERT: schreibt `quittiert_am` + `quittiert_von`
- Idempotent: bereits QUITTIERT → direkt zurückgeben

---

## Preisabweichungs-Schema

```
abweichung_pct = |angebots_preis - rechnungs_preis| / angebots_preis * 100

abweichung_pct ≤ 2.0% → AUTO_FREIGEGEBEN
abweichung_pct >  2.0% → ESKALIERT → manuelle Freigabe: FREIGEGEBEN | ABGELEHNT
```

- Standardschwelle: 2,0 %
- Eskalations-Freigabe mit Operator + Begründung
- Doppelte Prüfung desselben Auftrags/Artikels: idempotent
