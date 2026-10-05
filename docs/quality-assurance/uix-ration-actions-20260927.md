---
title: Rations-Lifecycle ueber die Mask ActionRuntime
type: reference
audience: [agent, entwickler, qa]
owner: Codex
status: aktiv
last_reviewed: 2026-09-27
description: Vertrag und Nachweis fuer die sechs nativen Rations-Lifecycle-Aktionen.
---

# Rations-Lifecycle ueber die Mask ActionRuntime

Die native Maske `agrar/ration` fuehrt ihre Statusaktionen jetzt ueber echte
Command-Endpunkte aus. `Zur Pruefung`, `Freigeben`, `Fuetterungsbeginn planen`,
`Jetzt aktivieren`, `Fuetterung beenden` und `Archivieren` adressieren die Ration
mit `{entity_id}`. Der Server ermittelt daraus die neueste unveraenderliche
Version und delegiert `execute` an den vorhandenen `RationLifecycleService`.

Es gibt keine zweite Statusmaschine. Rollenpruefung, Tenant-Isolation,
Vier-Augen-Regel, optimistische Statuspruefung, Readiness-Ausnahme, Audit und
Outbox bleiben in der vorhandenen Domaenenlogik. Die neue Adaptervalidierung
erkennt bereits vor der Mutation einen veralteten Maskenstatus, unzulaessige
Uebergaenge, fehlende Pflichtgruende und einen fehlenden Fuetterungsbeginn.

## Schreibfreiheit und Bedienweg

`validate`, `dryRun` und `propose` lesen nur den aktuellen Rationsstand und
liefern das einheitliche `MaskActionResult`. Erst `execute` ruft die Mutation
auf. Die Planung verwendet das editierbare Feld `feeding_start_input` aus der
ScreenDefinition. Beenden und Archivieren verwenden weiter den zentralen Dialog
fuer den Auditgrund; Freigeben und Aktivieren bleiben fuer Agenten
genehmigungspflichtig.

## Nachweis

`pytest -q tests/test_rations_action_runtime.py tests/test_rations_lifecycle_domain.py --no-cov --tb=short`

**10 Tests bestanden.** Geprueft wurden der ScreenDefinition-Vertrag, eine
schreibfreie Freigabevorschau, echte Service-Delegation, fehlender
Fuetterungsbeginn, veralteter Maskenstatus, Readiness-Blocker und die reine
Lifecycle-Statusmaschine.

`pytest -q tests/test_rations_action_runtime.py tests/test_mask_input_flow_contracts.py tests/test_agent_mask_contract.py --no-cov --tb=short`

**34 Tests bestanden.** Damit sind auch Human-Form-Abgrenzung und der zentrale
Agentenvertrag nach der Umstellung gruen. Zusammen sind es 38 unterschiedliche
gezielte Tests. Die Python-Kompilierung und `git diff --check` waren ebenfalls
gruen.

Architektur-Impact: ein neuer Adapterpfad im bestehenden Agrar-Router, keine
neue Domaenengrenze, Datenbanktabelle, Migration oder Runtime.
