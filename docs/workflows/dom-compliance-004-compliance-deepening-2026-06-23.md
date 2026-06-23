# DOM-COMPLIANCE-004 — Compliance-Domäne Vertiefung
\
2026-06-23 | Owner: Claude Code | Slice: DOM-COMPLIANCE-004

## Überblick

Dieser Slice hebt drei Compliance-Kernprozesse auf volle 004-Tiefe:

1. **PCN-Meldung-Lifecycle** (.2) — Pflanzenschutzrechtliche Änderungsmeldungen von DRAFT bis CLOSED
2. **VVVO-Prüfung + Sachkunde-Ablauf** (.3) — Behördliche Fälligkeitsüberwachung
3. **Artikel-Sperre Audit-Trail** (.4) — Unveränderlicher Nachweis für Sperr/Freigabe-Aktionen

---

## PCN-Meldung-Statusmaschine

```
DRAFT ──► VALIDATED ──► SUBMITTED ──► CLOSED
  │
  └──► WITHDRAWN (aus DRAFT oder VALIDATED)
```

- **DRAFT**: Meldung angelegt, noch nicht geprüft
- **VALIDATED**: Inhalt geprüft, bereit zur Einreichung
- **SUBMITTED**: An Behörde (BVL) eingereicht
- **CLOSED**: Von Behörde bestätigt / abgeschlossen
- **WITHDRAWN**: Zurückgezogen (irreversibel)

Jeder Übergang wird in `compliance_pcn_status_log` protokolliert.

---

## VVVO-Prüfzyklus

- Betrieb besitzt VVVO-Zulassungsnummer
- Jährliche Prüfpflicht: `naechste_pruefung_am` berechnet aus letzter Prüfung + 365 Tage
- Service listet alle Betriebe, deren Prüfung innerhalb der nächsten `days` Tage fällig ist
- Sachkunde-Ablauf: Zertifikat besitzt `ablauf_datum`, Alarm-Schwelle 30 Tage

---

## Artikel-Sperre Audit-Trail

- Jede Aktion (SPERRE, FREIGABE, STORNO) erzeugt einen neuen Audit-Eintrag
- Append-only: keine Updates, kein Delete
- Sperre-Guard: Artikel, der bereits gesperrt ist, kann nicht erneut gesperrt werden (idempotent-check)
- Freigabe-Guard: nur gesperrte Artikel können freigegeben werden
- Vollständige Rückverfolgung: `artikel_id + tenant_id` → alle Aktionen in chronologischer Reihenfolge
