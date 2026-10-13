# DocFlow: Teilmengen über mehrere Folgebelege, verbindliche Statushistorie

Stand: 2026-10-13 · Slice `DOCFLOW-TEILMENGEN-STATUSHISTORIE-20261013` · Phase 0.2 und 0.3 aus
[Bestandsprüfung Screen Framework](../design/screen-framework-fiori-gap-analyse.md)

## Auftrag und Bedingungen

Entscheidung des Auftraggebers vom 13.10.2026: DocFlow wird die führende Belegstruktur — unter der
Bedingung, dass es Teilrechnungen und revisionssichere Statuswechsel nachweislich trägt.

Bedingungen von Codex (Identität), vom Auftraggeber übermittelt:

1. Teilmengen ausdrücklich anfordern; ein bloßer Wiederholungsaufruf erzeugt keinen zusätzlichen Folgebeleg.
2. Idempotenz: derselbe Schlüssel mit identischem Inhalt liefert denselben Beleg, mit verändertem
   Inhalt wird er abgewiesen. Aufrufer gemeinsam anpassen.
3. Restmengen atomar: Folgebeleg, Mengenreferenzen und Restmenge in einer Transaktion; parallele
   Aufrufe übernehmen nie mehr als verfügbar.
4. Statushistorie und Audit verbindlich: Scheitert die Protokollierung, schließt die Änderung nicht
   erfolgreich ab. Der Akteur kommt aus der geprüften Anmeldung.
5. Abnahme gegen den Prüfstand: Wiederholung, Parallelzugriff, Teilmengen, Storno, Rollback.

## Vorher

- Je Quellbeleg und Folgeart gab es genau einen Folgebeleg — doppelt gesichert durch
  `uq_docflow_header_link_source_relation` und einen eindeutigen Index. Ein zweiter Aufruf gab den
  ersten Folgebeleg zurück; ein zweiter Teillieferschein entstand nie.
- Teilmengen wurden gegen die volle Quellmenge geprüft, nicht gegen das schon Umgewandelte.
- Die Idempotenz verglich nur den Schlüssel: Derselbe Schlüssel mit anderem Inhalt bekam die alte Antwort.
- Der Status wurde im Kopf überschrieben, ohne Historie. Das Protokoll (`best_effort_audit`) schrieb
  ohne Benutzer und verschluckte Fehler; in der gewachsenen Datenbank gibt es seine Zieltabelle
  `infrastructure.audit_log` nicht — dort wurde nie etwas protokolliert.
- Wer handelte, stand in der Anfrage (`created_by`, `released_by`, `posted_by`, `reversed_by`).
- `PUT /docflow/{id}` konnte den Status auf `posted` setzen, ohne zu buchen.
- Die Stornobuchung schrieb sich fest, bevor Nachweis und Belegstatus geschrieben waren.

## Jetzt

### Teilmengen (0.2)

- Migration `docflow_teilmengen_statushistorie_20261013` (ein Head): Eindeutig ist das Paar
  Quelle/Ziel (`uq_docflow_header_link_pair`); der alte Schutz und der eindeutige Index entfallen.
- **Restmenge je Position** = Belegmenge minus Summe der Mengen in Folgebelegen derselben Art
  (`umgewandelte_mengen`). Stornierte, abgebrochene und gelöschte Folgebelege zählen nicht: Ihre Menge
  ist wieder frei.
- **Ohne Mengenangabe** geht der ganze Beleg in den Folgebeleg — aber nur, solange noch nichts
  umgewandelt ist. Danach verlangt DocFlow die Mengen ausdrücklich (409) und erzeugt keinen Beleg.
- **Mit Mengenangabe** entsteht ein Teilbeleg; mehr als die Restmenge wird abgelehnt:
  „Position 1: Menge 5 übersteigt die Restmenge 4 (Beleg 10, bereits umgewandelt 6)."
- Lieferschein und Rechnung aus demselben Auftrag haben je eigene Restmengen.
- **Atomar und nacheinander:** Das Kommando sperrt den Quellbeleg (`SELECT … FOR UPDATE`), prüft
  danach die Idempotenz und schreibt Folgebeleg, Positionsbezüge, Protokoll und Idempotenzantwort in
  einer Transaktion. Jede frühe Rückkehr (Wiederholung, Trockenlauf) gibt die Sperre sofort frei.

### Idempotenz

- `command_idempotency_keys.request_hash`: Der Inhalt der Anfrage wird mit gespeichert. Gleicher
  Schlüssel und gleicher Inhalt → dieselbe Antwort; gleicher Schlüssel und anderer Inhalt → 409
  „Der Idempotenzschlüssel wurde bereits mit anderem Inhalt verwendet". Gilt für Umwandeln,
  Freigeben, Buchen, Stornieren.
- Angepasster Aufrufer: „Sofortrechnung" im Auftrag (`OrderEditorLegacyPage`) schickte je Klick einen
  neuen Zufallsschlüssel und verließ sich darauf, den vorhandenen Beleg zurückzubekommen. Der Schlüssel
  ist jetzt je Auftrag fest; ein zweiter Klick liefert dieselbe Rechnung. Andere Aufrufer des
  Umwandelns gibt es im Repository nicht (geprüft: Frontend, Backend, Playwright).

