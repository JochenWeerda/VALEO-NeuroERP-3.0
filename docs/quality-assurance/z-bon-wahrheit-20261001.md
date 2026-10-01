---
title: Kassenbericht — ein Z-Bon über 0,00 Euro ist keine Störungsmeldung
type: reference
audience: [entwickler, agent, qa, betrieb, compliance]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-01
version: 1.0.0
description: Warum X- und Z-Bericht ein Schema lasen, in dem die Kassentabelle nicht liegt, warum sie jeden Fehler als umsatzlosen abgeschlossenen Tag meldeten, und warum hier keine Migration die Antwort war.
---

# Kassenbericht

## Der Befund in einem Satz

**`pos_payments.x_report` und `z_report` lasen `domain_pos.pos_transactions` —
eine Tabelle, die in diesem Schema nicht liegt.** Jede Abfrage scheiterte, und
das `except` meldete:

| Bericht | Antwort bei Fehler |
|---|---|
| X | `total_eur: 0.0`, keine Zahlart |
| Z | `total_eur: 0.0` **und `closed: true`** |

Ein Tagesabschluss, der einen umsatzlosen, abgeschlossenen Kassentag behauptet,
ist keine leere Lage, sondern eine Falschaussage. Bei einer Kasse ist „0,00 €"
eine Aussage über **den Tag**, nicht über die Datenbank — und sie ist nach GoBD
und KassenSichV aufbewahrungspflichtig.

## Hier war keine Migration die Antwort

`scripts/check_schema_drift.py` nennt `domain_pos.pos_transactions` unter den
Tabellen, die der Code erwähnt und die es im Migrationsstand nicht gibt. Der
naheliegende Reflex wäre, sie anzulegen. Das wäre falsch gewesen: Der
Kassenumsatz **existiert**, nur an einer anderen Stelle.

| vorhanden | Inhalt |
|---|---|
| `domain_docflow.pos_fiscal_transactions` | der Kassenvorgang: `business_date`, `gross_total`, `payment_breakdown`, `state`, Signatur |
| `domain_erp.pos_transactions` | ein Rumpf: `id`, `tenant_id`, `source`, zwei Zeitstempel — **kein Betrag, keine Zahlart** |
| `domain_pos.pos_transactions` | gibt es nicht |

Auch das richtige Schema hätte also nicht genügt: `domain_erp.pos_transactions`
trägt keinen Betrag. Die Antwort war der dritte Weg aus
`schema-drift-2026-09-30.md` — **den Verweis korrigieren**, nicht die Tabelle
nachbauen. Eine neue `domain_pos.pos_transactions` hätte eine zweite, leere
Wahrheit über den Kassenumsatz geschaffen.

## Was sich geändert hat

**Der Umsatz kommt aus dem Bestand, der ihn trägt.** Beide Berichte summieren
`domain_docflow.pos_fiscal_transactions` je Mandant und Geschäftstag.

**Alle Zahlarten, nicht nur zwei.** Die Aufschlüsselung entsteht aus
`jsonb_each_text(payment_breakdown)`. Die vorhandene `daily_summary`
(`app/services/fiscalization/service.py`) kennt nur `BAR` und `KARTE` fest
verdrahtet — eine SEPA- oder Gutschein-Zahlung steckt dort im Bruttoumsatz, aber
in keinem der beiden Töpfe. Der Bericht schlüsselt jetzt auf, was tatsächlich
gezahlt wurde.

**Unfertige Vorgänge werden ausgewiesen.** `unfinished_count` zählt, was nicht
auf `FINISHED` steht. Ein Z-Bon über unfertige Vorgänge ist kein Abschluss; wer
ihn zieht, soll das sehen.

**`closed` kommt aus dem Tagesabschluss.** Vorher war es eine Zuweisung
(`"closed": True`). Jetzt liest der Bericht `domain_pos.pos_tagesabschluesse` und
ist nur dann geschlossen, wenn dort `ABGESCHLOSSEN` steht — das Ende der
Zustandsmaschine aus `pos_tagesabschluss_service` (OFFEN → IN_ABSCHLUSS →
Z_BON_ERSTELLT → TSE_SIGNIERT → DSFINVK_EXPORTIERT → ABGESCHLOSSEN).
`closing_status` gibt den Stand zusätzlich im Klartext.

