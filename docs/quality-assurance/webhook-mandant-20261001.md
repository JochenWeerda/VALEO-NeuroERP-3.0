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

## Die zwei offenen Fragen sind entschieden

### Ein Vokabular, eine Implementierung

Es gab zwei Module unter einem Prefix, mit **disjunkten** Bereichslisten:
`webhook_system.py` kannte Ereignisse (`WIEGUNG_NEU`, `KONTRAKT_NEU`, …),
`webhooks.py` kannte Objekte (`auftrag`, `bestellung`, `kunde`, …). Das sind zwei
verschiedene Arten von Namen, und keine der beiden Listen deckt die andere ab.

**Entschieden:** Gezeichnet wird ein **Ereignis**, nicht ein Objekt — ein
Fremdsystem will wissen, *dass etwas passiert ist*, nicht *dass ein Objekt
existiert*. Das kanonische Vokabular steht in
`app/services/webhook_service.py` (`BEREICHE`) und ist die **Vereinigung** beider
alten Listen in einer Schreibweise: die elf Ereignisse aus `webhook_system` plus
je ein Ereignis für die Objekte, die nur `webhooks.py` anbot (`AUFTRAG_NEU`,
`ARTIKEL_GEAENDERT`, `LAGERBEWEGUNG_GEBUCHT`, `PICKLISTE_ERSTELLT`,
`NVE_ERSTELLT`, `STAMMDATEN_GEAENDERT`).

Die alten Objektnamen bleiben als **Alias** gültig (`ALIASSE`) und werden auf das
zugehörige Ereignis abgebildet; gespeichert wird immer der kanonische Name.
Niemand verliert eine Wahlmöglichkeit, bestehende Aufrufer brechen nicht, und es
gibt nur **eine** Form in der Tabelle.

**Und nur eine Implementierung:** `app/services/webhook_service.py` ist die
einzige Stelle, die die Anbindungen anfasst — Tabelle, Mandant, Vokabular,
Signatur, Zustellprotokoll. Beide Router sind dünn und rufen dorthin. Eine
zweite, abweichende Fassung kann nicht mehr entstehen; ein Vertrag prüft, dass
beide Wege dieselbe Anbindung sehen.

Die **zwei URL-Formen** bleiben (`GET /webhooks` liefert die flache Liste,
`GET /webhooks/` die paginierte), weil Aufrufer auf beiden hängen und das Entfernen
einer Route ein Bruch wäre, der keinem Anwender hilft. Sie sind jetzt zwei Sichten
auf denselben Bestand statt zwei Bestände.

**Nicht verdrahtet bleibt das Senden selbst:** `trigger` hat außerhalb der Tests
keinen Aufrufer, weil kein Fachdienst Webhook-Ereignisse meldet. Das ist der
nächste Schritt und ein eigener Vorgang — er gehört an die Stelle, an der die
Ereignisse entstehen (Outbox), nicht in die Webhook-Verwaltung.

### Ein Zustellversuch bekommt einen Nachweis

`fehler_count` und `letzte_auslosung_am` waren Behauptungen: Die alte, nie
migrierte Tabelle hatte Zähler, die niemand las, und
`webhook_registrations` hat keine. Ein Zähler sagt außerdem nicht, **was**
schiefging — und das ist die Frage, die bei einer nicht angekommenen Meldung
gestellt wird.

**Entschieden:** ein Protokoll statt zweier Zähler. Die Migration
`webhook_zustellprotokoll_20261001` legt `domain_shared.webhook_deliveries` an —
je Zustellversuch eine Zeile mit Zeitpunkt, Erfolg, Statuscode, Dauer, Fehlertext
und der Angabe, ob signiert gesendet wurde. Die beiden ausgegebenen Felder werden
daraus **abgeleitet** und sind damit belegt. `GET /webhooks/{id}/zustellversuche`
zeigt die letzten Versuche; die Maske öffnet sie über den Zeitpunkt des letzten
Versuchs.

`ON DELETE CASCADE`: Wird eine Anbindung abgemeldet, verliert ihr Protokoll seinen
Bezug. Es ist Betriebsnachweis einer Anbindung, keine aufbewahrungspflichtige
Buchung — ein Vertrag hält das fest.

Scheitert das Protokoll selbst, wird der auslösende Vorgang **nicht**
mitgerissen: Er ist die Buchung, der Webhook ist der Bote.

## Nebenbefund: die Maske war auf eine andere Antwort gebaut

`packages/frontend-web/src/pages/admin/webhooks.tsx` erwartete `name`,
`events[]`, `aktiv` und `last_triggered` — **vier Felder, die der Endpunkt nie
geliefert hat.** Sichtbar wurde das nie, weil die Liste immer leer war: Die
Tabelle, aus der gelesen wurde, legte keine Migration an, und ein Lesefehler kam
als `[]` zurück. Beim ersten echten Webhook wäre `w.name.toLowerCase()` in der
Suche gelaufen — die Maske hätte in dem Moment aufgehört zu funktionieren, in dem
sie etwas anzuzeigen gehabt hätte.

