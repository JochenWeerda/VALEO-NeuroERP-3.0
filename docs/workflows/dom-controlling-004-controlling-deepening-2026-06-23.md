# DOM-CONTROLLING-004 — Controlling-Domäne Vertiefung
\
2026-06-23 | Owner: Claude Code | Slice: DOM-CONTROLLING-004

## Überblick

Drei Controlling-Kernprozesse auf volle 004-Tiefe:

1. **Budget-Lifecycle** (.2) — Planwert-Freigabe und -Aktivierung
2. **Plan/Ist-Abweichungsanalyse** (.3) — Ampel-Status, Drill-Down
3. **Kostenstellen-Abschluss-Flow** (.4) — Perioden-Sperr-Mechanismus

---

## Budget-Statusmaschine

```
ENTWURF ──► FREIGEGEBEN ──► AKTIV ──► ABGESCHLOSSEN
    │
    └──► STORNIERT (aus ENTWURF oder FREIGEGEBEN)
```

- Freigabe: Freigabe-Operator Pflichtfeld
- Aktivierung: idempotent (bereits AKTIV → zurückgeben)
- Jeder Übergang → append-only `controlling_budget_status_log`

---

## Abweichungsanalyse Ampel-Schema

```
abweichung_pct = (ist_eur - plan_eur) / plan_eur * 100

|abweichung_pct| ≤  5% → GRÜN
|abweichung_pct| ≤ 15% → GELB
|abweichung_pct| >  15% → ROT
```

- Kein Planwert → ampel = "KEIN_PLAN"
- Drill-Down: Liste aller KST-Perioden-Paare mit Ampel

---

## Kostenstellen-Abschluss

```
OFFEN ──► IN_BEARBEITUNG ──► ABGESCHLOSSEN
```

- Abgeschlossene Perioden: Ist-Buchungen gesperrt (fail-closed)
- Idempotent via (kostenstelle_id, periode)
- Abschluss schreibt `abgeschlossen_am` Zeitstempel
