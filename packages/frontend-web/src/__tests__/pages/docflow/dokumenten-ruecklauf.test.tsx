import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import DokumentenRuecklaufPage from '@/pages/docflow/dokumenten-ruecklauf'

const { get, post, invalidateQueries, toast } = vi.hoisted(() => ({
  get: vi.fn(), post: vi.fn(), invalidateQueries: vi.fn(), toast: vi.fn(),
}))

vi.mock('@/lib/api-client', () => ({ apiClient: { get, post } }))
vi.mock('@tanstack/react-query', () => ({ useQueryClient: () => ({ invalidateQueries }) }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast }) }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ screenId, onAction }: { screenId: string; onAction: (_key: string, _row: Record<string, unknown>) => Promise<void> }) => (
    <div data-testid="native-worklist" data-screen-id={screenId}>
      <button type="button" onClick={() => void onAction('mark_received', { id: 'case-1' })}>Eingang</button>
    </div>
  ),
}))

describe('Dokumentenruecklauf', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    vi.spyOn(window, 'prompt').mockReturnValue('Posteingang geprueft')
    post.mockResolvedValue({ data: { success: true, summary: 'Ruecklauffall: return_status received.' } })
    invalidateQueries.mockResolvedValue(undefined)
  })

  it('nutzt die native ScreenDefinition und auditiert Statuswechsel', async () => {
    render(<DokumentenRuecklaufPage />)
    expect(screen.getByTestId('native-worklist')).toHaveAttribute('data-screen-id', 'docflow/dokumenten-ruecklauf')
    fireEvent.click(screen.getByRole('button', { name: 'Eingang' }))
    // Kommando-Weg der Maske (nicht unter /docflow), den auch CLI und MCP rufen.
    await waitFor(() => expect(post).toHaveBeenCalledWith('/api/v1/document-returns/case-1/actions/mark_received', {
      _auditReason: 'Posteingang geprueft', _idempotencyKey: expect.any(String),
    }))
    expect(invalidateQueries).toHaveBeenCalledWith({ queryKey: ['docflow/dokumenten-ruecklauf'] })
  })
})
