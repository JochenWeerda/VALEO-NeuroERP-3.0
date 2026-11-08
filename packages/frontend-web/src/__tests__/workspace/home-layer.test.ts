import { describe, expect, it, vi } from 'vitest'
import type { LaunchpadSpace } from '@/app/navigation/launchpad-spaces'
import type { InboxQueueItem } from '@/components/adaptive-workspace/inbox'
import { SPECIALIZED_COMPONENT_KINDS } from '@/studio/workspace-composition'
import {
  DISPOSITION_BOARD_SLOT,
  INBOX_SLOT,
  defaultHomeSignals,
  openInboxItemInMask,
  prioritizeLaunchpadSpaces,
  rankedLaunchpadTileIds,
} from '@/workspace'

const spaces: LaunchpadSpace[] = [
  {
    id: 'ernte',
    label: 'Ernte',
    pages: [
      {
        id: 'waage',
        label: 'Waage',
        origin: 'catalog',
        locked: true,
        tiles: [
          { id: 'wiegungen', label: 'Wiegungen', path: '/waage/wiegungen' },
          { id: 'warteschlange', label: 'Warteschlange', path: '/annahme/warteschlange' },
        ],
      },
    ],
  },
]

describe('home signals and launchpad priority', () => {
  it('erzeugt nur Kalender-Signale ohne erfundene Zaehler', () => {
    const signals = defaultHomeSignals(new Date('2026-08-12T08:00:00'))
    expect(signals.every((signal) => signal.source === 'calendar' || signal.source === 'clock')).toBe(true)
    expect(signals.every((signal) => signal.count === undefined)).toBe(true)
    expect(signals[0]?.relatedActionIds).toContain('harvest.intake-queue')
    expect(signals[0]?.reasonCodes).toEqual(
      expect.arrayContaining(['cal:season:harvest', 'layer:situational']),
    )
    expect(signals[0]?.layer).toBe('situational')
  })

  it('stuft reine Proactive-Kalenderquellen als proactive mit reasonCodes ein', () => {
    const planting = defaultHomeSignals(new Date('2026-04-15T18:30:00'))
    expect(planting.find((s) => s.id === 'cal-season')).toMatchObject({
      layer: 'proactive',
      relatedActionIds: ['agrar.overdue-contracts'],
    })
    expect(planting.find((s) => s.id === 'cal-season')?.reasonCodes).toEqual(
      expect.arrayContaining(['cal:season:planting', 'layer:proactive']),
    )
    expect(planting.find((s) => s.id === 'cal-daypart')).toMatchObject({
      layer: 'proactive',
      relatedActionIds: ['finance.invoices-awaiting-my-approval'],
    })
    expect(planting.find((s) => s.id === 'cal-daypart')?.reasonCodes).toEqual(
      expect.arrayContaining(['cal:day:evening', 'layer:proactive']),
    )

    const afternoon = defaultHomeSignals(new Date('2026-08-12T15:00:00'))
    expect(afternoon.find((s) => s.id === 'cal-daypart')).toMatchObject({
      layer: 'proactive',
      relatedActionIds: ['logistics.undispatched-truck-orders'],
    })
  })

  it('liefert Launchpad-IDs und Fachaktions-IDs fuer denselben Rang', () => {
    expect(
      rankedLaunchpadTileIds([{ id: 'harvest.intake-queue', launchpadTileId: 'warteschlange' }]),
    ).toEqual(['warteschlange', 'harvest.intake-queue'])
  })

  it('hebt gerankte und gepinnte Kacheln, bis die Oberflaeche fixiert ist', () => {
    const ranked = rankedLaunchpadTileIds([
      { id: 'harvest.intake-queue', launchpadTileId: 'warteschlange' },
    ])
    const open = prioritizeLaunchpadSpaces(spaces, ranked, { pinned: [], surfaceLocked: false })
    expect(open[0]?.pages[0]?.tiles.map((tile) => tile.id)).toEqual(['warteschlange', 'wiegungen'])

    const locked = prioritizeLaunchpadSpaces(spaces, ranked, {
      pinned: ['wiegungen'],
      surfaceLocked: true,
    })
    expect(locked[0]?.pages[0]?.tiles.map((tile) => tile.id)).toEqual(['wiegungen', 'warteschlange'])
  })

  it('konsumiert Studio-Kinds und oeffnet die Belegmaske ohne Prefill-Umgehung', () => {
    expect(SPECIALIZED_COMPONENT_KINDS).toEqual(expect.arrayContaining([INBOX_SLOT.kind, DISPOSITION_BOARD_SLOT.kind]))
    expect(INBOX_SLOT.queueEndpoint).toBe('/api/mcp/documents/inbox/queue')
    expect(DISPOSITION_BOARD_SLOT).toMatchObject({
      kind: 'disposition_board',
      id: 'lkw-disposition-board',
      route: '/disposition/touren-disposition',
      screenId: 'disposition/touren-disposition',
    })

    const withoutKind = vi.fn()
    openInboxItemInMask(
      {
        id: 'INBOX-1',
        can_open: true,
        proposal: { target_route: '/einkauf/rechnung-eingang-erfassung' },
        actions: [{ key: 'open_mask', href: '/einkauf/rechnung-eingang-erfassung', enabled: true }],
      } as InboxQueueItem,
      withoutKind,
    )
    expect(withoutKind).not.toHaveBeenCalled()

    const navigate = vi.fn()
    openInboxItemInMask(
      {
        id: 'INBOX-1',
        can_open: true,
        proposal: {
          document_kind: 'EINGANGSRECHNUNG',
          target_route: '/einkauf/rechnung-eingang-erfassung',
        },
        actions: [{ key: 'open_mask', href: '/einkauf/rechnung-eingang-erfassung', enabled: true }],
      } as InboxQueueItem,
      navigate,
    )
    expect(navigate).toHaveBeenCalledTimes(1)
    expect(navigate).toHaveBeenCalledWith('/belege/purchase_invoice/neu?inbox=INBOX-1')
  })
})
