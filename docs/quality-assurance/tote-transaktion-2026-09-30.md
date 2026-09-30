---
title: Tote Transaktion — wo ein except ein Scheinergebnis erzeugt
type: reference
audience: [entwickler, agent, qa]
owner: Claude Code
status: aktiv
last_reviewed: 2026-09-30
version: 1.0.0
description: Das Muster, die systematische Suche, die 78 Fundstellen mit Einordnung, und was davon behoben ist.
---

# Tote Transaktion

## Das Muster

```python
try:
    db.execute(...)          # scheitert, die Transaktion ist ab hier tot
except Exception as fehler:
    log.append({"error": str(fehler)})   # gefangen, aber nicht zurückgerollt

db.execute(...)              # scheitert mit InFailedSqlTransaction
db.commit()                  # scheitert ebenfalls
```

Postgres bricht bei einem Fehler die **ganze** Transaktion ab. Ein `except`
fängt die Ausnahme, aber ohne `rollback()` oder Savepoint (`begin_nested()`)
ist jede weitere Anweisung verloren. Und weil die Fehlermeldung im Protokoll
landet statt beim Aufrufer, **sieht das Ergebnis aus wie ein Ergebnis**.

## Der Anlass

Am 29.09.2026 lief der Löschweg nach Art. 17 DSGVO komplett ins Leere und
meldete `503 Failed to update erasure request`. Eine Nebentabelle
(`domain_crm.crm_customers`) fehlt auf einer frischen Installation; die
Namensabfrage darauf brach die Transaktion ab. Das `except` protokollierte den
Fehler, aber jede weitere Anweisung — darunter das abschließende `UPDATE` des
Antrags — scheiterte danach. Eine Rechtspflicht blieb unerfüllt, und der
Aufrufer erfuhr nicht, woran es lag.

## Die Suche

`scripts/check_dead_transactions.py` liest den AST, nicht den Text. Als Fund
gilt ein `try`, das eine Datenbankanweisung ausführt, dessen `except`-Zweig
weder `rollback()` noch `raise` noch eine nutzersichtbare Fehlerantwort
enthält — **und** nach dem noch weitergearbeitet wird:

- das `try` steht in einer Schleife (der nächste Durchlauf fällt mit), oder
- nach dem `try` folgt in derselben Funktion eine weitere Anweisung.

Ohne diese zweite Bedingung meldet die Suche **351** Stellen. Die meisten
richten nichts an: Endet die Anfrage nach dem `except`, wird die Sitzung
geschlossen und niemand sieht ein Scheinergebnis. Mit ihr bleiben **78**.

Zwei Feinheiten, die beide aus Fehlversuchen stammen:

1. **Der Savepoint liegt oft *innerhalb* des `try`.** Genau so sieht der
   richtige Weg aus. Die erste Fassung des Skripts prüfte nur die
   Verschachtelung *um* das `try` und meldete damit den Löschweg, der einen Tag
   vorher behoben worden war. `_db_aufruf_ohne_savepoint` steigt nicht in
   Savepoint-Blöcke hinab.
2. **`ast.walk` läuft über Knoten ohne Zeilennummer** (`ast.Store` und
   Verwandte). Die werden übergangen, nicht geraten.

`tests/test_check_dead_transactions.py` hält beide Unterscheidungen fest, ohne
Datenbank: zehn Fälle, je einer pro Unterscheidung.

## Was behoben ist

**Der Art.-17-Pfad** (`app/api/v1/endpoints/compliance_dsgvo.py`):

- Savepoint je Anweisung in `_namen_des_betroffenen` und `_anonymize_subject`.
  Eine fehlende Nebentabelle reißt den Lauf nicht mehr mit.
- Eine Tabelle, die es **nicht gibt**, gilt als „enthält keine Daten des
  Betroffenen" und wird als `table_missing` protokolliert — nicht als Fehler.
  Sonst bliebe jeder Löschantrag auf einer Installation ohne diese
  Nebentabellen dauerhaft unerledigt. Jede andere Störung bleibt ein Fehler.
- **Die Löschung ist jetzt auditiert.** Nach dem Commit schreibt der Endpunkt
  einen Eintrag in `domain_shared.audit_logs` — hashverkettet
  (`prev_hash`/`hash`), mit `user_id` des Handelnden, dem Betroffenen und dem
  vollständigen Löschprotokoll. Die Antragszeile sagt *was* gelöscht wurde; sie
  sagte nicht, *wer* gehandelt hat, und eine spätere Verarbeitung könnte sie
  überschreiben.
- Scheitert der Auditeintrag, steht das als `audit_fehler` in der Antwort. Die
  Löschung ist dann vollzogen und **nicht** bezeugt — eine Lage, die der
  Betrieb erfahren muss, statt sie im Protokoll zu verlieren.

