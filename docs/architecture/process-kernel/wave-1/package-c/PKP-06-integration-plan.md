# PKP-06 Integration Plan

## Reihenfolge

1. `policy-manager`
   - rendert Backend-`explainability` direkt
2. `workflow-sandbox`
   - blockiert Preview ohne versionierte Definitionsmetadaten
3. `annahme/qualitaets-check`
   - zeigt kompakten Entscheidungs- und Referenzstatus
4. `annahme/abrechnung`
   - bleibt Detailpfad fuer Referenzkette, Ausnahmehinweise und Explainability

## Abhaengigkeiten

- Backend liefert stabile `ExplainabilityView`-Responses
- Backend liefert stabile `ProcessReferenceContext`-Responses
- Sandbox liefert verbindlich `definition_version`, `definition_origin`, `definition_status`
