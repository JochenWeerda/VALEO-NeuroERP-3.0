---
title: Webhooks — eine Anbindung gehört einem Haus
type: reference
audience: [entwickler, agent, qa, betrieb, compliance]
owner: Claude Code
status: aktiv
last_reviewed: 2026-10-01
version: 1.0.0
description: Warum zwei Module unter /api/v1/webhooks hängen, wie beide den Mandanten verfehlten, warum das hinterlegte Geheimnis verworfen wurde, und warum keine neue Tabelle die Antwort war.
---

# Webhooks

## Der Befund in einem Satz

**Unter `/api/v1/webhooks` hängen zwei Module, und beide bestimmten das Haus
falsch** — das eine kannte es überhaupt nicht, das andere nahm es als
Abfrageparameter.

| Modul | Tabelle | wie es das Haus bestimmte |
|---|---|---|
| `webhook_system.py` | `domain_shared.webhooks` — **ohne Migration** | gar nicht: kein Import von `get_tenant_id` |
| `webhooks.py` | `domain_shared.webhook_registrations` — migriert, ORM | `?tenant_id=`, Rückfall `DEFAULT_TENANT_ID` |

## Was daraus folgte

**`webhook_system.py`:**

- Die Liste zeigte die Webhooks aller Häuser, **mit ihren Ziel-URLs**.
- Die laufende Nummer kam aus `MAX(nr) + 1` über die ganze Tabelle, war also
  hausübergreifend.
- `_trigger_webhook` wählte alle Webhooks eines Bereichs: Ein Ereignis aus Haus A
  wäre an die URL von Haus B gegangen. **Diese Funktion hat keinen Aufrufer** —
  der Abfluss war angelegt, nicht in Betrieb. Das ist der Unterschied zwischen
  einem Vorfall und einem Befund, und er gehört genannt.
- `DELETE /{nr}` war **unerreichbar**: `webhooks.py` ist unter demselben Prefix
  zuerst eingebunden und hat `DELETE /{webhook_id}`, also traf jede Abmeldung
  dort eine Kennung, die keine laufende Nummer ist.
- Als Prüfung der Ziel-URL genügte `https://`. Damit ließ sich die Anwendung als
  Bote in das eigene Netz oder an den Metadatendienst der Cloud schicken
  (`https://169.254.169.254/…`).

**`webhooks.py`:**

- Wer `?tenant_id=` setzte, las und schrieb die Anbindungen eines fremden
  Hauses. Ohne den Parameter traf es pauschal `DEFAULT_TENANT_ID`.
- `DELETE /{webhook_id}` hatte **keinen** Mandantenfilter: Die Kennung eines
  fremden Webhooks löschte dessen Anbindung.

**Beide:** Das Feld `secret` wurde seit immer entgegengenommen und **verworfen**.
Ohne hinterlegtes Geheimnis gibt es keine Signatur, und ein Empfänger kann nicht
unterscheiden, ob ein Aufruf von uns kommt oder von jemandem, der die URL kennt.

## Keine neue Tabelle

`scripts/check_schema_drift.py` nennt `domain_shared.webhooks` unter den Tabellen
ohne Migration. Der Reflex wäre, sie anzulegen — und er wäre falsch, zum zweiten
Mal in dieser Welle nach dem Kassenbericht: `domain_shared.webhook_registrations`
**existiert**, ist migriert, hat ein ORM-Modell, trägt `tenant_id` (mit
Fremdschlüssel auf `tenants`) und `secret`. Eine zweite Webhook-Tabelle wäre eine
zweite Wahrheit darüber, wohin wir Ereignisse melden.

`webhook_system.py` liest und schreibt jetzt dort. Die laufende Nummer ist keine
Spalte mehr, sondern die Stellung der Zeile **im eigenen Haus**
(`ROW_NUMBER() OVER (ORDER BY created_at, id)`).

## Was sich geändert hat

| vorher | jetzt |
|---|---|
| kein Mandant in `webhook_system.py` | `get_tenant_id` in allen vier Wegen |
| `MAX(nr) + 1` über alle Häuser | laufende Nummer je Haus, beginnt bei 1 |
| `DELETE /{nr}` unerreichbar | `DELETE /abmelden/{nr}`, mandantenrein |
| `?tenant_id=` bestimmte das Haus | der Kopf bestimmt es; ein abweichender Parameter wird protokolliert und ignoriert |
| `DELETE /{webhook_id}` ohne Filter | mit Filter — fremde Kennung ist 404 |
| `secret` verworfen | hinterlegt, nie ausgegeben, signiert jeden Aufruf (`X-Valeo-Signature: sha256=…` als HMAC-SHA256 über den gesendeten Rumpf) |
| `https://` als einzige Prüfung | `validate_outbound_http_target` wie in `webhooks.py` |
| Lesefehler → `[]` | Lesefehler → 503 |

