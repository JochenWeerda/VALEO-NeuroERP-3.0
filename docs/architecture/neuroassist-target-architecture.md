# NeuroASSIST Target Architecture

## Ziel

`NeuroASSIST` ist der fachliche Orchestrierungs- und Assistenten-Layer fuer VALEO-NeuroERP.

`LangGraph` bleibt die technische Engine fuer:
- State
- Resume
- Checkpoints
- Human-in-the-loop-Unterbrechungen

Das fachliche Steuerungsmodell ist:

`case-based orchestration with stages, gates, contracts and audited commands`

Damit wird die fruehere generische Agent-/APM-Mode-Welt durch ein ERP-taugliches Modell ersetzt.

## Warum die alten Modes nicht mehr passen

Die Begriffe `VAN`, `PLAN`, `CREATE`, `IMPLEMENT`, `REFLECT` stammen aus einem generischen Entwicklungs- und Meta-Agenten-Kontext. Fuer VALEO-NeuroERP sind sie aus vier Gruenden nicht mehr passend:

1. Sie beschreiben interne KI-Arbeit, nicht fachliche ERP-Ablaufe.
2. Sie foerdern Prompt-getriebene Parallelwelten statt Process-/Policy-/Command-Contracts.
3. Sie sind fuer Human Approval, Audit, DQ und Seiteneffekte zu unscharf.
4. Sie vermischen produktive Fachorchestrierung mit internem Tooling.

Deshalb wird das bisherige Mode-Modell fachlich abgeloest, nicht nur umbenannt.

## Zielbild

NeuroASSIST besteht aus drei Schichten:

1. `Business Workflow`
- produktive, fachliche, zustandsbehaftete Ablaufsteuerung
- Beispiele: Bestellvorschlag, Finance-Skonto, Compliance-Fall, DQ-Ausnahmebehandlung

2. `Operational Assistant`
- kontextbezogene Assistenz innerhalb eines bestehenden Prozesses
- Beispiele: naechste Aktion, Risikoerklaerung, Eskalationsvorschlag, Begruendung

3. `Improvement Runbook`
- interne, nicht-produktive Verbesserungs- und Diagnoseablaeufe
- Beispiele: Incident-Triage, Architekturpruefung, Connector-Diagnose

Wichtig:
- Produktive Fachorchestrierung liegt unter `app/agents`
- internes Tooling liegt ausserhalb des produktiven Pfads
- Seiteneffekte laufen ueber Commands oder explizite Persistenz-Services
- Engine-spezifische Aufrufe wie LangGraph-Trigger/Resume sitzen hinter Workflow-Runner-Adaptern, nicht direkt im Service-Layer

## Begriffsmodell

### Behalten

- `workflow`
- `case`
- `run`
- `stage`
- `gate`
- `capability`
- `role contract`

### Ersetzen

- historischer Produktbegriff -> `NeuroASSIST`
- `mode` -> `stage` oder `orchestration_state`
- `cycle` -> `workflow_run` oder `orchestration_run`
- `loop` -> `iteration` nur fuer Improvement-Pfade
- `soul` -> `role_contract`
- freie `skills` im APM-Sinn -> `capability_pack`

### Sprachregel

`cycle` und `loop` bleiben nur fuer interne kontinuierliche Verbesserung oder Monitoring sinnvoll.

Fuer produktive ERP-Orchestrierung werden sie nicht mehr als Leitbegriffe verwendet.

## Orchestrierungsmodell

### Standard-Stages

Jeder NeuroASSIST-Fall durchlaeuft je nach Typ diese fachlichen Stages:

1. `intake`
- Ziel, Fall oder Signal aufnehmen
- Scope und Kontext identifizieren

2. `analysis`
- Datenlage, Prozesskontext, Policy, Risiken, DQ und Historie bewerten

3. `proposal`
- strukturierte Empfehlung oder Entscheidungsvorlage erzeugen

4. `approval`
- Human Gate oder Policy Gate
- genehmigen, ablehnen, eskalieren oder delegieren

5. `execution`
- kontrollierte Ausfuehrung ueber Commands oder Services

