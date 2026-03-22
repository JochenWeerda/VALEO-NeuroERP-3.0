# Wave 98 — Agent-Rollout Stufen 1–4 (Gap-Close, Capability-Pages, Keyboard-Rollout, QS)

**Status:** ABGESCHLOSSEN
**Datum:** 2026-03-20
**TypeScript:** 0 Fehler

## Stufe 1 — Rollout-Gaps schließen

### `pages/einkauf/bestellvorschlag-lager.tsx`
- `AgentSuggestionBadge<{ lieferant?: string; menge?: number }>` hinzugefügt
- capabilityKey: `bestellvorschlag_assistant`
- Parameter: `artikel_id`, `artikel_nr`, `bezeichnung` aus selectedArtikel
- `onAccept`: Übernahme von Lieferant + Menge in Eingabe-Zeile
- Nur sichtbar wenn Artikel ausgewählt (`selectedArtikel != null`)

### `app/route-aliases.json`
- +4 neue Einträge: `finance/skonto-optimizer`, `workflows/supervisor`, `admin/data-quality`, `qualitaet/ausnahmen`

## Stufe 2 — Neue Capability-Seiten

### `pages/admin/data-quality.tsx` (erweitert)
- `AgentProcessPanel domain="stammdaten"` nach Seitentitel
- `AgentSuggestionBadge<ExceptionSuggestion>` nach Validierungslauf (nur wenn Verstöße > 0)
- capabilityKey: `data_quality_assistant`
- Parameter: entity_types (Liste), total_violations

### `pages/qualitaet/ausnahmen.tsx` (NEU)
- Betriebs-Ausnahmen-Liste: `GET /api/v1/operations/exceptions`
- `AgentProcessPanel domain="operations"` nach Header
- `AgentSuggestionBadge<ExceptionSuggestion>` bei hochprio > 0
- capabilityKey: `operations_exception_assistant`
- Parameter: offen_count, eskaliert_count, hochprio_count, ausnahmen_ids
- Stats-Cards: Gesamt, Offen, Eskaliert, Hohe Priorität
- DataTable mit Prioritäts-Badge + Status-Icon (Eskaliert=rot, Offen=orange, Geschlossen=grün)
- Keyboard: Ctrl+N → /qualitaet/ausnahme-neu, F5 → refetch
- `KeyboardShortcutBar` + Wrapper-Pattern

### Nav-Eintrag in `domains/operations.tsx`
- Neuer Eintrag `ausnahmen` in der Compliance-Sektion:
  - Label: "Betriebs-Ausnahmen (KI)"
  - Icon: AlertCircle
  - keywords: ausnahmen, eskalation, exception, ki, agent, priorisierung

## Stufe 3 — Keyboard-Rollout (5 Seiten)

### `pages/compliance/sachkunde-register.tsx`
- `useRef` + `searchRef` auf Search-Input
- `buildCoreMaskShortcuts({ onNew, onSearch, onRefresh })`
- Ctrl+N → `/compliance/sachkunde-neu`, Ctrl+F → focus searchRef, F5 → refetch
- Wrapper-Pattern + `KeyboardShortcutBar`

### `pages/compliance/zulassungen-register.tsx`
- `useRef` + `searchRef` auf Search-Input
- `buildCoreMaskShortcuts({ onSearch, onRefresh })`
- Ctrl+F → focus searchRef, F5 → refetch
- Wrapper-Pattern + `KeyboardShortcutBar`

### `pages/compliance/vvvo-register.tsx`
- `useRef` + `searchRef` auf Search-Input
- `buildCoreMaskShortcuts({ onNew, onSearch, onRefresh })`
- Ctrl+N → `/compliance/vvvo-neu`, Ctrl+F → focus searchRef, F5 → refetch
- Wrapper-Pattern + `KeyboardShortcutBar`

### `pages/compliance/enni-meldungen.tsx`
- `buildCoreMaskShortcuts({ onNew, onRefresh })`
- Ctrl+N → `/compliance/enni-neu`, F5 → refetch
- Wrapper-Pattern + `KeyboardShortcutBar`

### `pages/verkauf/kunden-liste.tsx`
- `useRef` + `searchRef` auf Search-Input
- `buildCoreMaskShortcuts({ onNew, onSearch, onRefresh })`
- Ctrl+N → `/verkauf/kunde/neu`, Ctrl+F → focus searchRef, F5 → refetch
- Wrapper-Pattern + `KeyboardShortcutBar`

## Stufe 4 — QS / Bugfix

### `domains/finance.tsx`
- Doppeltes `Zap`-Import entfernt (war durch Wave 96 entstanden → TS2300 behoben)

## Agentic Workflow Rollout-Stand nach Wave 98

| Domäne | Seite | Agent-Panel | Agent-Suggestion | Keyboard |
|--------|-------|-------------|------------------|----------|
| Einkauf | bestellvorschlag-lager.tsx | ✓ einkauf | ✓ bestellvorschlag_assistant | ✓ |
| Finance | skonto-optimizer.tsx | ✓ finanzen | ✓ skonto_optimizer | ✓ |
| Stammdaten | admin/data-quality.tsx | ✓ stammdaten | ✓ data_quality_assistant | — |
| Operations | qualitaet/ausnahmen.tsx | ✓ operations | ✓ operations_exception_assistant | ✓ |
| Compliance | qs-checkliste.tsx | ✓ compliance | — | ✓ |
| Compliance | cross-compliance.tsx | ✓ compliance | — | ✓ |
| Compliance | meldewesen-konsole.tsx | ✓ compliance | — | ✓ |
| Compliance | sachkunde-register.tsx | — | — | ✓ |
| Compliance | zulassungen-register.tsx | — | — | ✓ |
| Compliance | vvvo-register.tsx | — | — | ✓ |
| Compliance | enni-meldungen.tsx | — | — | ✓ |
| Verkauf | kunden-liste.tsx | — | — | ✓ |
| Lager | einlagerung.tsx | ✓ | ✓ einlagerung_assistant | ✓ |
| Lager | auslagerung.tsx | ✓ | ✓ auslagerung_assistant | ✓ |
| Annahme | rohware.tsx | ✓ | ✓ rohware_annahme_assistant | ✓ |
| Verladung | lkw-beladung.tsx | ✓ lager | — | ✓ |
| Workflows | supervisor.tsx | ✓ all | — | ✓ |

## Capability-Abdeckung (alle 8 registrierten Capabilities)

| Capability | Readiness | Seite mit Suggestion-Badge |
|------------|-----------|---------------------------|
| bestellvorschlag_assistant | productive | bestellvorschlag-lager.tsx ✓ |
| rohware_annahme_assistant | assisted | rohware.tsx ✓ |
| auslagerung_assistant | assisted | auslagerung.tsx ✓ |
| einlagerung_assistant | assisted | einlagerung.tsx ✓ |
| skonto_optimizer | productive | skonto-optimizer.tsx ✓ |
| compliance_copilot | productive | (via AgentProcessPanel) |
| data_quality_assistant | assisted | admin/data-quality.tsx ✓ |
| operations_exception_assistant | assisted | qualitaet/ausnahmen.tsx ✓ |

**Alle 8 Capabilities haben mindestens eine UI-Anlaufstelle.**
