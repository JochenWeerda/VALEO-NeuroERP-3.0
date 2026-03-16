# Wave-27 Status

## Scope
Konsistente Informationsdichte je Rolle als gemeinsamer Frontend-Contract (Gap 027)

## Zielbild

Wave 27 hebt die bisher implizite Informationsdichte aus einzelnen
Seitenentscheidungen in einen gemeinsamen Rollen-Contract. Statt lokale
`if role === ...`-Abzweigungen zu verteilen, wird jetzt zentral
aufgeloest, wie stark Toolbar, Overview, ObjectPage, ListReport und
Process-Explainability fuer fokussierte, standardisierte oder verdichtete
Rollen surfacen.

Der Contract bleibt bewusst additiv: bestehende Pattern und Wave-22/25-
Bausteine werden nicht ersetzt, sondern rollenbewusst begrenzt und
konsistent gemacht.

Im erweiterten Loop ist dieser Contract nicht auf Rollen stehengeblieben:
`tenantId`, `pageDomain`, Action-Volumen und Approval-/Detailtiefe duerfen
die Dichte jetzt kontrolliert hochziehen. Zusaetzlich wird dieser
Resolver nun aus einem produktiven Backend-Read-Model gespeist:
`/api/v1/commands/ui-density-manifest` leitet Dichtehinweise nicht nur aus
dem Command-Katalog, sondern auch aus produktiven Policy-/Approval-
Contracts ab. Damit wird Wave 27 von einer statischen Rollenmatrix zu
einem tenant-, prozess- und contract-bezogenen Surfacing-Contract.

## Lieferumfang

| AP | Zielmodul | Beschreibung | Status |
|----|-----------|--------------|--------|
| AP1 | `packages/frontend-web/src/features/role-density/role-density.ts` | Gemeinsamer Resolver fuer `focused`, `standard`, `dense` inklusive Limits fuer Toolbar, KPI-, Listen- und Prozessdetails | abgeschlossen |
| AP2 | `packages/frontend-web/src/features/role-density/role-density.ts` | Kontextanhebung fuer `tenantId`, `pageDomain`, Action-Volumen und Approval-/Detailtiefe | abgeschlossen |
| AP3 | `app/core/ui_density_manifest.py` + `app/api/v1/endpoints/command_catalog.py` | Produktives Backend-Read-Model `/api/v1/commands/ui-density-manifest`, das Dichtehinweise aus Command- sowie Policy-/Approval-Contracts zusammenfuehrt | abgeschlossen |
| AP4 | `packages/frontend-web/src/lib/api/ui-density-manifest.ts` + `packages/frontend-web/src/components/navigation/PageToolbar.tsx` | Frontend-Read-Model fuer das Backend-Manifest; Pattern koennen einen backend-gespeisten `densityProfileOverride` an `PageToolbar` geben | abgeschlossen |
| AP5 | `packages/frontend-web/src/components/patterns/OverviewPage.tsx` + `ObjectPage.tsx` + `ListReport.tsx` + `Wizard.tsx` | Pattern-Komponenten konsumieren denselben Contract fuer KPI-/Chart-/Listen-Surfacing, Key-Info, Section-Badges, Filterdichte und Wizard-Beschreibung | abgeschlossen |
| AP6 | `packages/frontend-web/src/components/workflow/ProcessStatusPanel.tsx` + `packages/frontend-web/src/features/workflow/APInvoiceApprovalPanel.tsx` + `packages/frontend-web/src/features/workflow/useApprovalDensityProfile.ts` | Explainability-Panel begrenzt oder erweitert Detailtiefe konsistent nach Rollen-, Tenant- und Approval-Kontext; AP, Closing, USTVA, Zahlungslauf, Lastschriften und Settlement-Preview nutzen dafuer denselben backend-gespeisten Manifest-Contract | abgeschlossen |
| AP7 | `packages/frontend-web/src/components/workflow/CompactDecisionCard.tsx` + `packages/frontend-web/src/pages/finance/ap-invoices-list.tsx` + `packages/frontend-web/src/pages/annahme/abrechnung.tsx` + `packages/frontend-web/src/pages/policy-manager.tsx` + `packages/frontend-web/src/policy/PolicyBadge.tsx` | Nicht-panelbasierte Explainability-Surfacings nutzen dieselbe Dichte- und Manifest-Logik fuer Listenzeilen, kompakte Statuskarten und Policy-Badges statt lokaler Inline-Renderings | abgeschlossen |
| AP8 | `tests/test_process_kernel_wave27_ui_density_manifest.py` + `packages/frontend-web/src/__tests__/features/role-density/role-density.test.ts` + `packages/frontend-web/src/__tests__/components/navigation/PageToolbar.role-density.test.tsx` + `packages/frontend-web/src/__tests__/components/workflow/ProcessStatusPanel.test.tsx` + `packages/frontend-web/src/__tests__/components/workflow/CompactDecisionCard.test.tsx` + `packages/frontend-web/src/__tests__/components/patterns/Wizard.test.tsx` | Backend-Contract- und Frontend-UI-Tests fuer Manifest, Rollenauflosung, Kontext-Bumps und sichtbare Dichtewirkung | abgeschlossen |