Die Maske liest jetzt die echte Antwort und kann, was eine Verwaltungsmaske können
muss: registrieren (mit Ereignisauswahl aus `GET /bereiche`, Ziel-URL und
optionalem Geheimnis), abmelden über die laufende Nummer, und das
Zustellprotokoll eines Eintrags ansehen. Der Knopf „Neuer Webhook" hatte vorher
keinen Handler. Beide Mutationen haben Sperre gegen Doppelausführung, gesperrten
Knopf während der Ausführung und sichtbare Rückmeldung in Erfolg und Fehlschlag.
Eine Kennzahl ist neu und fachlich die wichtigste: **wie viele Anbindungen ohne
Signatur** senden.

## Tabellen-Ratsche: 24 → 21 lebend

`domain_shared.webhooks` ist genauso ein falscher Verweis gewesen wie
`domain_pos.pos_transactions` im Kassenbericht; dazu liest die Kundenakte
`domain_crm.contacts`/`.crm_customers` nicht mehr an einem lebenden Weg (der
Handshake von gestern ist damit erledigt). Die Schwelle steht bündig bei 21.

**Blinder Fleck, bewusst nicht in diesem Slice behoben:**
`scripts/check_table_references.py` scannt nur `app/api/v1/endpoints`. Wandert
rohes SQL in einen Dienst unter `app/services` — wie hier —, sinkt die Zahl, ohne
dass Schuld verschwindet. In diesem Fall ist nichts verdeckt worden, weil
`webhook_registrations` existiert. Die Prüfung auf `app/services` auszuweiten ist
richtig und ein eigener Vorgang; der Bestand dort ist **nicht** gemessen.

## Abnahme

28 Verträge in `tests/test_webhook_mandant_vertrag.py`:

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
| Vokabular | eine Liste in einer Schreibweise, beide alten Listen aufgegangen; vier alte Objektnamen werden angenommen und kanonisch gespeichert; ein unbekannter Bereich wird abgewiesen; **beide Wege sehen dieselbe Anbindung** |
| Zustellprotokoll | ein Erfolg und ein HTTP 500 ergeben `fehler_count = 1` und einen belegten letzten Versuch; fremde Versuche sind nicht lesbar; Abmelden nimmt das Protokoll mit |

7 Verträge in `packages/frontend-web/src/__tests__/pages/admin/webhooks.test.tsx`:
Darstellung der echten Antwort, Suche über Ziel-URL **und** Ereignis (der alte
Absturz), Registrieren mit Erfolgsmeldung, gesperrter Knopf ohne Eingabe,
sichtbarer Fehlschlag, Abmelden über die laufende Nummer, Zustellprotokoll im
Dialog.

```bash
DATABASE_URL=postgresql://valeo_dev:…@127.0.0.1:5432/valeo_probe   python -m pytest tests/test_webhook_mandant_vertrag.py -q
cd packages/frontend-web && npx vitest run src/__tests__/pages/admin/webhooks.test.tsx   --testTimeout=30000 --maxWorkers=2
```

**Ergebnis 2026-10-01:** 28 Backend-Verträge und 7 Frontend-Verträge grün, dazu
49 vorhandene Tests (`test_gs1_webhook_ruestliste.py`,
`test_security_webhooks_vies.py`, `test_security_outbound_policy.py`,
`test_l3c_smoke.py`). Zwei Tests in `test_gs1_webhook_ruestliste.py` rufen die
Endpunktfunktionen direkt und positionell auf; sie wurden auf den
Mandantenparameter nachgezogen. `tsc` und `eslint` melden für die Maske nichts.

Geprüft wurde gegen die **vorhandene** gemeinsame Prüfstand-Datenbank, mit
eigenen Mandantenkennungen und ohne Zurücksetzen — nach
`test-database-resource-policy-20261001.md`.

Nebenbefund der Abnahme: `webhook_registrations.tenant_id` hat einen
Fremdschlüssel auf `tenants`. Die Testzeilen scheiterten zunächst daran — eine
echte Bedingung, die die gewachsene Entwicklungsdatenbank an anderen Stellen
verloren hat.

## Was die Spezifikation betrifft

Neu sind `DELETE /webhooks/abmelden/{nr}` (vorher `DELETE /{nr}`, unerreichbar)
und `GET /webhooks/{id}/zustellversuche`. Die OpenAPI-Spezifikation driftet
dadurch; der laufende `OPENAPI-DRIFT-REFRESH` hält ausdrücklich fest, dass jeder
spätere Router-Commit sie erneut regenerieren muss. Der Abfrageparameter
`tenant_id` bleibt in der Schnittstelle — er wird nur nicht mehr befolgt.