Der Abfrageparameter `tenant_id` **bleibt** in der Schnittstelle, damit die
Spezifikation sich nicht ändert, wo Aufrufer ihn senden — er wird nur nicht mehr
befolgt. Ausgegeben wird statt des Geheimnisses das Feld `signiert`.

## Offen, und zwar bewusst

**Zwei Module, zwei Vokabulare.** `webhook_system.py` kennt `WIEGUNG_NEU`,
`KONTRAKT_NEU`, `SETTLEMENT_GEBUCHT` … ; `webhooks.py` kennt `auftrag`,
`bestellung`, `kunde` … Die Mengen sind **disjunkt**. Beide schreiben jetzt in
dieselbe Spalte `event_area`. Welches Vokabular gilt — oder wie die Abbildung
aussieht — ist eine fachliche Entscheidung und hier **nicht** getroffen. Dass
zwei Module unter einem Prefix hängen und sich Wege verdecken, gehört in
denselben Vorgang.

**Zustellversuche werden nicht gezählt.** `webhook_registrations` hat keine
Spalten für Fehlerzähler und letzte Auslösung. `fehler_count` und
`letzte_auslosung_am` stehen deshalb konstant auf `0` und `null`. Das ist
ehrlicher als die alte Tabelle, in der die Zähler standen, aber niemand sie las —
richtig wird es erst mit einem Zustellprotokoll (eigene Tabelle) oder zwei
zusätzlichen Spalten. Ein Zustellversuch ohne Nachweis ist für einen Betrieb
wenig wert; das gehört als eigener Vorgang entschieden.

**Die Route hat sich geändert** (`DELETE /{nr}` → `DELETE /abmelden/{nr}`), also
driftet die OpenAPI-Spezifikation. Der laufende `OPENAPI-DRIFT-REFRESH` hält
ausdrücklich fest, dass jeder spätere Router-Commit sie erneut regenerieren muss.

## Abnahme

18 Verträge in `tests/test_webhook_mandant_vertrag.py`:

| Gruppe | prüft |
|---|---|
| Eine Tabelle | die Registrierung landet in `webhook_registrations`; `domain_shared.webhooks` kommt in `app/`, `modules/` und `alembic/` in keiner Abfrage mehr vor |
| Liste | keine fremde Ziel-URL in der Antwort; Nummer beginnt in jedem Haus bei 1 |
| Geheimnis | wird hinterlegt, erscheint nie in einer Antwort, `signiert` steht dafür |
| Abfrageparameter | `?tenant_id=<fremd>` ändert weder Lesen noch Schreiben |
| Löschen | fremde Kennung ist 404 und die Zeile bleibt; `abmelden/{nr}` trifft die eigene; unbekannte Nummer löscht nichts |
| Auslöser | sendet nur an das eigene Haus; signiert genau den gesendeten Rumpf; ohne Geheimnis keine Signatur; **ohne Haus sendet er nichts** |
| Störung | Spalte kurzzeitig umbenannt → 503, nicht `[]` |
| Ziel-URL | `127.0.0.1`, `localhost` und `169.254.169.254` werden abgewiesen |

```bash
DATABASE_URL=postgresql://valeo_dev:…@127.0.0.1:5432/valeo_probe \
  python -m pytest tests/test_webhook_mandant_vertrag.py -q
```

**Ergebnis 2026-10-01:** 18 Verträge grün, dazu 49 vorhandene Tests
(`test_gs1_webhook_ruestliste.py`, `test_security_webhooks_vies.py`,
`test_security_outbound_policy.py`, `test_l3c_smoke.py`) grün. Zwei Tests in
`test_gs1_webhook_ruestliste.py` rufen die Endpunktfunktionen direkt und
positionell auf; sie wurden auf den neuen Mandantenparameter nachgezogen.

Geprüft wurde gegen die **vorhandene** gemeinsame Prüfstand-Datenbank, mit
eigenen Mandantenkennungen und ohne Zurücksetzen — nach
`test-database-resource-policy-20261001.md`.

Nebenbefund der Abnahme: `webhook_registrations.tenant_id` hat einen
Fremdschlüssel auf `tenants`. Die Testzeilen scheiterten zunächst daran — eine
echte Bedingung, die die gewachsene Entwicklungsdatenbank an anderen Stellen
verloren hat.
