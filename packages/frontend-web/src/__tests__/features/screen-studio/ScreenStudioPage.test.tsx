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
        permissions: { canDesign: true, canPublish: true },
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
            canPublish: true, definitionReady: true,
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
      return { data: { violations: [], canPublish: true, definitionReady: true, readiness: { generatorReady: true, errors: [] } } }
    })
  })

  it('lets an agent intent replace the draft and keeps the preview', async () => {
    renderStudio()
    expect(screen.getByTestId('screen-studio')).toBeInTheDocument()
    fireEvent.change(screen.getByLabelText('Maskenabsicht'), { target: { value: 'Kundenliste' } })
    fireEvent.click(screen.getByRole('button', { name: 'Aus Absicht erzeugen' }))
    await waitFor(() => expect(screen.getByDisplayValue('Kunden-Arbeitsliste')).toBeInTheDocument())
    expect(screen.getByTestId('studio-preview')).toBeInTheDocument()
    expect(screen.getByTestId('studio-gates')).toHaveTextContent('Freigabe gesperrt')
    expect(screen.getByRole('button', { name: 'Freigeben' })).toBeDisabled()
  })

  it('keeps publish disabled while gates are red', async () => {
    postMock.mockImplementation(async () => ({
      data: {
        violations: ['action_confirmation_fehlt:stornieren'],
        canPublish: false, definitionReady: false,
        readiness: { generatorReady: false, errors: [] },
      },
    }))
    renderStudio()
    await waitFor(() => expect(screen.getByTestId('studio-gates')).toHaveTextContent('action_confirmation_fehlt'))
    expect(screen.getByRole('button', { name: 'Freigeben' })).toBeDisabled()
  })

  it('requires saving local changes before review or publication', async () => {
    const response = async (url: string, body: { definition?: unknown }) => ({ data: {
      id: 'draft-a', status: url.endsWith('/submit-review') ? 'review' : 'draft', revision: 'revision-a', definition: body.definition,
      violations: [], canPublish: true, definitionReady: true, readiness: { errors: [] },
      simulation: { passed: true, candidate_revision: 'revision-a', profile: 'grain.v1' },
    } })
    postMock.mockImplementation(response)
    putMock.mockImplementation(response)
    renderStudio()
    await waitFor(() => expect(screen.getByRole('button', { name: 'Speichern' })).toBeEnabled())
    fireEvent.click(screen.getByRole('button', { name: 'Speichern' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Prüfung' })).toBeEnabled())
    expect(screen.getByRole('button', { name: 'Freigeben' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Prüfung' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Prozess simulieren' })).toBeEnabled())
    expect(screen.getByRole('button', { name: 'Freigeben' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Prozess simulieren' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Freigeben' })).toBeEnabled())
    fireEvent.change(screen.getByLabelText('Titel'), { target: { value: 'Ungespeicherter Entwurf' } })
    expect(screen.getByRole('button', { name: 'Prüfung' })).toBeDisabled()
    expect(screen.getByRole('button', { name: 'Freigeben' })).toBeDisabled()
    expect(screen.getByText('Änderungen zuerst speichern, danach erneut prüfen.')).toBeInTheDocument()
    putMock.mockRejectedValueOnce(new Error('Speichern fehlgeschlagen'))
    fireEvent.click(screen.getByRole('button', { name: 'Speichern' }))
    await waitFor(() => expect(screen.getByText('Speichern fehlgeschlagen')).toBeInTheDocument())
    expect(screen.getByRole('button', { name: 'Freigeben' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Speichern' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Prüfung' })).toBeEnabled())
    expect(screen.getByRole('button', { name: 'Freigeben' })).toBeDisabled()
  })


  it('reopens a persisted draft and publishes the displayed server revision', async () => {
    const { emptyStudioDraft } = await import('@/features/screen-studio/studio-defaults')
    const definition = { ...emptyStudioDraft(), title: 'Entwurf einer anderen Person' }
    const record = { id: 'draft-review', status: 'review', revision: 'loaded-revision', definition }
    getMock.mockImplementation(async (url: string) => ({ data:
      url.endsWith('/drafts') ? { drafts: [record] } : url.endsWith('/draft-review') ? record : { floorplans: ['worklist'], permissions: { canDesign: true, canPublish: true } },
    }))
    postMock.mockImplementation(async (url: string, body: { definition?: unknown }) => ({ data:
      url.endsWith('/simulate') ? { ...record, simulation: { passed: true, candidate_revision: record.revision, profile: 'grain.v1' } } : url.endsWith('/publish') ? { ...record, status: 'published_temp', violations: [], canPublish: true, definitionReady: true, readiness: { errors: [] } }
        : { definition: body.definition, violations: [], canPublish: true, definitionReady: true, readiness: { errors: [] } },
    }))
    renderStudio()
    await screen.findByRole('option', { name: 'Entwurf einer anderen Person (review)' })
    fireEvent.change(screen.getByLabelText('Gespeicherten Entwurf öffnen'), { target: { value: 'draft-review' } })
    await waitFor(() => expect(screen.getByDisplayValue('Entwurf einer anderen Person')).toBeInTheDocument())
    await waitFor(() => expect(screen.getByRole('button', { name: 'Prozess simulieren' })).toBeEnabled())
    expect(screen.getByRole('button', { name: 'Freigeben' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Prozess simulieren' }))
    await waitFor(() => expect(screen.getByRole('button', { name: 'Freigeben' })).toBeEnabled())
    fireEvent.click(screen.getByRole('button', { name: 'Freigeben' }))
    await waitFor(() => expect(postMock).toHaveBeenCalledWith('/api/v1/studio/drafts/draft-review/publish', { expected_revision: 'loaded-revision', idempotency_key: expect.any(String) }))
  })

})