Nachweis: `tests/test_tote_transaktion_vertrag.py`, fünf Verträge gegen den
frischen Prüfstand. Der Kernfall löst die Datenbank-Ausnahme **echt** aus (eine
`CHECK`-Bedingung, die den Anonymisierungsnamen verbietet) und prüft **genau
einen** Statuscode: 422, nicht 503 und nicht 200. Er prüft außerdem, dass die
Schritte *nach* dem gescheiterten gelaufen sind — der direkte Nachweis, dass
die Transaktion nicht tot war.

## Die Fundliste — 78 Stellen, nach Nutzerwirkung geordnet

Die Ratsche in `scripts/check_dead_transactions.py` steht auf **78** und läuft
im Quality Gate, bewusst **vor** der Pagination-Prüfung: Der Job bricht beim
ersten roten Schritt ab, und die Pagination-Schwelle ist seit dem 27.05. nicht
erfüllbar. Hinter ihr würde dieser Wächter nie laufen.

### Buchung und Zahlung (8) — die schwersten

| Stelle | Funktion |
|---|---|
| `payment_runs.py:799` | `execute_payment_run` |
| `ap_invoice_kernel_posting.py:222` | `post_ap_invoice_kernel_sync` |
| `erechnung_import.py:225` | `buchen` |
| `zinsabrechnung.py:249` | `buche_zinsabrechnung` |
| `op_skonto_auszifferung.py:198` | `create_auszifferung` |
| `credit_debit_memos.py:485` | `settle_credit_memo` |
| `payment_matching.py:214` | `import_payments_csv` |
| `closing_checklists.py:857` | `get_closing_cockpit_summary` |

**`execute_payment_run` im Einzelnen**, weil es Geld bewegt und weil die Stelle
zeigt, wie der Schaden entsteht: In der Schleife über die Zahlungen steht

```python
except Exception as e:
    logger.warning(f"Could not settle open item {payment.get('op_id')}: {e}")
```

Die Absicht ist erkennbar: *diesen* Posten überspringen, mit den übrigen
weitermachen. Die Absicht hält nicht. Scheitert das Ausziffern eines Postens in
der Datenbank, ist die Transaktion tot; jedes weitere Ausziffern in der
Schleife scheitert ebenso, und das `db.commit()` danach auch. Der äußere
`except`-Block rollt dann alles zurück und liefert 500. Es gibt also kein
„einen überspringen" — es gibt nur ganz oder gar nicht, und niemand erfährt,
welcher Posten der Auslöser war. Zwei Savepoints (einer je Posten, einer um die
AP-Rechnungsfortschreibung) stellen die Absicht wieder her.

### Löschung (1)

`agrar_feldbuch.py:577` — `bulk_delete_massnahmen`. In einer Schleife; eine
Maßnahme, die nicht gelöscht werden kann, verhindert die Löschung aller
folgenden.

### Freigabe (1)

`sales_blanket_orders.py:304` — `create_release`.

### Anlage und Import (9)

`bank_statement_import.py:505` und `:522`, `customers.py:452`,
`liquidity_planning.py:244`, `logistics_freight.py:434`,
`psm_proplanta.py:357`, `inventory_compat_service.py:443`, `:473`, `:503`.

Bei Importen ist das Muster besonders tückisch: Der Zähler „X von Y
importiert" zählt Schleifendurchläufe, nicht erfolgreiche Schreibvorgänge.
Nach dem ersten Datenbankfehler ist jeder weitere Durchlauf verloren, und die
Meldung sagt trotzdem Y.

### Lesen und Sonstiges (59)

Ohne unmittelbare Datenwirkung. Die vollständige Liste:
`python scripts/check_dead_transactions.py --liste` beziehungsweise
`--json` für die maschinenlesbare Form.

## Offen — gehört anderen

Die 19 mutierenden Stellen außer dem Art.-17-Pfad sind **nicht** behoben, und
zwar bewusst. Jede braucht nach der Hausregel einen HTTP-Vertragstest, der die
Datenbank-Ausnahme echt auslöst, und liegt in einer Fachdomäne mit eigenem
Owner: Finanzen, Agrar, Verkauf, Lager, Logistik. Ein Savepoint ist schnell
gesetzt; die Frage, *was* nach einem Fehlschlag gelten soll — Posten
überspringen, Import abbrechen, Teilergebnis melden —, ist eine fachliche und
gehört dem Owner.

Der Wächter verhindert ab jetzt, dass neue Stellen dazukommen.

## Für den nächsten Fix

Das Muster, das die Absicht trägt:

```python
for posten in posten_liste:
    try:
        with db.begin_nested():          # Savepoint je Posten
            db.execute(...)
        protokoll.append({"posten": posten, "stand": "ausgeziffert"})
    except Exception as fehler:          # noqa: BLE001
        protokoll.append({"posten": posten, "fehler": str(fehler)})
db.commit()
```

Und die Regel dahinter: **Ein Protokolleintrag ist keine Fehlerbehandlung.**
Entweder die Transaktion wird aufgeräumt (Savepoint oder `rollback`), oder der
Fehler geht an den Aufrufer. Alles andere erzeugt eine Zahl, die keiner prüfen
kann.
