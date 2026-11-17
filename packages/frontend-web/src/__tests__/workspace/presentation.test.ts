import { describe, expect, it } from 'vitest'
import { groupWorkspaceItems, workspaceActionHint, workspaceActionLabel } from '@/workspace/presentation'
import { WORKSPACE_FACHAKTIONEN } from '@/workspace/registry'

describe('workspace human presentation', () => {
  it('keeps business references, replaces technical UUID prefixes only', () => {
    expect(workspaceActionLabel('019c0004-0000-7000-8000-000000000001: Waage')).toBe('Kontrakt · Waage')
    expect(workspaceActionLabel('K-2026-17: Waage')).toBe('K-2026-17: Waage')
  })
  it('groups repeated task labels while preserving every distinct target', () => {
    const actions = ['000001', '000002'].map(suffix => ({
      action: { ...WORKSPACE_FACHAKTIONEN[0], id: suffix, businessDomain: 'agrar', label: `019c0004-0000-7000-8000-000000${suffix}: Waage`, target: { route: `/waage?contract=${suffix}` } },
      score: 1, reasonCodes: [],
    }))
    const grouped = groupWorkspaceItems(actions)
    expect(grouped).toHaveLength(1)
    expect(grouped[0].map(item => item.action.target.route)).toEqual(['/waage?contract=000001', '/waage?contract=000002'])
  })
  it('explains priority without exposing ranking diagnostics or mutating the action', () => {
    const item = { action: WORKSPACE_FACHAKTIONEN[0], score: 3, reasonCodes: ['layer:situational', 'severity:3', 'overdue'] }
    expect(workspaceActionHint(item)).toBe('Überfällig – bitte prüfen')
    expect(item.reasonCodes).toEqual(['layer:situational', 'severity:3', 'overdue'])
  })
})
