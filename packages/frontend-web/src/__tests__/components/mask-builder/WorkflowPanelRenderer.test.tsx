import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import type { ReactElement } from 'react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { WorkflowPanelRenderer } from '@/components/mask-builder/renderers/WorkflowPanelRenderer'
import { apiClient } from '@/lib/api-client'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
    post: vi.fn(),
  },
}))

const mockedGet = vi.mocked(apiClient.get)
const mockedPost = vi.mocked(apiClient.post)

function renderWithQuery(ui: ReactElement) {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })
  return render(<QueryClientProvider client={queryClient}>{ui}</QueryClientProvider>)
}

describe('WorkflowPanelRenderer collab rail', () => {
  beforeEach(() => {
    mockedGet.mockResolvedValue({
      data: [
        {
          id: 'note-1',
          tenant_id: 'tenant-a',
          entity_type: 'crm/customer-360',
          entity_id: 'cust-1',
          body: 'Bestehende Notiz',
          mentions: [{ user_id: 'dev-user' }],
          created_by: 'other-user',
          created_at: '2026-07-07T08:00:00Z',
          updated_at: '2026-07-07T08:00:00Z',
          deleted_at: null,
        },
      ],
    } as never)
    mockedPost.mockResolvedValue({
      data: {
        id: 'note-2',
        tenant_id: 'tenant-a',
        entity_type: 'crm/customer-360',
        entity_id: 'cust-1',
        body: 'Neue Notiz @dev-user',
        mentions: [{ user_id: 'dev-user' }],
        created_by: 'dev-user',
        created_at: '2026-07-07T08:01:00Z',
        updated_at: '2026-07-07T08:01:00Z',
        deleted_at: null,
      },
    } as never)
  })

  afterEach(() => {
    vi.clearAllMocks()
  })

  it('renders notes, mention badge and submits a new note', async () => {
    renderWithQuery(
      <WorkflowPanelRenderer
        contextRailSections={['workflow', 'collab']}
        entityType="crm/customer-360"
        entityId="cust-1"
        currentUserId="dev-user"
      />,
    )

    expect(await screen.findByText('Bestehende Notiz')).toBeInTheDocument()
    expect(screen.getByTestId('collab-mention-badge')).toHaveTextContent('1')

    fireEvent.change(screen.getByTestId('collab-note-body'), {
      target: { value: 'Neue Notiz @dev-user' },
    })
    fireEvent.change(screen.getByTestId('collab-mention-input'), {
      target: { value: 'u-mentioned' },
    })
    fireEvent.click(screen.getByTestId('collab-note-submit'))

    await waitFor(() => expect(mockedPost).toHaveBeenCalledTimes(1))
    expect(mockedPost).toHaveBeenCalledWith('/api/v1/collab/notes', {
      entity_type: 'crm/customer-360',
      entity_id: 'cust-1',
      body: 'Neue Notiz @dev-user',
      mentions: [{ user_id: 'dev-user' }, { user_id: 'u-mentioned' }],
    })
  })
})
