import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { CommandPalette } from '@/components/navigation/CommandPalette'
import { apiClient } from '@/lib/api-client'
import { FakeSttProvider } from '@/lib/voice/stt-provider'

const dispatchMock = vi.fn<(_actionId: string, _params?: Record<string, unknown>) => Promise<boolean>>()

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}))

vi.mock('@/hooks/useFeature', () => ({
  useFeature: (feature: string) => feature === 'agrar',
}))

vi.mock('@/app/navigation/nav-runtime', () => ({
  useNavigationShortcuts: () => [],
}))

vi.mock('@/features/ki-usability/context/ActionDispatchHooks', () => ({
  useActionDispatch: () => ({
    registerHandler: vi.fn(),
    dispatch: dispatchMock,
  }),
}))

const mockedGet = vi.mocked(apiClient.get)

describe('CommandPalette', () => {
  beforeEach(() => {
    window.HTMLElement.prototype.scrollIntoView = vi.fn()
    delete window.__VALEO_STT_PROVIDER__
    dispatchMock.mockReset()
    dispatchMock.mockResolvedValue(true)
    mockedGet.mockReset()
    const registryResponse = {
      data: {
        schema_version: 1,
        masks: [
          {
            mask_id: 'finance/abschluss',
            route: '/finance/abschluss',
            label: 'Periodenabschluss-Arbeitsplatz',
            domain: 'finance',
            mask_class: 'A',
            process_key: 'closing_checklist',
            explainability: 'required',
            requires_approval_ui: true,
            gobd_relevant: true,
            wave1_contract: true,
            schema_version: 1,
          },
        ],
      },
    }
    // global-search (/api/v1/search) liefert results[]; alles andere Mask-Registry
    mockedGet.mockImplementation((url: string) => {
      if (url.includes('/search')) {
        return Promise.resolve({ data: { results: [] } })
      }
      if (url.includes('/omnibox-catalog')) {
        return Promise.resolve({ data: [] })
      }
      return Promise.resolve(registryResponse)
    })
  })

  it('laedt Prozessmasken aus der Registry und dispatcht ueber den zentralen Action-Dispatcher', async () => {
    const onOpenChange = vi.fn()
    const queryClient = new QueryClient()

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <CommandPalette open onOpenChange={onOpenChange} />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    await screen.findByText('Periodenabschluss-Arbeitsplatz')

    fireEvent.click(screen.getByText('Periodenabschluss-Arbeitsplatz'))

    await waitFor(() => {
      expect(dispatchMock).toHaveBeenCalledWith('mask:finance/abschluss', {
        path: '/finance/abschluss',
        maskId: 'finance/abschluss',
        maskClass: 'A',
        processKey: 'closing_checklist',
      })
    })
    expect(onOpenChange).toHaveBeenCalledWith(false)
  })

  it('zeigt die Omnibox-Intent-Vorschau "Verstanden als" mit Filter-Chips (UIX-060)', async () => {
    const onOpenChange = vi.fn()
    const queryClient = new QueryClient()

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <CommandPalette open onOpenChange={onOpenChange} />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    fireEvent.change(screen.getByPlaceholderText(/Aktion suchen/), {
      target: { value: 'überfällige rechnungen' },
    })

    await screen.findByText('Verstanden als')
    // Bester Plan trägt den overdue-Filter in der Route; kein Dispatch ohne Auswahl
    await waitFor(() => {
      const intentItems = document.querySelectorAll('[data-mcp-action^="omnibox-intent:"]')
      expect(intentItems.length).toBeGreaterThan(0)
    })
    const first = document.querySelector('[data-mcp-action="omnibox-intent:nav-rechnungen"]')
    expect(first).not.toBeNull()
    expect(dispatchMock).not.toHaveBeenCalled()
  })

  it('uebernimmt Voice-Text in die Omnibox, ohne Command-Drafts zu erzeugen', async () => {
    const provider = new FakeSttProvider()
    window.__VALEO_STT_PROVIDER__ = provider
    mockedGet.mockImplementation((url: string) => {
      if (url.includes('/search')) return Promise.resolve({ data: { results: [] } })
      if (url.includes('/omnibox-catalog')) {
        return Promise.resolve({
          data: [
            {
              screen_id: 'crm/customer-360',
              title: 'Kundenakte',
              domain: 'crm',
              floorplan: 'cockpit',
              route: '/crm/kunden',
              synonyms: ['kundenakte'],
              example_prompts: [],
              filterable_fields: [],
              actions: [
                {
                  key: 'create_activity',
                  label: 'Aktivitaet anlegen',
                  dangerLevel: 'safe',
                  requiresConfirmation: false,
                  forbiddenForAgents: false,
                  verbs: ['anlegen'],
                  fields: [],
                },
              ],
            },
          ],
        })
      }
      return Promise.resolve({ data: { schema_version: 1, masks: [] } })
    })
    const onOpenChange = vi.fn()
    const queryClient = new QueryClient()

    render(
      <QueryClientProvider client={queryClient}>
        <MemoryRouter future={{ v7_startTransition: true, v7_relativeSplatPath: true }}>
          <CommandPalette open onOpenChange={onOpenChange} />
        </MemoryRouter>
      </QueryClientProvider>,
    )

    const voiceText = 'xyzzy plover'
    fireEvent.click(screen.getByTestId('voice-ptt'))
    act(() => provider.emitFinal(voiceText))
    await waitFor(() => {
      expect(screen.getByTestId('voice-transcript')).toHaveValue(voiceText)
    })
    fireEvent.click(screen.getByTestId('voice-commit'))

    await waitFor(() => {
      expect(screen.getByPlaceholderText(/Aktion suchen/)).toHaveValue(voiceText)
    })
    expect(document.querySelector('[data-mcp-action^="omnibox-command:"]')).toBeNull()
    expect(dispatchMock).not.toHaveBeenCalled()
  })
})