### Statushistorie und Protokoll (0.3)

- `domain_docflow.document_status_history`: von, nach, Kommando, wer, warum, wann. **Die Datenbank
  schreibt sie** (Trigger auf `document_headers`), in derselben Transaktion wie der Wechsel. Kein Weg,
  auch kein rohes SQL, ändert den Status ohne Eintrag; scheitert der Eintrag, scheitert der Wechsel.
  Auch das Löschen eines Entwurfs steht darin (`geloescht`).
- `domain_docflow.document_command_log`: jedes Kommando (anlegen, ändern, freigeben, umwandeln,
  buchen, stornieren, löschen, Druck, Ausgabe) mit Akteur und Inhalt, vom Dienst in derselben
  Transaktion geschrieben, nicht „best effort". `best_effort_audit` spiegelt weiter ins zentrale
  Audit-Log, wo es eines gibt.
- **Unveränderlich:** Beide Tabellen lehnen `UPDATE` und `DELETE` ab. Löschen geht nur mit dem
  Wartungsschalter `valeo.docflow_wartung = 'loeschen'` (Entfernen eines Mandanten, Testaufräumen).
- **Akteur aus der Anmeldung:** Alle neun schreibenden DocFlow-Wege verlangen jetzt die Anmeldung und
  übergeben die Kennung des angemeldeten Benutzers. Was die Anfrage als `*_by` mitschickt, zählt nicht.
- `GET /docflow/{id}/status-history` liest die Historie.
- **Buchungsstatus nur durch Kommandos:** Ein Beleg wird nicht als `posted`, `reversed` oder
  `cancelled` angelegt, und `PUT` setzt weder `posted` noch `reversed`.
- **Storno in einem Commit:** Stornobuchung, Nachweis, Historie und Belegstatus werden gemeinsam
  festgeschrieben.

## Auslegungen (meine, nicht entschieden)

- **„Ausdrücklich" heißt: Mengen je Position in der Anfrage.** Der erste Aufruf ohne Mengen wandelt
  den ganzen Beleg um; das ist die vollständige Umwandlung, keine Teilmenge.
- **Ein neuer Schlüssel ist ein neuer Auftrag.** Zwei Aufrufe mit verschiedenen Schlüsseln und
  denselben Teilmengen erzeugen zwei Teilbelege, solange Restmenge da ist.
- **Akteur ist die Kennung `sub` der Anmeldung.** Dienste ohne Anmeldung (interne Aufrufe) dürfen
  weiter einen Akteur nennen.

## Befunde, nicht behoben

- **Mandant aus der Anfrage** (Phase 0.1): unverändert, liegt bei Codex. Die Lesewege haben weiterhin
  keine eigene Anmeldeprüfung am Weg.
- **Auftrag doppelt fakturierbar (nach dem Code, nicht nachgestellt):** Die Restmenge gilt je Folgeart.
  Ein Auftrag lässt sich direkt fakturieren (`order_to_invoice`) und zusätzlich über seine Lieferscheine
  (`delivery_to_invoice`).
- **`infrastructure.audit_log` fehlt in der gewachsenen Datenbank.**
- **Async-Wege mit blockierenden Datenbankaufrufen:** Die DocFlow-Wege sind `async def` und rufen
  synchron in die Datenbank. Ein wartender Aufruf blockiert die Ereignisschleife. Der Paralleltest
  hat darüber einen Deadlock gezeigt (Sperre über die Rückkehr hinaus gehalten); der ist behoben,
  die Bauart bleibt.

## Nachweis

- `tests/test_docflow_teilmengen_statushistorie.py`: 19 bestanden gegen `valeo_probe` —
  drei Teillieferscheine und Schluss, Überlieferung mit Restmenge in der Meldung, Wiederholung ohne
  Mengen erzeugt keinen Beleg, vollständige Umwandlung und keine zweite, eigene Restmengen je
  Folgeart, gleicher Schlüssel gleicher Inhalt, gleicher Schlüssel anderer Inhalt, **acht parallele
  Teillieferungen zu je 3 aus 10 (genau drei gelingen, Summe 9)**, sechs parallele Wiederholungen
  desselben Auftrags (ein Beleg), Storno gibt die Menge frei, Historie mit angemeldetem Benutzer
  trotz fremder Angabe in der Anfrage, Statuswechsel am Dienst vorbei wird festgehalten, Historie und
  Protokoll unveränderlich, **Protokollausfall rollt Folgebeleg und Buchung zurück**, Ausfall der
  Historie verhindert den Wechsel, kein Anlegen als gebucht, kein `posted` per `PUT`.
- Bestehende DocFlow-Tests, Rechnung, Übergabe: zusammen 110 bestanden; weitere Tests mit
  DocFlow-Bezug: 250 bestanden. Angepasst: `test_docflow_draft_cleanup.py` (Reihenfolge der
  Anweisungen) und `test_docflow_steuerschluessel.py` (Anmeldung, Aufräumen mit Wartungsschalter).
- `check_pagination`, `check_dead_transactions`, `check_baseline_integrity`: in Ordnung.

**Nicht geprüft:** der Klick „Sofortrechnung" im Browser.
