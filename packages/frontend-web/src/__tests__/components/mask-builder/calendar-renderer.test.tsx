import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter } from '@/app/routing/test-router'
import { compileCalendar, compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { CalendarRenderer } from '@/components/mask-builder/renderers/CalendarRenderer'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const mockNavigate = vi.fn()

vi.mock('@/app/routing/typed-router', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/app/routing/typed-router')>()
  return { ...actual, useNavigate: () => mockNavigate }
})

function calendarSchema(): ScreenDefinition {
  return {
    schemaVersion: 1,
    id: 'planung/kalender',
    domain: 'platform',
    mode: 'cockpit',
    title: 'Planungskalender',
    calendar: {
      endpoint: '/api/v1/planung/kalender',
      defaultView: 'agenda',
      deadlineBandDays: 14,
      layers: [
        { key: 'finanzen', label: 'Finanzen', defaultVisible: true },
        { key: 'fristen', label: 'Fristen', defaultVisible: true },
        { key: 'personal', label: 'Personal', defaultVisible: false },
      ],
    },
  }
}

describe('compileCalendar', () => {
  it('kompiliert die Kalender-Primitive in den RenderPlan', () => {
    const plan = compileRenderPlanFromScreenDefinition(calendarSchema())
    expect(plan.calendar?.endpoint).toBe('/api/v1/planung/kalender')
    expect(plan.calendar?.deadlineBandDays).toBe(14)
    expect(plan.calendar?.layers.map((layer) => layer.key)).toEqual(['finanzen', 'fristen', 'personal'])
  })

  it('verwirft unvollstaendige Calendar-Definitionen', () => {
    const schema = calendarSchema()
    schema.calendar = { endpoint: '', layers: [] }
    expect(compileCalendar(schema)).toBeUndefined()
  })
})

describe('CalendarRenderer', () => {
  it('rendert Layer, Fristenband und navigiert per Objekt-Link', () => {
    mockNavigate.mockClear()
    const calendar = compileCalendar(calendarSchema())
    const queryClient = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter>
          <CalendarRenderer
            calendar={calendar}
            initialItems={[
              {
                id: 'frist-1',
                layer: 'fristen',
                item_type: 'frist',
                title: 'Ende Fruehbezugsrabatt',
                starts_at: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(),
                all_day: true,
                status: 'projected',
                object_route: '/kontrakte/kon-1',
                object_screen_id: 'agrar/kontrakte',
              },
              {
                id: 'pers-1',
                layer: 'personal',
                item_type: 'frist',
                title: 'Sachkunde laeuft ab',
                starts_at: new Date(Date.now() + 4 * 24 * 60 * 60 * 1000).toISOString(),
                all_day: true,
                status: 'projected',
                object_route: '/compliance/sachkunde/sk-1',
                object_screen_id: 'compliance/sachkunde',
              },
            ]}
          />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    expect(screen.getByTestId('calendar-renderer')).toBeInTheDocument()
    expect(screen.getByTestId('calendar-deadline-frist-1')).toBeInTheDocument()
    expect(screen.queryByText('Sachkunde laeuft ab')).not.toBeInTheDocument()

    fireEvent.click(screen.getByTestId('calendar-layer-personal'))
    expect(screen.getByTestId('calendar-item-pers-1')).toBeInTheDocument()

    fireEvent.click(screen.getByTestId('calendar-item-frist-1'))
    expect(mockNavigate).toHaveBeenCalledWith('/kontrakte/kon-1')
  })
})