6. `verification`
- Ergebnis, Policy, DQ, Vollstaendigkeit und Seiteneffekte pruefen

7. `closure`
- Audit, Handover, Statusabschluss, naechste Aktion

8. `improvement`
- optional fuer interne Verbesserung, nicht Standard in produktiven Faellen

### Gates

Zwischen Stages duerfen nur explizite Gates den Uebergang freigeben:

- `approval_gate`
- `policy_gate`
- `dq_gate`
- `role_gate`
- `process_gate`

Ohne erfuellten Gate-Entscheid keine implizite Fortsetzung.

## Standardmuster fuer Workflows

### 1. Decision Workflow

Schema:

`intake -> analysis -> proposal -> approval -> execution -> verification -> closure`

Beispiele:
- Bestellvorschlag
- Zahlungslauf-Vorbereitung
- Settlement-Freigabe

### 2. Exception Workflow

Schema:

`intake -> analysis -> proposal -> approval -> execution -> verification -> closure`

Spezifik:
- Ausloeser ist ein Fehler, Konflikt oder Policy-/DQ-Verstoss

Beispiele:
- Importausnahme
- Matching-Konflikt
- Connector-Fehler

### 3. Review Workflow

Schema:

`intake -> analysis -> proposal -> closure`

Optional:
- `approval`, falls aus dem Review direkt eine Aktion vorbereitet wird

Beispiele:
- Compliance-Pruefung
- USTVA-Vorpruefung
- Closing-Review

### 4. Ingestion Workflow

Schema:

`intake -> analysis -> verification -> approval -> execution -> closure`

Spezifik:
- DQ und Konfliktpruefung liegen vor Persistenz

Beispiele:
- CSV-/Dateiimport
- Connector-Ingestion
- Portal-Erfassung

### 5. Improvement Runbook

Schema:

`intake -> analysis -> proposal -> execution -> verification -> closure`

Optional:
- mehrere `iterations`

Beispiele:
- Architekturhaertung
- Betriebsdiagnose
- Performance- oder DQ-Verbesserung

## Rollenmodell

NeuroASSIST arbeitet nicht mit diffusen Personas, sondern mit `Role Contracts`.

### Role Contract Schema

Jede Rolle beschreibt:

- `role_key`
- `purpose`
- `scope`
- `owned_process_scopes`
- `allowed_actions`
- `forbidden_actions`
- `required_inputs`
- `allowed_commands`
- `required_gates`
- `explainability_requirements`
- `handover_requirements`

### Beispielstruktur

```yaml
role_key: procurement_assistant
purpose: Einkaufsentscheidungen vorbereiten und kontrolliert ausfuehren
scope:
  domains: [einkauf, disposition]
  process_definitions: [contract_to_intake]
owned_process_scopes:
  - purchase_order
allowed_actions:
  - analyze
  - propose
  - prepare_command
forbidden_actions:
  - bypass_human_approval
  - invent_fallback_ids
  - perform_uncontracted_http_calls
required_inputs:
  - process_context
  - policy_context
  - command_catalog
  - read_models
allowed_commands:
  - CreatePurchaseOrder
required_gates:
  - approval_gate
  - role_gate
explainability_requirements:
  - decision_reason
  - evidence_refs
handover_requirements:
  - audit_entry
  - workflow_status
```

## Prompt-Modell

### Grundsatz

Keine freien Monsterprompts.

Jede Rolle bekommt ein `Prompt Pack`, zusammengesetzt aus festen Bloecken.

### Prompt Pack Template

```text
Mission:
Du unterstuetzt im fachlichen Scope X.

Scope:
Du arbeitest nur auf den definierten Aggregaten, Prozessen und Read Models.

Allowed Actions:
Du darfst analysieren, validieren, vorschlagen und vorbereitete Commands erzeugen.

Forbidden Actions:
Keine stillen Defaults, keine unbestaetigten Schreibvorgaenge, keine Policy-Umgehung,
keine erfundenen IDs, keine freien HTTP-Nebenpfade.

Decision Policy:
Wenn Daten unvollstaendig sind -> ablehnen oder eskalieren.
Wenn Risiko hoch ist -> Approval Gate.
Wenn Contract fehlt -> nicht ausfuehren.

Inputs:
Process Context, Workflow Version, Policy Result, DQ Result, relevante Read Models.

Output:
Typed Schema mit Entscheidung, Begruendung, Risiken, Evidenz und naechster Aktion.

Handover:
Schreibe Audit-, Status- und Gate-Resultate im definierten Contract.
```

