# DOM-FINANCE-004 — Finance-Domäne Vertiefung
\
2026-06-23 | Owner: Claude Code | Slice: DOM-FINANCE-004

## Überblick

Drei Finance-Kernprozesse auf volle 004-Tiefe:

1. **SEPA-Zahlungsträger** (.2) — Lastschrift-Mandate + Batch-Export
2. **Ratenzahlungsplan-Lifecycle** (.3) — Plan anlegen, Raten buchen, Abschluss
3. **Mahnstufen-Eskalation-Trail** (.4) — Stufe 1→2→3→INKASSO, append-only

---

## SEPA-Flow

```
Mandat AKTIV ──► Lastschrift-Batch (XML) ──► Einzug
   │
   └──► WIDERRUFEN | ABGELAUFEN
```

- Mandat-Typ: CORE (Verbraucher) oder B2B (Geschäftskunde)
- Batch-Export: vereinfachter PAIN.008 XML pro Fälligkeitstag
- Widerruf: setzt `widerruf_am`, Status → WIDERRUFEN

---

## Ratenzahlungsplan-Lifecycle

```
AKTIV → Rate 1 bezahlt → Rate 2 bezahlt → ... → ABGESCHLOSSEN
  │
  └──► STORNIERT
```

- Gesamtbetrag wird auf N Raten aufgeteilt
- Restbetrag reduziert sich bei jeder Ratenbuchung
- `restbetrag_eur == 0` → Status automatisch ABGESCHLOSSEN

---

## Mahnstufen-Eskalation

| Stufe | Bezeichnung | Bearbeitungsgebühr |
|-------|-------------|-------------------|
| 1 | Zahlungserinnerung | 0 EUR |
| 2 | Mahnung | 5 EUR |
| 3 | Letzte Mahnung | 15 EUR |
| INKASSO | Inkasso-Übergabe | 40 EUR |

- Eskalation nur vorwärts (1→2→3→INKASSO), kein Rückschritt
- Jede Stufe schreibt append-only Audit-Eintrag
- Doppel-Eskalation auf gleiche Stufe: idempotent (kein neuer Eintrag)
