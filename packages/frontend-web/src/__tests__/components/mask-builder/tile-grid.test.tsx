/**
 * UIX-061: TileGridRenderer + compileTiles — cockpit-Kacheln.
 */
import { describe, it, expect, vi, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { MemoryRouter } from '@/app/routing/test-router'
import { compileTiles } from '@/components/mask-builder/render-plan/schema-compiler'
import { TileGridRenderer } from '@/components/mask-builder/renderers/TileGridRenderer'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import type { RenderTilePlan } from '@/components/mask-builder/render-plan/types'

const mockNavigate = vi.fn()

vi.mock('@/app/routing/typed-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/app/routing/typed-router')>()
  return { ...actual, useNavigate: () => mockNavigate }
})

function schemaWithTiles(tiles: ScreenDefinition['tiles']): ScreenDefinition {
  return {
    schemaVersion: 1,
    id: 'workspace/fibu',
    domain: 'finance',
    mode: 'cockpit',
    title: 'FIBU-Cockpit',
    tiles,
  }
}

describe('compileTiles', () => {
  it('haengt targetFilters als Query an die aufgeloeste Route', () => {
    const plans = compileTiles(
      schemaWithTiles([
        { key: 'op', label: 'OP Debitoren', targetScreenId: 'finance/ar-open-item', targetRoute: '/finance/op-debitoren', targetFilters: { overdue: '1' }, tone: 'warning' },
      ]),
    )
    expect(plans).toHaveLength(1)
    expect(plans[0].targetPath).toBe('/finance/op-debitoren?overdue=1')
    expect(plans[0].tone).toBe('warning')
  })

  it('verwirft Kacheln ohne aufgeloeste Route (kein toter Link)', () => {
    const plans = compileTiles(
      schemaWithTiles([
        { key: 'x', label: 'Ohne Route', targetScreenId: 'foo/bar', targetFilters: {} },
      ]),
    )
    expect(plans).toHaveLength(0)
  })

  it('setzt Default-Ton neutral und laesst Route ohne Filter unveraendert', () => {
    const plans = compileTiles(
      schemaWithTiles([
        { key: 'a', label: 'A', targetScreenId: 'x', targetRoute: '/lager/bestandsuebersicht' },
      ]),
    )
    expect(plans[0].targetPath).toBe('/lager/bestandsuebersicht')
    expect(plans[0].tone).toBe('neutral')
  })
})

describe('TileGridRenderer', () => {
  beforeEach(() => mockNavigate.mockClear())

  const tiles: RenderTilePlan[] = [
    { key: 'op', label: 'Offene Posten', targetScreenId: 'finance/ar-open-item', targetPath: '/finance/op-debitoren?overdue=1', tone: 'warning' },
    { key: 'zl', label: 'Zahlungslauf', targetScreenId: 'finance/payment-run', targetPath: '/fibu/zahlungslaeufe', tone: 'danger' },
  ]

  it('rendert je Kachel eine Karte mit Ton und navigiert bei Klick', () => {
    render(
      <MemoryRouter>
        <TileGridRenderer tiles={tiles} />
      </MemoryRouter>,
    )
    const opTile = screen.getByTestId('tile-op')
    expect(opTile).toHaveAttribute('data-tone', 'warning')
    fireEvent.click(opTile)
    expect(mockNavigate).toHaveBeenCalledWith('/finance/op-debitoren?overdue=1')
  })

  it('zeigt einen Live-Zaehler wenn vorhanden', () => {
    render(
      <MemoryRouter>
        <TileGridRenderer tiles={tiles} counts={{ op: 7 }} />
      </MemoryRouter>,
    )
    expect(screen.getByText('7 offen')).toBeInTheDocument()
  })

  it('rendert nichts bei leerer Kachelliste', () => {
    const { container } = render(
      <MemoryRouter>
        <TileGridRenderer tiles={[]} />
      </MemoryRouter>,
    )
    expect(container.querySelector('[data-testid="tile-grid"]')).toBeNull()
  })
})
