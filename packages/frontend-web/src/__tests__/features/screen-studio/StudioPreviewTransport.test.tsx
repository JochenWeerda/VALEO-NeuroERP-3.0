import { act, render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import { StudioPreview } from '@/features/screen-studio/StudioPreview'
import { apiClient } from '@/lib/api-client'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { compileRenderPlanFromScreenDefinition, invalidateRenderPlanCache } from '@/components/mask-builder/render-plan/schema-compiler'
import { createStudioPreviewPlan } from '@/components/mask-builder/render-plan/studio-preview'

afterEach(() => vi.restoreAllMocks())

function definition(): ScreenDefinition {
  return {
    id: 'tenant/transport-preview', schemaVersion: 1, domain: 'agrar', mode: 'cockpit', title: 'Transport-Probe',
    layout: { floorplan: 'cockpit', columnNavigation: 'single', contextRail: 'none' },
    calendar: { endpoint: 'https://untrusted.test/calendar', layers: [{ key: 'probe', label: 'Termine' }] },
    twin: { endpoint: 'https://untrusted.test/twin' },
    voice: { enabled: true },
    actions: [{ key: 'execute', label: 'Ausführen', kind: 'primary' }],
    tables: [{ key: 'rows', label: 'Zeilen', columns: [{ key: 'id', label: 'ID' }],
      rowRouteTemplate: '/productive/{id}', rowActions: [{ key: 'change', label: 'Ändern' }],
      bulkActions: [{ key: 'bulk', label: 'Sammeländerung' }] }],
  }
}

it('opens an embedded preview without live reads or navigation/write controls', async () => {
  const calls = vi.spyOn(apiClient, 'get').mockResolvedValue({ data: [] })
  render(<MemoryRouter><QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
    <StudioPreview definition={definition()} />
  </QueryClientProvider></MemoryRouter>)
  await act(async () => {})
  expect(calls).not.toHaveBeenCalled()
  expect(screen.getByText(/Ohne Live-Zugriff/)).toBeVisible()
  expect(screen.getByRole('button', { name: 'Ausführen' })).toBeDisabled()
  expect(screen.queryByTestId('twin-read-model')).not.toBeInTheDocument()
  expect(screen.queryByTestId('calendar-view-month')).not.toBeInTheDocument()
})

it('does not poison the cached plan later used by the real mask', () => {
  invalidateRenderPlanCache()
  const source = definition()
  const live = compileRenderPlanFromScreenDefinition(source)
  const { plan } = createStudioPreviewPlan(live)
  expect(plan.actions[0].disabled).toBe(true)
  expect(plan.tablesByKey.rows.rowActions).toBeUndefined()
  expect(plan.tablesByKey.rows.rowRouteTemplate).toBeUndefined()
  expect(plan.shell.voice?.enabled).toBe(false)
  expect(plan.calendar).toBeUndefined()
  expect(live.calendar?.endpoint).toBe(source.calendar?.endpoint)
  expect(live.tablesByKey.rows.rowActions).toHaveLength(1)
  expect(live.actions[0].disabled).not.toBe(true)
  expect(compileRenderPlanFromScreenDefinition(source)).toBe(live)
})