**Eine Störung ist ein 503.** Nicht 0,00 €.

## Zwei Tagesabschlüsse — eine offene Frage an den POS-Owner

Im System stehen zwei Dinge, die „Tagesabschluss" heißen:

1. **Der echte:** `pos_tagesabschluss_service` mit Zustandsmaschine,
   TSE-Signatur, Z-Bon-Nummer und DSFinV-K-Export.
2. **Dieser Bericht:** eine Aggregation, die nichts abschließt.

Dieser Slice macht den zweiten ehrlich — er zeigt jetzt an, was der erste
entschieden hat, statt es zu behaupten. Ob ein zweiter Weg mit dem Namen
„Z-Report" überhaupt bleiben soll, oder ob die Maske direkt am
Tagesabschluss hängen müsste, ist eine fachliche Entscheidung des POS-Owners und
in diesem Slice **nicht** getroffen.

## Abnahme

13 Verträge in `tests/test_z_bon_wahrheit_vertrag.py`:

| Gruppe | prüft |
|---|---|
| Summen | Z-Bericht summiert vier echte Vorgänge auf 479,00 € und weist den einen unfertigen aus |
| Zahlarten | BAR 169,00 (aus drei Vorgängen, einer geteilt), KARTE 250,00, **SEPA 60,00** |
| Laufender Tag | X-Bericht zeigt den heutigen Tag |
| Mandant | der Umsatz des fremden Hauses am selben Tag bleibt draußen |
| `closed` | ohne Abschluss `false`; über alle fünf Stände der Zustandsmaschine nur bei `ABGESCHLOSSEN` `true` |
| Störung | die Spalte, über die summiert wird, wird kurzzeitig umbenannt: 503 für **beide** Berichte, und keine `0.0` in der Antwort |
| Verweis | `domain_pos.pos_transactions` kommt in `app/` und `modules/` in keiner Abfrage mehr vor |

```bash
export TEST_DATABASE_URL=postgresql://valeo_dev:…@127.0.0.1:5432/valeo_probe
python scripts/pruefstand_db.py
DATABASE_URL="$TEST_DATABASE_URL" python -m pytest tests/test_z_bon_wahrheit_vertrag.py -q
```

**Ergebnis 2026-10-01:** 13 Verträge grün gegen den frischen Stand, dazu 36
vorhandene POS-Tests (Buchungsquelle, Fiskaldokumente, Fiskalisierungsanbieter,
Sicherheitsvertrag, Zahlarten) grün.

Nebenbefund der Abnahme: Die Testzeilen scheiterten zunächst an `terminal_id`,
`cash_register_id`, `client_id`, `started_at` und `provider_response` — alle
`NOT NULL` auf einer **frischen** Datenbank. Genau der Grund, aus dem der
Prüfstand frisch ist.

## Tabellen-Ratsche: der Stand ist rot, und zwar nicht hierdurch

Dieser Slice entfernt einen Verweis ins Leere an einem lebenden Weg; gemessen
gegen `valeo_probe` sinkt die Zahl von 26 auf 25. **Die Schwelle steht bei 24 und
bleibt dort** — sie wurde in diesem Slice bewusst *nicht* angehoben.

Der Überhang kommt aus Commit `aede5e1cc` („fix(crm): Kundenakte liest
Partnerstamm, Posten und Register"): `crm_360.py` liest dort
`domain_crm.contacts` und `domain_crm.crm_customers`. Beide stehen auf der Liste
der 76 Tabellen ohne Migration, und beide lagen vorher an einem *ruhenden* Weg.
Die Kundenakte liest sie jetzt an einem lebenden — auf einer frischen
Installation also ins Leere.

**Handshake an den CRM-Owner:** Entweder die beiden Tabellen bekommen eine
Migration, oder die Akte liest den Bestand, der sie trägt. Eine angehobene
Schwelle wäre die dritte, falsche Möglichkeit. Vorgewarnt war der Stand im
Vorgänger-Slice (`lastschrift-mandant-20260930.md`), solange die Dateien noch
nicht eingecheckt waren.
