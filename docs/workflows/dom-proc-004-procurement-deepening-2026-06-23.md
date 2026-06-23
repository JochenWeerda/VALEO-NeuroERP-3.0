# DOM-PROC-004 — Procurement-Domäne Vertiefung
\
2026-06-23 | Owner: Claude Code | Slice: DOM-PROC-004

## Überblick

Drei Procurement-Kernprozesse auf volle 004-Tiefe:

1. **Bestellung-Lifecycle** (.2) — Statusmaschine mit Freigabe-Workflow
2. **Wareneingangs-Buchung + QS** (.3) — WE buchen mit Qualitätsprüfungsstatus
3. **Rechnungsprüfung + ERS** (.4) — 3-Way-Match, Auto-Freigabe, Sperrung

---

## Bestellungs-Statusmaschine

```
DRAFT ──► FREIGEGEBEN ──► VERSANDT ──► WE_ERHALTEN
  │
  └──► STORNIERT (aus DRAFT oder FREIGEGEBEN)
```

- Freigabe: Freigabe-Operator Pflichtfeld
- WE_ERHALTEN: Wareneingang gebucht
- Jeder Übergang → append-only `proc_bestellung_status_log`

---

## Wareneingangs-Buchung QS-Flow

```
WE buchen → QS_STATUS: AUSSTEHEND → BESTANDEN | GESPERRT
```

- GESPERRT: Ware kann nicht ins Lager transferiert werden (fail-closed)
- Idempotent: Gleiche Bestellung + Menge → bestehender WE zurückgeben
- WE-Buchung nur wenn Bestellung = VERSANDT

---

## Rechnungsprüfung 3-Way-Match

```
abweichung_pct = |rechnungs_betrag - (bestell_preis × we_menge)| / (bestell_preis × we_menge) × 100

abweichung_pct ≤ 3.0% → FREIGEGEBEN (auto)
abweichung_pct >  3.0% → GESPERRT → manuelle Freigabe: FREIGEGEBEN | ABGELEHNT
```

- Standardschwelle: 3,0 %
- Idempotent via (bestellung_id, rechnungs_nr)
