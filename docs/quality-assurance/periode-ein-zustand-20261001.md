---
title: Buchungsperiode — ein Zustand, nicht drei Vokabulare
type: reference
audience: [entwickler, agent, qa, betrieb, compliance]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-01
version: 1.0.0
description: Warum die dokumentierte Wiedereröffnung einer Periode nicht wirkte, warum ein Lesefehler die Periodensperre ganz abschaltete, und warum ein gescheiterter Abschluss Erfolg meldete.
---

# Buchungsperiode

## Der Befund in einem Satz

**In `public.finance_accounting_periods.status` standen drei Vokabulare**, und
sieben Buchungswege verglichen jeder für sich `status != "OPEN"`.

| schreibt | Wert |
|---|---|
| Verwaltungsmaske (`accounting_periods.py`) | `OPEN` / `CLOSED` / `ADJUSTING` |
| `close_period` | `closed` |
| `reopen_period` | `offen` |

## Drei Folgen, alle nachgewiesen

**1. Die Wiedereröffnung wirkte nicht.** `reopen_period` verlangt einen Grund,
weist eine Wiedereröffnung ohne Grund ab und schreibt ihn in `metadata` — alles
richtig. Dann setzte es `offen`. Die sieben Wächter lasen `offen != "OPEN"` und
**sperrten weiter**. Eine Periode, die mit Begründung wiedereröffnet wurde, war
danach genauso gesperrt wie vorher. Der GoBD-Prozess existierte auf dem Papier
und hatte keine Wirkung.

**2. `ADJUSTING` sperrte wie `CLOSED`.** Die Maske ließ den Zustand setzen; er
bedeutete dann nichts — eine Periode, die „nur noch für Abschlussbuchungen offen"
heißt und in die niemand buchen kann.

**3. Ein Lesefehler schaltete die Sperre ab.** `check_period_open` im
`FinanceTransactionService` endete mit:

```python
except Exception:
    pass  # table may not exist in test/dev — allow through
```

War die Periodentabelle nicht lesbar, **entfiel die Sperre ganz** — still. Das
ist die Unveränderbarkeit nach GoBD (Rz. 107 ff.) genau verkehrt herum: Wer nicht
feststellen kann, ob eine Periode offen ist, darf nicht buchen lassen.

## Und ein vierter Fund: ein Abschluss, der Erfolg meldet

`POST /finance/closing/lock` und `POST /finance/closing/run` fingen jeden
unerwarteten Fehler und riefen `_legacy_close_accounting_period` auf:

```python
UPDATE domain_erp.accounting_periods SET status = 'closed', closed_at = NOW() …
```

Dieses Schema gibt es in **keinem** Migrationsstand. Auf einer Installation, auf
der die Tabelle doch liegt, trifft das `UPDATE` null Zeilen, `commit()` gelingt —
und der Endpunkt antwortet `success: true, "Periode gesperrt."` **ohne Sperre**.
`/closing/run` behauptete zusätzlich einen vollständigen Abschluss, nachdem es
nur einen Status zu setzen versucht hatte: **ohne Salden und ohne
Abschlussbuchung**. Ein gemeldeter Abschluss ohne Abschlussbuchung verfehlt die
Vollständigkeit (GoBD Rz. 36 ff.).

Der Rückfall ist entfernt. Ein gescheiterter Abschluss scheitert.

## Was jetzt gilt

**Ein Wörterbuch, an einer Stelle:** `app/core/finance_periods.py`.

| Zustand | Bedeutung | buchen |
|---|---|---|
| `OPEN` | offen | ja |
| `ADJUSTING` | nur noch Abschlussbuchungen | **ja** |
| `CLOSED` | abgeschlossen | nein |

**Entscheidung zu `ADJUSTING`:** Der Zustand erlaubt buchen. Sonst wäre er
gleichbedeutend mit `CLOSED` und damit wertlos; wer eine Periode gegen jede
Buchung sperren will, schließt sie. Dass `ADJUSTING` fachlich nur
*Abschluss*buchungen erlauben soll, ist eine Einschränkung auf der Belegart und
gehört an die Buchungsart, nicht an die Periodensperre — benannte Lücke, keine
stille Umdeutung.

