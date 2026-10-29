import { describe, expect, it } from 'vitest'
import { renderHook } from '@testing-library/react'
import {
  WORKSPACE_FACHAKTIONEN,
  detectSeason,
  emptyUserContext,
  noopRankingAdvisor,
  orderLaunchpadTileIds,
  rankWorkspaceItems,
  useRankingAdvisor,
  type RankingAdvisor,
  type TypedFachaktion,
  type WorkspaceSignal,
} from '@/workspace'

const harvestNoon = new Date('2026-08-12T12:00:00')

function actionById(id: string): TypedFachaktion {
  const found = WORKSPACE_FACHAKTIONEN.find((action) => action.id === id)
  if (!found) {
    throw new Error(`missing action ${id}`)
  }
  return found
}

describe('workspace prioritization', () => {
  it('hebt ueberfaellige Freigaben ueber Navigation und nennt Reason-Codes', () => {
    const signals: WorkspaceSignal[] = [
      {
        id: 'sig-overdue-invoices',
        kind: 'deadline',
        layer: 'proactive',
        relatedActionIds: ['finance.invoices-awaiting-my-approval'],
        severity: 5,
        source: 'approval-worklist',
        dueAt: '2026-08-01',
        count: 4,
      },
      {
        id: 'sig-harvest-queue',
        kind: 'season',
        layer: 'situational',
        relatedActionIds: ['harvest.intake-queue'],
        severity: 2,
        source: 'calendar',
        season: 'harvest',
        dayPart: 'midday',
      },
    ]

    const ranked = rankWorkspaceItems({
      actions: [
        actionById('finance.invoices-awaiting-my-approval'),
        actionById('harvest.intake-queue'),
        actionById('workspace.document-inbox'),
      ],
      context: emptyUserContext({
        scopes: ['finance:read', 'logistics:read', 'dms:read'],
        roles: ['buchhalter'],
      }),
      signals,
      now: harvestNoon,
    })

    expect(ranked.map((item) => item.action.id)).toEqual([
      'finance.invoices-awaiting-my-approval',
      'harvest.intake-queue',
      'workspace.document-inbox',
    ])
    expect(ranked[0]?.reasonCodes).toEqual(
      expect.arrayContaining(['overdue', 'severity:5', 'layer:proactive', 'role:finance']),
    )
    expect(ranked[1]?.reasonCodes).toEqual(expect.arrayContaining(['season:harvest', 'day:midday']))
  })

  it('filtert Aktionen ohne Scope und laesst Pins vor saisonalen Kacheln stehen', () => {
    const ranked = rankWorkspaceItems({
      actions: WORKSPACE_FACHAKTIONEN,
      context: emptyUserContext({
        scopes: ['logistics:read', 'dms:read'],
        pinned: ['workspace.document-inbox'],
      }),
      signals: [
        {
          id: 'sig-harvest',
          kind: 'season',
          layer: 'situational',
          relatedActionIds: ['harvest.intake-queue', 'logistics.undispatched-truck-orders'],
          severity: 3,
          source: 'calendar',
          season: 'harvest',
        },
      ],
      now: harvestNoon,
    })

    expect(ranked.every((item) =>
      item.action.requiredScopes.length === 0 ||
      item.action.requiredScopes.some((scope) => ['logistics:read', 'dms:read'].includes(scope)),
    )).toBe(true)
    expect(ranked.some((item) => item.action.id === 'finance.invoices-awaiting-my-approval')).toBe(false)
    expect(ranked[0]?.action.id).toBe('workspace.document-inbox')
    expect(ranked[0]?.reasonCodes).toContain('pinned')
  })

  it('behaelt bei fixierter Oberflaeche die Katalogordnung hinter den Pins', () => {
    const ordered = orderLaunchpadTileIds(
      ['a', 'b', 'c'],
      ['c', 'a'],
      { pinned: ['b'], surfaceLocked: true },
    )
    expect(ordered).toEqual(['b', 'a', 'c'])
  })

  it('sortiert ohne Fixierung nach Rang, Pins zuerst, und der KI-Hook bleibt optional', () => {
    expect(detectSeason(harvestNoon)).toBe('harvest')
    const reverse: RankingAdvisor = (items) => [...items].reverse()
    const ranked = rankWorkspaceItems({
      actions: [
        actionById('workspace.document-inbox'),
        actionById('harvest.intake-queue'),
      ],
      context: emptyUserContext({ scopes: ['dms:read', 'logistics:read'] }),
      signals: [],
      now: harvestNoon,
      advisor: reverse,
    })
    expect(noopRankingAdvisor(ranked)).toBe(ranked)
    expect(ranked.map((item) => item.action.id)).toEqual([
      'workspace.document-inbox',
      'harvest.intake-queue',
    ])
  })

  it('liefert useRankingAdvisor den noop-Default und akzeptiert Override', () => {
    const { result: defaultAdvisor } = renderHook(() => useRankingAdvisor())
    expect(defaultAdvisor.current).toBe(noopRankingAdvisor)

    const reverse: RankingAdvisor = (items) => [...items].reverse()
    const { result: overridden } = renderHook(() => useRankingAdvisor(reverse))
    const sample = rankWorkspaceItems({
      actions: [
        actionById('workspace.document-inbox'),
        actionById('harvest.intake-queue'),
      ],
      context: emptyUserContext({ scopes: ['dms:read', 'logistics:read'] }),
      signals: [],
      now: harvestNoon,
      advisor: overridden.current,
    })
    expect(sample.map((item) => item.action.id)).toEqual([
      'workspace.document-inbox',
      'harvest.intake-queue',
    ])
  })
})
