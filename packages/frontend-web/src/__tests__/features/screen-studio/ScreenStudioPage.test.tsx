import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import { ScreenStudioPage } from '@/features/screen-studio/ScreenStudioPage'

const postMock = vi.hoisted(() => vi.fn())
const getMock = vi.hoisted(() => vi.fn())
const putMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', async () => {
  const actual = await vi.importActual<typeof import('@/lib/api-client')>('@/lib/api-client')
  return {
    ...actual,
    apiClient: {
      get: getMock,
      post: postMock,
      put: putMock,
    },
  }
})

vi.stubGlobal('ResizeObserver', class {
  observe() {}
  unobserve() {}
  disconnect() {}
})

function renderStudio() {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return render(
    <MemoryRouter>
      <QueryClientProvider client={client}>
        <ScreenStudioPage />
      </QueryClientProvider>
    </MemoryRouter>,
  )
}

describe('ScreenStudioPage', () => {
  beforeEach(() => {
    getMock.mockResolvedValue({
      data: {
        floorplans: ['worklist', 'objectPage'],
        fieldTypes: ['text'],
        columnNavigation: ['single', 'listDetail'],
        dataSources: [],
        actions: [],
      },
    })
    postMock.mockImplementation(async (url: string) => {
      if (String(url).includes('/propose')) {
        return {
          data: {
            violations: [],
            canPublish: true,
            readiness: { generatorReady: true, errors: [] },
            definition: {
              schemaVersion: 1,
              id: 'tenant/kunden-arbeitsliste',
              domain: 'crm',
              mode: 'list',
              title: 'Kunden-Arbeitsliste',
              layout: { floorplan: 'worklist', columnNavigation: 'listDetail', density: 'compact', contextRail: 'none' },
              tables: [{ key: 'list', label: 'Kunden', columns: [{ key: 'name', label: 'Name' }] }],
            },
          },
        }
      }
      return { data: { violations: [], canPublish: true, readiness: { generatorReady: true, errors: [] } } }
    })
  })

  it('lets an agent intent replace the draft and keeps the preview', async () => {
    renderStudio()
    expect(screen.getByTestId('screen-studio')).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Maskenabsicht'), { target: { value: 'Kundenliste' } })
    fireEvent.click(screen.getByRole('button', { name: 'Aus Absicht erzeugen' }))
    await waitFor(() => expect(screen.getByDisplayValue('Kunden-Arbeitsliste')).toBeInTheDocument())
    expect(screen.getByTestId('studio-preview')).toBeInTheDocument()
    expect(screen.getByTestId('studio-gates')).toHaveTextContent('Publish möglich')
  })
})
