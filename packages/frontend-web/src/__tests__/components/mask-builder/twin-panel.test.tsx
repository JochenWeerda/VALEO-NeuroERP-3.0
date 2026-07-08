/**
 * UIX-081: Twin-Panel Geometrie-Parser + Farblogik + Renderer.
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import {
  parseTwinPlan,
  shapeToPath,
  cellStyle,
  keyboardOrder,
  type TwinMetricDef,
  type TwinPlan,
} from '@/components/mask-builder/renderers/twin-geometry'
import { TwinPanelRenderer } from '@/components/mask-builder/renderers/TwinPanelRenderer'

const METRICS: TwinMetricDef[] = [
  { key: 'fill_pct', label: 'Fuellstand', kind: 'percent' },
  { key: 'moisture', label: 'Feuchte', kind: 'number', warnAbove: 14.5 },
  { key: 'locked', label: 'Gesperrt', kind: 'flag' },
  { key: 'qs_status', label: 'QS', kind: 'status' },
]

describe('parseTwinPlan', () => {
  it('parst rect + polygon, verwirft fehlerhafte Zellen mit Fehlermeldung', () => {
    const { plan, errors } = parseTwinPlan({
      plan_id: 'p1',
      canvas: { width: 100, height: 100 },
      cells: [
        { id: 'a', shape: { kind: 'rect', x: 0, y: 0, w: 10, h: 10 } },
        { id: 'b', shape: { kind: 'polygon', points: [[0, 0], [10, 0], [10, 10]] } },
        { id: 'c', shape: { kind: 'rect', x: 0, y: 0, w: -5, h: 10 } }, // ungueltig
        { id: 'd', shape: { kind: 'kreis' } }, // unbekannt
        { shape: { kind: 'rect', x: 0, y: 0, w: 1, h: 1 } }, // id fehlt
      ],
    })
    expect(plan).not.toBeNull()
    expect(plan!.cells.map((c) => c.id)).toEqual(['a', 'b'])
    expect(errors.length).toBe(3)
  })

  it('gibt null-Plan bei fehlendem canvas', () => {
    const { plan, errors } = parseTwinPlan({ plan_id: 'p', cells: [] })
    expect(plan).toBeNull()
    expect(errors).toContain('canvas.width/height fehlt')
  })

  it('meldet doppelte Zellen-ids', () => {
    const { plan, errors } = parseTwinPlan({
      plan_id: 'p', canvas: { width: 10, height: 10 },
      cells: [
        { id: 'x', shape: { kind: 'rect', x: 0, y: 0, w: 1, h: 1 } },
        { id: 'x', shape: { kind: 'rect', x: 1, y: 1, w: 1, h: 1 } },
      ],
    })
    expect(plan!.cells).toHaveLength(1)
    expect(errors.some((e) => e.includes('doppelte id'))).toBe(true)
  })
})

describe('shapeToPath', () => {
  it('rect → geschlossener Pfad', () => {
    expect(shapeToPath({ kind: 'rect', x: 5, y: 10, w: 20, h: 30 })).toBe('M 5 10 h 20 v 30 h -20 Z')
  })
  it('polygon → geschlossener Pfad', () => {
    expect(shapeToPath({ kind: 'polygon', points: [[0, 0], [10, 0], [10, 10]] })).toBe('M 0 0 L 10 0 L 10 10 Z')
  })
})

describe('cellStyle — Metrik-Farblogik', () => {
  it('Fuellstand faerbt Gold; hoeherer Fuellstand → sattere Farbe', () => {
    const low = cellStyle(METRICS, { fill_pct: 10 }).fill
    const high = cellStyle(METRICS, { fill_pct: 90 }).fill
    expect(low).not.toBe(high)
  })
  it('warnAbove-Ueberschreitung → danger-Kontur', () => {
    const ok = cellStyle(METRICS, { moisture: 13 })
    const warn = cellStyle(METRICS, { moisture: 15 })
    expect(warn.stroke).toBe('#dc2626')
    expect(warn.strokeWidth).toBeGreaterThan(ok.strokeWidth)
  })
  it('locked=true → Schraffur', () => {
    expect(cellStyle(METRICS, { locked: true }).hatched).toBe(true)
    expect(cellStyle(METRICS, { locked: false }).hatched).toBe(false)
  })
})

describe('keyboardOrder', () => {
  it('stabile Sortierung nach id', () => {
    expect(keyboardOrder([{ id: 'b', shape: { kind: 'rect', x: 0, y: 0, w: 1, h: 1 } }, { id: 'a', shape: { kind: 'rect', x: 0, y: 0, w: 1, h: 1 } }])).toEqual(['a', 'b'])
  })
})

describe('TwinPanelRenderer', () => {
  const plan: TwinPlan = {
    plan_id: 'emden',
    canvas: { width: 400, height: 300 },
    cells: [
      { id: 'S1-Z01', label: 'Silo 1', shape: { kind: 'rect', x: 10, y: 10, w: 40, h: 60 } },
      { id: 'S1-Z02', shape: { kind: 'polygon', points: [[80, 10], [120, 10], [120, 70]] } },
    ],
  }

  it('rendert je Zelle einen Pfad und aktiviert bei Klick (Durchstich)', () => {
    const onActivate = vi.fn()
    render(<TwinPanelRenderer plan={plan} metrics={METRICS} cellData={{ 'S1-Z01': { fill_pct: 80, locked: true } }} onCellActivate={onActivate} updatedLabel="10:41:20" />)
    expect(screen.getByTestId('twin-cell-S1-Z01')).toBeInTheDocument()
    expect(screen.getByTestId('twin-updated')).toHaveTextContent('10:41:20')
    fireEvent.click(screen.getByTestId('twin-cell-S1-Z01'))
    expect(onActivate).toHaveBeenCalledWith('S1-Z01')
  })

  it('Enter auf fokussierter Zelle loest Durchstich aus (Tastatur)', () => {
    const onActivate = vi.fn()
    render(<TwinPanelRenderer plan={plan} metrics={METRICS} cellData={{}} onCellActivate={onActivate} />)
    fireEvent.keyDown(screen.getByTestId('twin-cell-S1-Z02'), { key: 'Enter' })
    expect(onActivate).toHaveBeenCalledWith('S1-Z02')
  })

  it('gesperrte Zelle erhaelt Schraffur-Markierung', () => {
    render(<TwinPanelRenderer plan={plan} metrics={METRICS} cellData={{ 'S1-Z01': { locked: true } }} onCellActivate={vi.fn()} />)
    expect(screen.getByTestId('twin-cell-S1-Z01')).toHaveAttribute('data-hatched', 'true')
  })
})
