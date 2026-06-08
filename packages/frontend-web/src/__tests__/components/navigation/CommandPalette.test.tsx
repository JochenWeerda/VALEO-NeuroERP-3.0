import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { CommandPalette } from '@/components/navigation/CommandPalette'
import { apiClient } from '@/lib/api-client'

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
    dispatchMock.mockReset()
    dispatchMock.mockResolvedValue(true)
    mockedGet.mockReset()
    mockedGet.mockResolvedValue({
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
})
