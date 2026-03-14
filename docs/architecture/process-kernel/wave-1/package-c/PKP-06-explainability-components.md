# PKP-06 Explainability Components

## Gemeinsamer UI-Rahmen

- Adapter: `buildDecisionView(...)`
- Zielzustaende: `allowed`, `blocked`, `approval-required`, `exception`
- Darstellungsbausteine:
  - Statuskarte mit `statusLabel`, `summary`, `details`
  - Referenzkarte mit `process_key`, `anchor_entity`, `anchor_id`, `chain`
  - Workflow-Metadatenkarte mit `definition_version`, `definition_origin`, `definition_status`

## Verbindliche Regeln

- API-Explainability ist Primaerquelle fuer Entscheidungsdarstellung.
- Lokale Ableitungen sind nur Altlastenschutz, nicht Regelpfad.
- Neue Kernmasken duerfen keine zweite Explainability-Mapping-Logik einfuehren.