### Prompt-Pack-Bausteine

Ein Prompt Pack besteht aus:

- `mission`
- `scope`
- `constraints`
- `decision_policy`
- `input_contract`
- `output_contract`
- `handover_rules`

Das Prompt Pack ist sprachlich.
Die Ausfuehrung wird zusaetzlich technisch durch Capability Packs begrenzt.

Stand:
- als expliziter Vertragsbaustein umgesetzt
- Capability-Packs referenzieren jetzt konkrete Prompt Packs

## Capability-Modell

### Capability Pack

Ein `Capability Pack` ist die technische Ausfuehrungsoberflaeche einer Rolle.

Es definiert:

- Queries / Read Models
- Policies
- Commands
- Tools
- erlaubte Persistenzpfade
- Gate-Abhaengigkeiten

### Ziel

Prompt und Capability duerfen nie auseinanderlaufen.

Die Rolle darf nur das ausfuehren, was technisch im Capability Pack freigegeben ist.

Stand:
- als erweiterter Execution-Pfad umgesetzt
- Capability-Packs referenzieren jetzt konkrete Execution Packs mit Read Models, Policy-Resolvern, Commands, Services, Audit-Sinks und Side-Effect-Klassen

## Technisches Ausfuehrungsmodell

### NeuroASSIST Runtime

Die Runtime benoetigt diese Bausteine:

1. `Case Resolver`
- identifiziert Fall, Tenant, Prozessdefinition, Workflow-Version und Kontext

2. `Role Contract Resolver`
- waehlt die zulaessige Rolle

3. `Capability Resolver`
- laedt die technische Ausfuehrungsoberflaeche

4. `Stage Engine`
- fuehrt die Stages in der definierten Reihenfolge aus

5. `Gate Engine`
- prueft Approval, Policy, DQ, Rollen und Process Gates

6. `Command Boundary`
- alle Seiteneffekte laufen ueber Commands oder klar definierte Services

7. `Audit Sink`
- Entscheidungen, Evidenz, Gate-Entscheide und Ergebnisse werden persistiert

8. `Resume Engine`
- unterbrochene Faelle werden sauber wiederaufgenommen

Stand:
- generischer Audit-/Explainability-Sink ist im Anwendungskern eingefuehrt
- offen bleibt die durchgaengige Bruecke in die bestehenden Process-Audit- und Workflow-Version-Contracts

### Rolle von LangGraph

LangGraph ist:

- State Engine
- Checkpoint Engine
- Resume Engine

LangGraph ist nicht:

- das fachliche Zielmodell
- das Prompt-Modell
- das Rollenmodell
- das Policy-Modell

## Fachlich benoetigte NeuroASSIST-Rollen

### Produktiv

1. `procurement_assistant`
- Bestellvorschlag
- Lieferanten- und Bedarfsbegruendung
- Freigabevorbereitung

2. `finance_action_assistant`
- Skonto
- Zahlungsvorschlaege
- Closing- und USTVA-Unterstuetzung

3. `compliance_review_assistant`
- Regelpruefung
- Risikoerklaerung
- Massnahmenvorschlaege

4. `data_quality_assistant`
- Ursachenanalyse bei DQ-Verletzungen
- strukturierte Korrekturvorschlaege

5. `operations_exception_assistant`
- Ausnahmebehandlung in Annahme, Qualitaet, Settlement, Import

### Intern

6. `platform_improvement_assistant`
- Architektur-, Betriebs- und Integrationsverbesserung
- kein produktiver Fachagent

## Mapping Alt -> Neu

