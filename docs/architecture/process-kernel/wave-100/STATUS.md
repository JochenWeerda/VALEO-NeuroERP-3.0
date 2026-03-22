# Wave 100 - Settlement Endabnahme E2E (Gap 004)

## Scope

Formaler Abschluss fuer den noch offenen Rest von `Gap 004`: Settlement inkl. Gutschrift, Belastung, Korrekturpfad und Freigabe-/Verbuchungsnachweis als zusammenhaengender End-to-End-Fluss.

## Zielbild

Ein Settlement soll nur nach fachlicher Freigabe verbucht werden koennen und danach einen sichtbaren Korrekturpfad ueber Gutschrift, Belastung oder dokumentierte Korrektur besitzen. Die Abschlusspruefung soll fuer alle Varianten maschinenlesbar auswertbar sein.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|---|---|---|---|
| AP1 | `app/api/v1/endpoints/agrar_settlements.py` | Approval-Status, Approval-History, Posting-Gate, Correction-Draft und Completion-Status fuer Settlements | abgeschlossen |
| AP2 | `app/api/v1/endpoints/credit_debit_memos.py` | Settlement-Referenz und Correction-Mode fuer Gutschrift-/Belastungsbelege | abgeschlossen |
| AP3 | `packages/frontend-web/src/pages/annahme/abrechnung.tsx` | Sichtbarer Freigabe-, Verbuchungs- und Korrekturpfad direkt an der Settlement-Seite | abgeschlossen |
| AP4 | `packages/frontend-web/src/pages/einkauf/gutschriften-belastungen.tsx` | Direkte Vorbelegung aus Settlement-Korrekturentwurf fuer Gutschrift/Belastung | abgeschlossen |
| AP5 | `tests/test_process_kernel_wave100_settlement_completion.py` | Endabnahme fuer Approval -> Posting -> Correction -> Completion-Status | abgeschlossen |

## Abnahmekriterien

- `post-fibu` blockiert, solange ein Settlement nicht `FREIGEGEBEN` ist.
- Die Settlement-API liefert Approval-Status, Approval-History und zulassige Folgeaktionen sichtbar aus.
- Fuer verbuchte Settlements existiert ein direkter Correction-Draft fuer `credit` und `debit`.
- Completion-Status fuer `GUTSCHRIFT`, `BELASTUNG` und `KORREKTUR` ist maschinenlesbar abrufbar.
- Frontend-Seiten verbinden Settlement, Freigabe und Korrekturbeleg ohne Medienbruch.

## Tests

- `python -m pytest tests/test_process_kernel_wave19_settlement_approval.py tests/test_process_kernel_wave73_settlement_gutschrift_freigabe.py tests/test_process_kernel_wave100_settlement_completion.py -q --no-cov`
- `pnpm --dir packages/frontend-web exec tsc --noEmit --pretty false`

## Status

`abgeschlossen` - 2026-03-22 - Settlement-Endabnahme ueber Freigabe, Verbuchung, Gutschrift, Belastung und Korrekturpfad formal geschlossen.
