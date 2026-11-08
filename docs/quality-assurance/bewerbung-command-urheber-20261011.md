# Bewerbung und Einwilligungsfassung anlegen: Urheber, Idempotenz, Fehlermeldungen (Slice BEWERBUNG-COMMAND-URHEBER-20261011)

Stand: 2026-10-11 · Anlass: Prüfung der Masken-Commands aus MCP-MASK-CE-BATCH3, Handshake mit Codex
(`QUALITY-GATE-MASK-CONTRACT-20261011`)

## Befunde und Abhilfe

| Befund | Vorher | Jetzt |
|---|---|---|
| **Urheber einer Einwilligungsfassung** | Der Masken-Command nahm ihn aus dem Kopf `X-User-ID`, sonst aus dem Rumpf, sonst `"personal-user"`. Der fachliche Weg und der MCP-Weg nahmen ihn aus dem Rumpf. Nichts davon war geprüft. | Alle drei Wege nehmen `sub` aus dem geprüften Token. Ein Wert im Rumpf oder Kopf wird nicht gelesen. Nennt die Anmeldung keine Kennung, wird nichts geschrieben (403). |
| **Idempotenzschlüssel** | Wurde ins Audit geschrieben, aber nicht geprüft. Ein wiederholtes `execute` legte eine zweite Bewerbung an. | Derselbe Schlüssel legt einmal an; die Wiederholung liefert das frühere Ergebnis (`affectedIds`, `auditEntryId`). Derselbe Schlüssel mit anderen Angaben wird abgewiesen. Zwei gleichzeitige Läufe werden über eine Transaktionssperre je Schlüssel nacheinander gelegt. |
| **Bewerberdaten in Fehlermeldungen** | Eingabefehler gaben den Pydantic-Text samt Eingabe zurück. Datenbankfehler gaben `str(fehler)` zurück, also die Anweisung samt Parametern. | Eingabefehler nennen Feld und Regel. Datenbankfehler nennen Fehlerklasse, SQLSTATE und die verletzte Regel (`grund_ohne_daten`); der volle Fehler steht im Protokoll. Das gilt für alle Wege, die `fehler_deuten` nutzen. |
| **Audit ohne Urheber** | `crm_action_audit_log` hielt nicht fest, wer handelte; bei der Bewerbung stand stattdessen der Name der Bewerbenden in der Zusammenfassung. | Neue Spalte `performed_by` (Migration `audit_urheber_20261011`) mit der Kennung aus dem Token. Die Zusammenfassung nennt keinen Namen mehr: Das Audit überlebt den Löschlauf der Bewerbung. |

Eine Richtigstellung zum Handshake: Für **Fassungen** war die Dopplung enger als gemeldet. Derselbe
Wortlaut ist schon immer genau eine Fassung (409 mit der vorhandenen Nummer). Betroffen war die
Bewerbung.

## Entscheidungen

- **Ohne Schlüssel bleibt jede Bewerbung eine eigene.** Wer sich zweimal bewirbt, hat zwei
  Bewerbungen; ohne Schlüssel gibt es nichts zu erkennen. Die Maskenlaufzeit sendet den Schlüssel
  (`useActionRuntime`), wenn die Aktion einen trägt.
- **Die Vorschau verbraucht den Schlüssel nicht.** Nur `execute` prüft und schreibt ihn.
- **Eine gelöschte Bewerbung wird nicht wiederbelebt.** Gibt es den Satz zum Schlüssel nicht mehr,
  antwortet die Wiederholung „bereits ausgeführt“ und legt nichts an.
- **Kein eindeutiger Index auf dem Audit.** Die Tabelle wird von allen Maskenaktionen beschrieben;
  ein Index über Schlüssel hätte fremde Wege getroffen und in der gewachsenen Datenbank an
  Bestandsdubletten scheitern können. Die Durchsetzung liegt an den beiden Wegen.
- **`performed_by` ist nullbar.** Bestandszeilen haben keinen belegten Urheber. Nur Wege, die ihn
  übergeben, schreiben die Spalte; alle anderen bleiben unverändert.
- **Die Rolle wird weiter vor dem Datenbankzugriff geprüft.** Sie steht am Weg und zusätzlich als
  erster Parameter, aus dem die Kennung kommt.

## Nachweis

Im isolierten Lieferstand (HEAD-Worktree auf `ac7b576b5` plus die Dateien dieses Slices), gegen
`valeo_probe` nach `alembic upgrade head`:

- `tests/test_bewerbung_command_urheber_vertrag.py`: **19 Verträge grün** – Urheber auf dem
  fachlichen Weg und im Command trotz gefälschtem Kopf und Rumpf, Vorschau, fehlende Kennung (403,
  nichts geschrieben), Audit mit Urheber und ohne Namen; sechs Verträge zur Idempotenz; Eingabe- und
  Datenbankfehler ohne Bewerberdaten (echte Verletzung von `ck_bewerbung_name_gefuellt` auf beiden
  Wegen); Rollen unverändert.
- Zwei Erwartungen in Bestandsverträgen angepasst, nachdem Codex seine Dateien committet hatte:
  `erstellt_durch` ist die Kennung der Anmeldung statt des Rumpfwerts; die Fehlerdeutung nennt die
  Fehlerklasse (`InsufficientPrivilege`) statt des Rohtexts.
- Nachbarschaft: alle Bewerbungs-, Rollen-, Masken- und MCP-Verträge zusammen **572 grün**, darunter
  die Rollenmatrix „vor der Datenbank“ und die sechs Verträge aus
  `QUALITY-GATE-MASK-CONTRACT-20261011`.
- Gates grün: Single Head, Response-Modelle, OpenAPI-Doku und -Spec, Code-Inventare,
  Architektur-Index, tote Transaktionen, Tabellenverweise, Improvement-Pipelines.

## Offen

1. **Das Eingabefeld „Erstellt durch“ in der Maske der Einwilligungserklärungen** wird noch
   angezeigt und gesendet, aber nicht mehr gelesen. Es sollte aus Screen Definition, TS-Spiegel und
   `ErklaerungIn` verschwinden oder zur Anzeige werden.
2. **Andere Personenangaben aus dem Rumpf** in derselben Strecke sind unverändert:
   `entschieden_durch`, `beschluss_durch`, `durchgefuehrt_durch`, `erfasst_durch`. Sie sind als
   Angabe gedacht („wer hat entschieden“), nicht als Anmeldung; ob sie durch die Kennung ersetzt
   oder daneben gestellt werden, ist eine fachliche Entscheidung.
3. **Idempotenz der übrigen Masken-Commands** (`run_delegated_mask_action` und einzelne Handler)
   ist nicht geprüft worden.