## Abnahmekriterien

- Rollen werden deterministisch auf `focused`, `standard` oder `dense` aufgeloest
- Tenant-, Domain-, Approval- und Action-Kontext duerfen die Dichte kontrolliert hochziehen
- Das Frontend kann Dichtehinweise aus produktiven Backend-Command- sowie Policy-/Approval-Contracts beziehen
- AP, Closing, USTVA, Zahlungslauf, Lastschriften und Settlement-Preview nutzen denselben Manifestpfad statt lokaler Einzel-Bumps
- Auch Listenzeilen, kompakte Statuskarten und Policy-Badges nutzen denselben Resolver statt eigener Inline-Layouts
- Toolbar-Actions kippen bei fokussierten Rollen kontrolliert ins Overflow statt unstrukturiert zu wachsen
- Overview-, List- und Object-Patterns surfacen dieselbe Dichte-Logik statt seitenweiser Sonderregeln
- Process-Explainability zeigt fuer fokussierte Rollen nur die wesentlichen Details, ohne Admin-/Manager-Ansichten zu verflachen
- Keine neuen parallelen Rollenentscheidungen in einzelnen Pattern-Komponenten

## Tests

| Datei | Tests | Scope |
|-------|-------|-------|
| `tests/test_process_kernel_wave27_ui_density_manifest.py` | 4 | Backend-Manifest aus Command-, Policy- und Approval-Contracts, Domain-Mapping und Endpoint-Schema |
| `packages/frontend-web/src/__tests__/features/role-density/role-density.test.ts` | 6 | Rollenauflosung, Tenant-/Finance-/Approval-Bumps, backend-gespeistes Mindestniveau und Toolbar-Merging |
| `packages/frontend-web/src/__tests__/components/navigation/PageToolbar.role-density.test.tsx` | 2 | Fokussierte Rollen sehen nur zwei Primary-Actions; Finance-/Tenant-Kontext hebt auf mehr sichtbare Actions an |
| `packages/frontend-web/src/__tests__/components/workflow/ProcessStatusPanel.test.tsx` | 3 | ProcessStatusPanel begrenzt bzw. erweitert Detailtiefe nach Rolle und Approval-/Finance-Kontext |
| `packages/frontend-web/src/__tests__/components/workflow/CompactDecisionCard.test.tsx` | 2 | Kompakte Explainability-Surfacings begrenzen Details fuer einfache Rollen und ziehen ueber Manifest-Domains auf volle Sicht hoch |
| `packages/frontend-web/src/__tests__/components/patterns/Wizard.test.tsx` | 4 | Wizard bleibt unter dem erweiterten Dichte-Contract stabil |

**Gesamt Wave 27: 21 Tests gruen**

## Gap geschlossen

| Gap-ID | Beschreibung | Massnahme |
|--------|-------------|-----------|
| Gap 027 | Konsistente Informationsdichte je Rolle | Gemeinsamer Rollen-, Tenant-, Prozess- und Backend-Contract-Density-Contract fuer Toolbar, Pattern-Komponenten und Prozessstatus statt lokaler Einzelentscheidungen |

## Status
`abgeschlossen` - 2026-03-15 - Rollen-/Tenant-/Prozess-Density-Resolver, backend-gespeistes Command- plus Policy-/Approval-Manifest sowie Manifest-Anbindung fuer Panels und kompakte Explainability-Surfacings gruen