**Unbekanntes sperrt.** `sperrt("IRGENDWAS")` ist wahr. Eine Periode, deren
Zustand niemand benennen kann, ist kein Freibrief zum Buchen. **Keine Zeile
heißt offen:** Perioden entstehen beim ersten Abschluss, und eine nie angelegte
Periode ist nicht abgeschlossen.

**Die Datenbank hält das Wörterbuch.** `periode_statuswoerterbuch_20261001`
normalisiert `closed`/`geschlossen`/`gesperrt` → `CLOSED`, `offen`/`open` →
`OPEN`, und legt eine Prüfbedingung auf die drei Werte. Was danach noch nicht im
Wörterbuch steht, lässt die Migration **abbrechen** statt es zu `OPEN` zu
machen. Am 01.10.2026 war die Tabelle in beiden Datenbanken leer — die
Normalisierung ist heute ein Nullvorgang, die Prüfbedingung wirkt ab der ersten
Periode.

**Sieben Wächter, eine Prüfung.** `ap_invoices`, `bulk_journal_import`,
`finance_invoices`, `journal_entries`, `finance_actions`,
`ap_invoice_kernel_posting` und `finance_transaction_service` rufen
`finance_periods.gesperrter_zustand()`. Ein Vertrag sucht nach einem achten
Eigenvergleich.

## Nicht angefasst

`domain_finance.period_closure` ist leer und wird von keinem Modul genannt — ihre
Form (`fiscal_year`, `fiscal_period`, `dim_cost_center`, `dim_profit_center`,
`dim_project_tag`, `dim_region`) deutet aber auf eine **Controlling-Dimension**,
nicht auf eine Fibu-Periodensperre. Eine Tabelle stillzulegen, deren Zweck man
nur erraten kann, wäre derselbe Fehler in der anderen Richtung. Sie gehört dem
Controlling-Owner. Ebenso `domain_shared.fibu_perioden` — die wird von
`fibu_geschaeftsjahre.py` benutzt und ist die Geschäftsjahresverwaltung, nicht
die Buchungssperre.

## Abnahme

26 Verträge in `tests/test_periode_ein_zustand_vertrag.py`:

| Gruppe | prüft |
|---|---|
| Wörterbuch | die drei Zustände; `sperrt` über neun Eingaben, inklusive der Altschreibweisen und „unbekannt sperrt" |
| Einzige Stelle | kein Modul außer `finance_periods.py` vergleicht noch selbst `!= "OPEN"` |
| Rückfall | `_legacy_close_accounting_period` ist weg; kein `UPDATE domain_erp.accounting_periods` |
| Fail closed | `allow through` ist weg; ein nicht feststellbarer Zustand weist ab |
| Datenbank | `offen` wird von der Prüfbedingung abgewiesen; `gesperrter_zustand` liest die Periode über alle drei Zustände |
| Abschluss | schließen schreibt `CLOSED`; zweiter Abschluss abgewiesen; **Wiedereröffnung setzt `OPEN`, löscht `closed_at` und behält den Grund im Protokoll** |
| Buchungsweg | `CLOSED` weist ab, `OPEN` und `ADJUSTING` lassen durch; bei umbenannter Statusspalte wird abgewiesen, nicht durchgelassen |

```bash
DATABASE_URL=postgresql://valeo_dev:…@127.0.0.1:5432/valeo_probe \
  python -m pytest tests/test_periode_ein_zustand_vertrag.py -q
```

**Ergebnis 2026-10-01:** 96 Tests grün — 26 neue Verträge plus
`test_finance_actions.py`, `test_finance_closing_service.py`,
`test_finance_transaction_service.py`, `test_security_accounting_periods.py`,
`test_journal_entries_api.py`. Alle Ratschen grün; Tabellenverweise 17 gegen 17.

**Ein bestehender Test bewies den Fehler.**
`test_closing_calculate_lock_run_and_approve_paths` endete mit
`assert "2026-04" in db.closed_period_updates`, und `closed_period_updates`
wurde im Testdoppel aus dem `UPDATE domain_erp.accounting_periods` gefüllt — also
aus dem Rückfall. Der Test konnte nur grün sein, weil die Sperre nichts
hinterließ: Erst sperren, dann auf derselben Periode abschließen geht sonst nicht.
Jetzt sperrt er eine Periode, prüft die Festschreibung, lässt den **zweiten**
Abschluss derselben Periode mit 422 abweisen und schließt eine andere Periode ab.
