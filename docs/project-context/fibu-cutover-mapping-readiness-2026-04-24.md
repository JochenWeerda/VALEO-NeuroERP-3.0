# FIBU Cutover Mapping Readiness

Stand: `2026-04-24`

## Zweck

Der Cutover kann erst produktiv freigegeben werden, wenn Konten-, Steuer-, Kostenstellen- und Gegenkonto-Mappings fachlich genehmigt sind.
Repo-seitig ist jetzt ein formaler Pruefpfad vorhanden.

## Artefakte

- Vorlage: `config/fibu_cutover_mapping.template.yaml`
- Validator: `python scripts/check_fibu_cutover_mapping.py --mapping <datei>`
- Strikter Gate-Modus: `python scripts/check_fibu_cutover_mapping.py --mapping <datei> --strict`

## Pflichtbereiche

| Bereich | Zweck | Freigabe |
|---|---|---|
| `accounts` | L3-Konten auf Zielkonten | jedes Mapping `status: approved` |
| `tax_codes` | Steuerkennzeichen und Saetze | jedes Mapping `status: approved`, `rate` empfohlen |
| `cost_centers` | Kostenstellen/Profitcenter | jedes Mapping `status: approved` |
| `counter_accounts` | Kontextabhaengige Gegenkonten | jedes Mapping `status: approved` |

## Blocker

- `metadata.approval_status` muss `approved` sein.
- `metadata.approved_by` und `metadata.approved_at` muessen gesetzt sein.
- Jeder Pflichtbereich braucht mindestens einen Eintrag.
- Jeder Eintrag braucht Quelle, Ziel und `status: approved`.

## Grenze

Der Validator ersetzt keine fachliche Freigabe.
Er verhindert nur, dass ein unvollstaendiges oder als Draft markiertes Mapping als cutover-ready behandelt wird.
