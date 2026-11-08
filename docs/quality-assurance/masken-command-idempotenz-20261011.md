# Masken-Commands: Der Idempotenzschlüssel wird durchgesetzt

Stand: 2026-10-11 · Slice `MASKEN-COMMAND-IDEMPOTENZ-20261011` · offener Punkt aus
[Urheber, Idempotenz, Fehlermeldungen](bewerbung-command-urheber-20261011.md)

## Befund

Jeder Masken-Command las `_idempotencyKey` aus dem Rumpf und schrieb ihn in
`domain_crm.crm_action_audit_log`. **Keiner prüfte ihn.** Wer einen Auftrag nach einem Zeitlimit mit
demselben Schlüssel wiederholte, führte ihn ein zweites Mal aus, wo der Fachweg das nicht von sich
aus verhinderte: eine zweite Sanktionsprüfung im Protokoll, ein zweiter Bonuslauf, eine zweite Tour.
Wo der Fachweg es verhinderte (eine Freigabe ist nur einmal möglich), bekam der Aufrufer auf die
Wiederholung einen Fehler statt der Bestätigung, dass sein Auftrag gelaufen ist.

Betroffen waren alle 26 Schreibwege: elf über `run_delegated_mask_action`, fünfzehn mit eigenem
Ablauf (Fuhrpark, Logistik, Einkauf, Schulung, Bonuslauf, Frachttabelle, Postfach, Abfrageimport,
Sanktionsprüfung). Die zwei Bewerbungswege waren seit dem Vormittag geschlossen.

**Wer betroffen ist:** Das Frontend sendet keinen Schlüssel — dort schützt die Sperre des Knopfs
(`pending`-Zustand). Den Schlüssel senden Aufrufer der Schnittstelle und Agenten, also genau die,
die sich auf ihn verlassen.

## Abhilfe

Ein gemeinsamer Wächter in `app/services/mask_action_runtime_service.py`:

- `frueherer_lauf(...)` sperrt den Schlüssel bis zum Ende der Transaktion
  (`pg_advisory_xact_lock`) und sucht den Auditeintrag eines früheren Laufs. Die Sperre legt zwei
  gleichzeitige Läufe hintereinander.
- `wiederholter_auftrag(...)` liefert die Antwort auf einen schon gelaufenen Schlüssel — oder `None`.

| Fall | Antwort |
|---|---|
| Schlüssel schon gelaufen | Erfolg, „bereits ausgeführt", dieselbe Audit-Kennung und dasselbe Objekt; kein zweites Ereignis |
| Schlüssel schon gelaufen, aber für ein anderes Objekt | Fehler am Feld `_idempotencyKey`; nichts ausgeführt |
| Erster Lauf gescheitert | Der Schlüssel ist frei; die Wiederholung läuft |
| Trockenlauf (`validate`, `dryRun`, `propose`) | verbraucht den Schlüssel nicht |
| kein oder leerer Schlüssel | wie bisher |

Der Schlüssel gilt je Mandant, Aktion und Objektart.

**Im Standardweg** steht der Wächter zweimal: vor der Zustandsprüfung (nach dem ersten Lauf passt
der Zustand nicht mehr — „schon freigegeben" wäre die falsche Antwort auf die Wiederholung
desselben Auftrags) und noch einmal in der Schreibtransaktion (die erste Sperre endet mit der
Prüfung). **In den Einzelwegen** steht er am Beginn der Schreibtransaktion.

Keine Migration, kein neues Feld: Der Auditeintrag ist der Beleg, dass ein Schlüssel gelaufen ist.
Er entsteht in derselben Transaktion wie die fachliche Änderung.

## Grenzen

1. **Kein Vergleich der Angaben.** Das Audit speichert den Rumpf nicht. Derselbe Schlüssel mit
   anderen Angaben wird als Wiederholung beantwortet, nicht als Widerspruch. Nur die zwei
   Bewerbungswege vergleichen mit dem gespeicherten Satz.
2. **Wege mit eigener Vorprüfung** (z. B. Frachttabelle: „Nummer schon vergeben") antworten auf
   eine Wiederholung weiterhin mit ihrem fachlichen Fehler, weil die Vorprüfung vor dem Wächter
   steht. Doppelt entsteht dort nichts; nur die Antwort ist „gibt es schon" statt „bereits
   ausgeführt".
3. **`rations_lifecycle.py`** liest den Schlüssel und prüft ihn nicht: Der Lebenszyklus lehnt einen
   zweiten Übergang ab, und ein Audit mit Schlüssel schreibt der Weg nicht. Als Ausnahme mit Grund
   im Vertrag geführt; schreibt er später ein Audit, wird der Vertrag rot.
4. **`actionDef.idempotencyKey` im Frontend** ist ein fester Wert je Aktionsdefinition. Heute setzt
   ihn keine Maske. Würde eine ihn setzen, liefe jede Aktion dieser Maske genau einmal je Mandant.
   Ein Schlüssel gehört zu einem Auftrag, nicht zu einer Aktion — das Feld braucht vor einer
   Verwendung eine andere Bedeutung.

## Mitgeprüft: der Agentenweg

`app/services/mcp_execution_service.py` hat einen eigenen Schutz (`public.mcp_tool_executions`,
Sperre, Vergleich von Urheber und Prüfsumme der Angaben) und verlangt den Schlüssel bei `execute`
und `propose`. Alle 38 Audit-Schreibstellen dort liegen hinter dieser Prüfung. Kein Befund.

## Nachweis

`tests/test_masken_command_idempotenz_vertrag.py`, 16 Verträge gegen `valeo_probe`:

- Standardweg mit echter Sitzung: einmal je Schlüssel, ohne Schlüssel wie bisher, Antwort vor der
  Zustandsprüfung, anderes Objekt ist ein Fehler, gescheiterter Lauf und Trockenlauf verbrauchen
  nichts, Schlüssel je Mandant, **zwei gleichzeitige Läufe führen einmal aus**.
- Einzelweg über HTTP: eine wiederholte Sanktionsprüfung schreibt ein Protokoll, nicht zwei.
- Ratsche: Jede Datei, die `parse_action_body` nutzt und ein Audit schreibt, hat je Schreibstelle
  einen Wächter. Ein neuer Command ohne Wächter macht den Vertrag rot.

Gegenprobe: Mit abgeschaltetem Wächter sind fünf dieser Verträge rot.
