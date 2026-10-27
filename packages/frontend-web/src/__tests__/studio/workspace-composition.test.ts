import { readFileSync } from 'node:fs'
import { resolve } from 'node:path'
import { describe, expect, it } from 'vitest'

import { WORKSPACE_COMPOSITION_FIXTURE } from '@/studio/workspace-composition.fixture'
import { parseWorkspaceComposition } from '@/studio/workspace-composition-parser'
import {
  isWorkspaceCompositionValid,
  normalizeWorkspaceComposition,
  validateWorkspaceComposition,
  type WorkspaceComposition,
} from '@/studio/workspace-composition'

const YAML_FIXTURE_PATH = resolve(
  __dirname,
  '../../../../../config/studio_workspace_composition.fixture.yaml',
)

describe('WorkspaceComposition Vertrag', () => {
  it('akzeptiert die kanonische Fixture ohne Issues', () => {
    const issues = validateWorkspaceComposition(WORKSPACE_COMPOSITION_FIXTURE)
    expect(issues).toEqual([])
    expect(isWorkspaceCompositionValid(WORKSPACE_COMPOSITION_FIXTURE)).toBe(true)
  })

  it('parst die Fixture-Plain-Object-Form erfolgreich', () => {
    const result = parseWorkspaceComposition(WORKSPACE_COMPOSITION_FIXTURE)
    expect(result.ok).toBe(true)
    if (!result.ok) return
    expect(result.composition.id).toBe('workspace.disposition-und-inbox')
    expect(result.composition.specializedComponents.map((s) => s.kind).sort()).toEqual([
      'disposition_board',
      'inbox',
    ])
    expect(result.composition.fachaktionRefs).toHaveLength(4)
    expect(result.composition.personalization.pinStorageKey).toBe(
      'valeo.workspace.composition.overlay',
    )
  })

  it('lehnt unbekannte specialized kind und kaputte Refs ab', () => {
    const broken: WorkspaceComposition = {
      ...WORKSPACE_COMPOSITION_FIXTURE,
      specializedComponents: [
        {
          id: 'slot-bad',
          kind: 'kanban' as WorkspaceComposition['specializedComponents'][number]['kind'],
          label: 'Falsch',
          hostViewId: 'missing-view',
          bindingId: 'x',
        },
      ],
      fachaktionRefs: [
        {
          id: 'action-orphan',
          actionKey: 'x.y',
          label: 'Orphan',
          scope: 'view',
          viewId: 'gibt-es-nicht',
        },
      ],
      defaultViewId: 'auch-nicht',
    }

    const issues = validateWorkspaceComposition(broken)
    const codes = issues.map((i) => i.code)
    expect(codes).toEqual(
      expect.arrayContaining([
        'specialized_kind',
        'specialized_host',
        'fachaktion_view',
        'default_view',
      ]),
    )
    expect(issues).toEqual(
      [...issues].sort((a, b) => a.path.localeCompare(b.path) || a.code.localeCompare(b.code)),
    )
  })

  it('lehnt Personalization ohne valeo.-Prefix ab', () => {
    const issues = validateWorkspaceComposition({
      ...WORKSPACE_COMPOSITION_FIXTURE,
      personalization: {
        ...WORKSPACE_COMPOSITION_FIXTURE.personalization,
        pinStorageKey: 'local.overlay',
      },
    })
    expect(issues.some((i) => i.code === 'personalization_prefix')).toBe(true)
  })

  it('normalisiert Reihenfolge deterministisch nach order dann id', () => {
    const shuffled: WorkspaceComposition = {
      ...WORKSPACE_COMPOSITION_FIXTURE,
      modules: [
        { id: 'documents', label: 'Belege', order: 20 },
        { id: 'logistics', label: 'Logistik', order: 10 },
      ],
      views: [
        { ...WORKSPACE_COMPOSITION_FIXTURE.views[1], order: 20 },
        { ...WORKSPACE_COMPOSITION_FIXTURE.views[0], order: 10 },
      ],
    }
    const normalized = normalizeWorkspaceComposition(shuffled)
    expect(normalized.modules.map((m) => m.id)).toEqual(['logistics', 'documents'])
    expect(normalized.views.map((v) => v.id)).toEqual(['dispo-cockpit', 'beleg-inbox-host'])
    expect(normalized.fachaktionRefs.map((a) => a.id)).toEqual(
      [...WORKSPACE_COMPOSITION_FIXTURE.fachaktionRefs.map((a) => a.id)].sort(),
    )
  })

  it('Parser meldet Root-Typfehler und Schema-Mismatch', () => {
    expect(parseWorkspaceComposition(null).ok).toBe(false)
    expect(parseWorkspaceComposition('x').issues[0]?.code).toBe('root_type')

    const badVersion = parseWorkspaceComposition({
      ...WORKSPACE_COMPOSITION_FIXTURE,
      schemaVersion: 99,
    })
    expect(badVersion.ok).toBe(false)
    expect(badVersion.issues.some((i) => i.code === 'schema_version')).toBe(true)
  })

  it('YAML-Fixture driftet nicht gegen typed Fixture (Schluesselfelder + screenIds)', () => {
    const yaml = readFileSync(YAML_FIXTURE_PATH, 'utf8')
    expect(yaml).toContain('schemaVersion: 1')
    expect(yaml).toContain(`id: ${WORKSPACE_COMPOSITION_FIXTURE.id}`)
    expect(yaml).toContain(`studioVersion: ${WORKSPACE_COMPOSITION_FIXTURE.studioVersion}`)
    expect(yaml).toContain('kind: inbox')
    expect(yaml).toContain('kind: disposition_board')
    expect(yaml).toContain(
      `pinStorageKey: ${WORKSPACE_COMPOSITION_FIXTURE.personalization.pinStorageKey}`,
    )
    expect(yaml).toContain(
      `pinnedViewsKey: ${WORKSPACE_COMPOSITION_FIXTURE.personalization.pinnedViewsKey}`,
    )
    expect(yaml).toContain(
      `fixedStartViewKey: ${WORKSPACE_COMPOSITION_FIXTURE.personalization.fixedStartViewKey}`,
    )
    for (const view of WORKSPACE_COMPOSITION_FIXTURE.views) {
      expect(yaml).toContain(`screenId: ${view.screenId}`)
      expect(yaml).toContain(`id: ${view.id}`)
    }
    for (const slot of WORKSPACE_COMPOSITION_FIXTURE.specializedComponents) {
      expect(yaml).toContain(`id: ${slot.id}`)
      expect(yaml).toContain(`kind: ${slot.kind}`)
      expect(yaml).toContain(`hostViewId: ${slot.hostViewId}`)
      if (slot.screenId) {
        expect(yaml).toContain(`screenId: ${slot.screenId}`)
      }
    }
    const viewScreenIds = new Set(WORKSPACE_COMPOSITION_FIXTURE.views.map((view) => view.screenId))
    for (const slot of WORKSPACE_COMPOSITION_FIXTURE.specializedComponents) {
      if (slot.screenId) {
        expect(viewScreenIds.has(slot.screenId)).toBe(true)
      }
    }
    for (const action of WORKSPACE_COMPOSITION_FIXTURE.fachaktionRefs) {
      expect(yaml).toContain(`actionKey: ${action.actionKey}`)
    }
  })
})
