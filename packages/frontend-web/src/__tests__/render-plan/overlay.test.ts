/**
 * UIX-071: applyOverlay — Allowlist, Merge, Drift, Hash.
 */
import { describe, it, expect } from 'vitest'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { applyOverlay, hashOverlay, NON_OVERLAYABLE_KEYS } from '@/components/mask-builder/render-plan/overlay'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const SD: ScreenDefinition = {
  schemaVersion: 1,
  id: 'finance/ar-open-item',
  domain: 'finance',
  mode: 'list',
  title: 'Offene Posten',
  tables: [
    {
      key: 'op',
      label: 'Offene Posten',
      dataSourceKey: 'op',
      columns: [
        { key: 'nr', label: 'Nr', sortable: true, filterable: true },
        { key: 'kunde', label: 'Kunde', filterable: true },
        { key: 'betrag', label: 'Betrag', numeric: true, sortable: true },
        { key: 'faellig', label: 'Faellig', renderKind: 'date', sortable: true },
      ],
    },
  ],
}

function plan() {
  return compileRenderPlanFromScreenDefinition(SD)
}

describe('applyOverlay — Allowlist (Sicherheit)', () => {
  it('verwirft nicht-overlaybare Keys und meldet sie als violations', () => {
    const result = applyOverlay(plan(), {
      // @ts-expect-error absichtlich verbotene Felder
      actions: [{ key: 'delete' }],
      dangerLevel: 'safe',
      floorplan: 'worklist',
      density: 'expertDense',
    })
    expect(result.violations).toEqual(expect.arrayContaining(['actions', 'dangerLevel', 'floorplan']))
    // erlaubtes Feld wird angewendet
    expect(result.plan.shell.density).toBe('expertDense')
  })

  it('kein NON_OVERLAYABLE-Key wird jemals angewendet', () => {
    const overlay = Object.fromEntries(NON_OVERLAYABLE_KEYS.map((k) => [k, 'x'])) as Record<string, unknown>
    const before = plan()
    const result = applyOverlay(before, overlay)
    expect(result.violations.sort()).toEqual([...NON_OVERLAYABLE_KEYS].sort())
    // Plan-Sicherheitsfelder unveraendert
    expect(result.plan.shell.floorplan).toBe(before.shell.floorplan)
    expect(result.plan.shell.tableProfile).toBe(before.shell.tableProfile)
    expect(result.plan.actions).toEqual(before.actions)
  })
})

describe('applyOverlay — Tabellen-Merge', () => {
  it('reihenfolge + sichtbarkeit ueber visibleColumns', () => {
    const result = applyOverlay(plan(), { tables: { op: { visibleColumns: ['kunde', 'nr'] } } })
    expect(result.plan.tablesByKey.op.columns.map((c) => c.key)).toEqual(['kunde', 'nr'])
    expect(result.plan.tablesByKey.op.availableColumns?.map((c) => c.key)).toEqual(['nr', 'kunde', 'betrag', 'faellig'])
    expect(result.violations).toEqual([])
  })

  it('columnWidths setzt Breiten; activeVariant/customVariants werden uebernommen', () => {
    const result = applyOverlay(plan(), {
      tables: {
        op: {
          columnWidths: { kunde: 240 },
          activeVariant: 'meine',
          customVariants: [{ key: 'meine', label: 'Meine Sicht', filters: { status: 'offen' } }],
        },
      },
    })
    const col = result.plan.tablesByKey.op.columns.find((c) => c.key === 'kunde')
    expect(col?.width).toBe(240)
    expect(result.plan.tablesByKey.op.activeVariant).toBe('meine')
    expect(result.plan.tablesByKey.op.customVariants?.[0].key).toBe('meine')
  })

  it('unbekannte Tabelle/Spalte → invalidPaths (Drift), kein Fehler', () => {
    const result = applyOverlay(plan(), {
      tables: { gibtsnicht: { visibleColumns: ['x'] }, op: { visibleColumns: ['nr', 'fantasie'] } },
    })
    expect(result.invalidPaths).toEqual(expect.arrayContaining(['tables.gibtsnicht', 'tables.op.visibleColumns.fantasie']))
    // gueltige Spalte bleibt angewendet
    expect(result.plan.tablesByKey.op.columns.map((c) => c.key)).toEqual(['nr'])
    expect(result.plan.overlayInvalidPaths).toBeDefined()
  })

  it('mutiert den Eingabe-Plan nicht', () => {
    const before = plan()
    const originalOrder = before.tablesByKey.op.columns.map((c) => c.key)
    applyOverlay(before, { tables: { op: { visibleColumns: ['betrag'] } } })
    expect(before.tablesByKey.op.columns.map((c) => c.key)).toEqual(originalOrder)
  })
})

describe('applyOverlay — leeres/ungueltiges Overlay', () => {
  it('null-Overlay gibt den Plan unveraendert zurueck', () => {
    const before = plan()
    const result = applyOverlay(before, null)
    expect(result.plan).toBe(before)
    expect(result.violations).toEqual([])
  })

  it('ungueltige density → invalidPaths, keine Anwendung', () => {
    // @ts-expect-error absichtlich ungueltiger Wert
    const result = applyOverlay(plan(), { density: 'riesig' })
    expect(result.invalidPaths.some((p) => p.startsWith('density:'))).toBe(true)
  })
})

describe('hashOverlay', () => {
  it('ist stabil gegenueber Schluessel-Reihenfolge', () => {
    expect(hashOverlay({ density: 'compact', tileOrder: ['a', 'b'] })).toBe(
      hashOverlay({ tileOrder: ['a', 'b'], density: 'compact' }),
    )
  })

  it('unterscheidet verschiedene Overlays', () => {
    expect(hashOverlay({ density: 'compact' })).not.toBe(hashOverlay({ density: 'expertDense' }))
    expect(hashOverlay(null)).toBe('no-overlay')
  })
})
