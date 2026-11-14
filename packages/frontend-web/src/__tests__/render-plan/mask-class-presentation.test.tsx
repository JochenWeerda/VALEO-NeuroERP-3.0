import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { cleanup, fireEvent, render, screen } from '@testing-library/react'
import { afterEach, describe, expect, it, vi } from 'vitest'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import { compileRenderPlanFromScreenDefinition, invalidateRenderPlanCache } from '@/components/mask-builder/render-plan/schema-compiler'
import type { ScreenDefinition, ScreenFloorplan } from '@/components/mask-builder/schema'

afterEach(() => {
  cleanup()
  document.documentElement.classList.remove('dark')
})

// A class contract, not a replacement for each variant's business-command tests.
// JSDOM checks semantic tokens/target classes; studio-theme-contrast tests the
// actual palette ratios. Neither is a browser pixel or device acceptance test.
function definition(floorplan: ScreenFloorplan): ScreenDefinition {
  return {
    schemaVersion: 1, id: `synthetic/class-${floorplan}`, domain: 'agrar',
    mode: 'detail', title: 'Synthetische Klassenmaske',
    layout: { floorplan, density: 'compact', contextRail: 'none', columnNavigation: 'single' },
    fields: [{ key: 'name', label: 'Bezeichnung', type: 'text' }],
    actions: [
      { key: 'save', label: 'Speichern', kind: 'primary', permission: 'synthetic.edit' },
      { key: 'delete', label: 'Löschen', kind: 'danger', disabled: true, permission: 'synthetic.edit' },
    ],
  }
}

describe.each(['worklist', 'objectPage', 'transaction', 'cockpit', 'wizard'] as const)('%s class', floorplan => {
  it.each(['light', 'dark'])('renders labelled semantic controls and disabled actions in %s', theme => {
    invalidateRenderPlanCache()
    document.documentElement.classList.toggle('dark', theme === 'dark')
    const plan = compileRenderPlanFromScreenDefinition(definition(floorplan), { permissions: ['synthetic.edit'] })
    const action = vi.fn()
    render(<QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <UniversalMaskRenderer plan={plan} data={{ name: 'Synthetischer Datensatz' }} onAction={action} />
    </QueryClientProvider>)
    expect(screen.getByTestId(`screen-synthetic/class-${floorplan}`)).toHaveAttribute('data-floorplan', floorplan)
    expect(screen.getByRole('heading', { name: 'Synthetische Klassenmaske', level: 1 })).toHaveClass('text-foreground')
    expect(screen.getByRole('textbox', { name: /Bezeichnung/ })).toHaveValue('Synthetischer Datensatz')
    const save = screen.getByRole('button', { name: 'Speichern' })
    const remove = screen.getByRole('button', { name: 'Löschen' })
    expect(save).toHaveClass('min-h-touch', 'min-w-touch')
    expect(remove).toHaveClass('min-h-touch', 'min-w-touch')
    expect(remove).toBeDisabled()
    fireEvent.click(remove)
    expect(action).not.toHaveBeenCalled()
    fireEvent.click(save)
    expect(action).toHaveBeenCalledOnce()
    expect(action.mock.calls[0][0]).toBe('save')
    expect(document.documentElement.classList.contains('dark')).toBe(theme === 'dark')
  })
})