| Alt | Neu | Bewertung |
|-----|-----|-----------|
| historischer Produktbegriff | NeuroASSIST | Produktbegriff ersetzen |
| mode | stage | fachlich praeziser |
| cycle | workflow_run / orchestration_run | nur fuer Runtime |
| loop | iteration | nur fuer Improvement |
| VAN | intake + analysis | aufspalten |
| PLAN | proposal | fachlich konkretisieren |
| CREATE | execution preparation | als eigener Leitbegriff entfaellt |
| IMPLEMENT | execution | fachlich konkretisieren |
| REFLECT | verification + improvement | aufspalten |
| soul | role_contract | technisch belastbar |
| freie skill-kombination | capability_pack | kontrollierte Ausfuehrung |

## Migrationsplan

### Phase 1: Begriffe und Architektur

- `NeuroASSIST` als Zielbegriff in Architektur und Roadmap verankern
- historische Altbegriffe nur noch als Altbezug markieren
- `mode`/`cycle`/`loop` in Zieltexten nicht mehr als Leitbegriffe verwenden

### Phase 2: Vertragsmodell

- `RoleContract`
- `CapabilityPack`
- `StageDefinition`
- `GateDecision`
- `CaseRun`
- `WorkflowSchema`
- `CaseStageTransition`

als explizite Kernvertraege definieren

Stand:
- im Anwendungskern umgesetzt
- offen bleibt die generische Runtime-Ausfuehrung ueber diese Vertraege

### Phase 3: Runtime

- bestehende `app/agents`-Workflows auf Stage/Gate-Modell heben
- LangGraph als technische Engine beibehalten
- Seiteneffekte ueber Command Boundary erzwingen

Stand:
- Bestellvorschlag, Finance-Skonto, Compliance, Data-Quality und Operations-Exception schreiben bereits Stage-/Gate-Zustaende
- generische Run-/Gate-API ist produktiv
- `NeuroAssistService` nutzt jetzt eine generische Runner-/Schema-Registry fuer Run-, Status- und Gate-Ausfuehrung
- PromptPack-/ExecutionPack-Vertraege sowie ein generischer Audit-/Explainability-Sink sind eingefuehrt
- die Bruecke in die bestehenden Process-Audit-/Workflow-Version-Contracts ist konservativ eingefuehrt
- ein zentraler Context-Resolver fuer Prozessdefinition, Aggregatkontext und Workflow-Version ist eingefuehrt
- Policy-, DQ- und Read-Model-Aufloesung sind jetzt ebenfalls zentral im Resolver verankert
- offen bleibt die vollstaendige Nutzung dieses Resolvers durch weitere Capabilities ohne verbleibende capability-spezifische Kontextbeimischung

### Phase 4: Prompt Packs

- pro Rolle standardisierte Prompt Packs einfuehren
- keine freien Workflow-Sonderprompts mehr

### Phase 5: Rollout

- `bestellvorschlag_assistant`
- `finance_skonto_assistant`
- `compliance_copilot`
- `data_quality_assistant`
- `operations_exception_assistant`

schrittweise in das neue NeuroASSIST-Modell ueberfuehren

### Phase 6: Aufraeumen

- verbliebene Alt-Artefakte aus APM-/Mode-Welt stilllegen oder loeschen
- interne Improvement-Runbooks sauber von produktiver Orchestrierung trennen

## Architekturregeln

1. Produktive NeuroASSIST-Faelle laufen nur ueber definierte Stages und Gates.
2. Kein Agent fuehrt ungecontractete Seiteneffekte aus.
3. Keine stillen Ersatzkonfigurationen, Fallback-IDs oder Mock-Nebenpfade in produktiven Faellen.
4. Jede agentische Entscheidung erzeugt Explainability- und Audit-Daten.
5. Prozessbezug, Workflow-Version und Command-Vertrag muessen konsistent sein.
6. Improvement-Runbooks sind getrennt von produktiven Fachworkflows zu halten.

## Zielentscheidung

Das Zielmodell fuer VALEO-NeuroERP lautet:

- `NeuroASSIST` = fachlicher Orchestrierungs- und Assistenten-Layer
- `LangGraph` = technische State-/Resume-/Checkpoint-Engine
- `Steuerungsmodell` = case-based orchestration with stages, gates, contracts and audited commands

Das ersetzt die alte generische APM-/Agenten-Mode-Welt vollstaendig.
