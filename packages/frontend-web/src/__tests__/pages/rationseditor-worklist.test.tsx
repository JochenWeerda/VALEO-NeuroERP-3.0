/**
 * FEED-NAV-050: Rationsliste als Editor-Einstieg — ohne ?ration_id zeigt die
 * Route eine Worklist, deren Zeilen den Editor mit ration_id oeffnen.
 */
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import RationsEditorPage from '@/pages/futtermittel/rationseditor'

const listRationsMock = vi.hoisted(() => vi.fn())
const locationState = vi.hoisted(() => ({ search: '' }))

vi.mock('@/lib/api/rations-lifecycle', () => ({
  listRations: listRationsMock,
  fetchRationDetail: vi.fn(),
}))

vi.mock('@/features/feed-advice/RationEditor', () => ({
  RationEditor: ({ rationId }: { rationId: string }) => <div data-testid="editor">{rationId}</div>,
}))

vi.mock('@/app/routing/typed-router', () => ({
  useLocation: () => locationState,
}))

function renderPage(): void {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  render(<QueryClientProvider client={client}><RationsEditorPage /></QueryClientProvider>)
}

describe('Rationseditor-Einstieg (FEED-NAV-050)', () => {
  beforeEach(() => {
    listRationsMock.mockReset()
    locationState.search = ''
  })

  it('zeigt ohne ration_id die Rationsliste mit Editor-Links', async () => {
    listRationsMock.mockResolvedValue([{
      id: 'r-1', name: 'Sommerration', group_id: 'g-1', group_name: 'Hochleistung',
      version_no: 3, status: 'draft', updated_at: '2026-07-17T06:00:00Z',
    }])
    renderPage()

    const link = await screen.findByRole('link', { name: 'Sommerration' })
    expect(link).toHaveAttribute('href', '/futtermittel/rationseditor?ration_id=r-1')
    expect(screen.getByText('Hochleistung')).toBeInTheDocument()
    expect(screen.getByText('Entwurf')).toBeInTheDocument()
  })

  it('leerer Bestand verweist handlungsorientiert auf die Rationsoptimierung', async () => {
    listRationsMock.mockResolvedValue([])
    renderPage()
    expect(await screen.findByRole('status')).toHaveTextContent(/Rationsoptimierung/)
  })

  it('oeffnet mit ration_id direkt den Editor', () => {
    locationState.search = '?ration_id=r-9'
    renderPage()
    expect(screen.getByTestId('editor')).toHaveTextContent('r-9')
    expect(listRationsMock).not.toHaveBeenCalled()
  })
})
