# BELEG-021: Aktionen der Belegmaske

Stand: 2026-10-13 · Slice `BELEG-021` · aus dem
[Masterplan Belegmaske mit Varianten](../design/belegmaske-varianten-masterplan.md) ·
Folge aus [Belegmaske mit Varianten](belegmaske-varianten-20261013.md) und
[Risikobasierte Freigabe](approval-001-freigabe-20261013.md) · schließt die Lücke aus
`beleg-action-state-binding-20261013.md` („DocFlow-/Approval-Command-Adapter fehlt")

## Geliefert

Ein Aktionsweg für die Belegmaske:
`POST /api/v1/belege/{belegart}/{beleg_id}/actions/{aktion}` — über die vorhandene Laufzeit der
Maskenaktionen (`run_delegated_mask_action`: Trockenlauf, Ausführung, Audit, Ereignis, Wiederholung).

| Aktion | Fachkommando |
|---|---|
| `freigeben` | DocFlow: freigeben (endgültige Belegnummer) |
| `buchen` | DocFlow: buchen über Finance |
| `stornieren` (mit Grund) | DocFlow: stornieren mit Gegenbuchung |
| `umwandeln:<belegart>` | DocFlow: Folgebeleg aus dem ganzen Rest je Position |
| `freigabe_anfordern:post` / `:reverse` | Approval Engine: anfragen |
| `freigabe_erteilen:…`, `freigabe_ablehnen:…` | Approval Engine: entscheiden |

- **Keine eigene Fachlogik** (`app/services/docflow_belegaktionen.py`): Ob eine Aktion geht, sagt der
  Belegvertrag — dieselbe Auskunft, an der der Knopf hängt (Zustand, Recht, Freigabe). Was dort
  gesperrt ist, lehnt der Weg mit demselben Grund ab. Ausgeführt wird das eine Fachkommando; seine
  Prüfungen gelten unverändert.
- **Idempotenz aus Beleg, Aktion und Belegversion:** Derselbe Klick auf denselben Stand wirkt genau
  einmal. Trägt die Maske ihren Stand mit (`version`), wird ein veralteter Stand abgewiesen.
- **Akteur aus der Anmeldung** in Statushistorie und Protokoll.
- **Die Definition der Maske ruft diesen Weg noch nicht.** `app/core/screen_definitions_beleg.py` ist seit
  dem Abend des 13.10.2026 bei Codex in Arbeit (`DOCFLOW-MASK-COMMAND-APPROVAL-20261013`, ein Adapter im
  Frontend). Ich habe die Datei nicht geändert; der Weg steht als Serverseite bereit.

## Nachweis

`tests/test_beleg_aktionen.py`, 8 bestanden gegen `valeo_probe`, an den Referenzbelegen:

- Trockenlauf nennt, was geht und was nicht (Sperrgrund der Freigabe, falscher Stand, unbekannte
  Aktion) und schreibt nichts.
- Ohne Rolle 403; mit Leserecht „Keine Berechtigung", nichts gebucht.
- Folgebeleg entsteht genau einmal; der zweite Klick wird abgewiesen.
- Buchen aus der Maske: veralteter Stand abgewiesen; gebucht mit Akteur in der Historie; derselbe Klick
  noch einmal bucht nicht doppelt.
- Freigabe anfragen und erteilen aus der Maske: Antragstellerin sieht „erteilen" gesperrt und wird vom
  Server abgewiesen; Sachbearbeitung ohne Recht abgewiesen; nach Erteilung ist Buchen aktiv und bucht.
- Storno: ohne Freigabe abgewiesen, Sachbearbeitung fragt nicht an, Buchhaltung erteilt keine
  R4-Freigabe, ohne Grund abgewiesen, dann storniert mit Gegenbuchung.
- Abgelehnte Freigabe gilt nicht; danach lässt sich neu anfragen.
- Wo ein Sachgrund sperrt, wird keine Freigabe angefragt.

Die Definition der Maske und ihre Tests sind unverändert.

## Grenzen

- **Zwei Wege zum selben Ziel, noch nicht entschieden:** dieser Aktionsweg auf dem Server und der Adapter
  im Frontend, den Codex baut. Der Serverweg hält Zustands-, Rechte- und Freigabeprüfung, Mengen und
  Idempotenzschlüssel an einer Stelle; der Adapter müsste dann nur ihn rufen.
- **Nicht im Browser geprüft.**
- **Folgebeleg immer über den ganzen Rest.** Teilmengen aus der Maske gibt es nicht; dafür bleibt der
  DocFlow-Weg mit ausdrücklichen Mengen.
- **Eine abgewiesene Freigabeentscheidung** (Funktionstrennung, fehlendes Recht) steht bei Aufrufen über
  diesen Weg nicht im Freigabeprotokoll: Die Laufzeit der Maskenaktionen rollt bei Ablehnung alles
  zurück. Über `/api/v1/approvals/…` wird sie protokolliert.
- „Freigabe ablehnen" ist über den Weg möglich, hat aber keinen Knopf in der Definition.
- Anlegen und Bearbeiten eines Belegs in der Maske fehlen weiter.
- Schreibende MCP-Werkzeuge gibt es weiterhin nicht (MCP-WRITE-014).
