import { render } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import InboxPage from '@/pages/inbox'
import prepared from '../fixtures/inbox-prepared-synthetic.json'

const mocks = vi.hoisted(() => ({ post: vi.fn(), remove: vi.fn(), navigate: vi.fn(), toast: vi.fn(), invalidate: vi.fn(), props: {} as Record<string, unknown> }))
vi.mock('@tanstack/react-query', () => ({ useQueryClient: () => ({ invalidateQueries: mocks.invalidate }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { post: mocks.post, delete: mocks.remove } }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: mocks.toast }) }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => mocks.navigate }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: {} }) }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => ['dms.inbox.read'] }))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({ UniversalNativeCockpitPage: (props: Record<string, unknown>) => { mocks.props = props; return null } }))

async function action(key = 'create_beleg'): Promise<void> {
  render(<InboxPage />)
  await (mocks.props.onAction as (key: string, row: Record<string, unknown>) => Promise<void>)(key, { id: 'SYNTH-INBOX-1' })
}

describe('Inbox prepares a fresh proposal without booking', () => {
  beforeEach(() => { vi.clearAllMocks(); sessionStorage.clear(); mocks.post.mockResolvedValue({ data: structuredClone(prepared) }) })
  it('opens the permitted mask only after the server prepares this exact document', async () => {
    await action()
    expect(mocks.post).toHaveBeenCalledWith('/api/mcp/documents/inbox/SYNTH-INBOX-1/prepare', {})
    expect(mocks.navigate).toHaveBeenCalledOnce()
    expect(mocks.remove).not.toHaveBeenCalled()
    expect(mocks.invalidate).not.toHaveBeenCalled()
    expect(mocks.toast).not.toHaveBeenCalled()
    expect(mocks.props.permissions).toEqual(['dms.inbox.read'])
  })
  it.each(['foreign-id', 'booking', 'denied', 'unknown-kind'])('rejects %s responses without opening or marking processed', async reason => {
    const data = structuredClone(prepared)
    if (reason === 'foreign-id') data.item.id = 'OTHER'
    if (reason === 'booking') data.booking_allowed = true
    if (reason === 'denied') data.item.can_open = false
    if (reason === 'unknown-kind') data.item.proposal.document_kind = 'UNKNOWN'
    mocks.post.mockResolvedValue({ data })
    await action()
    expect(mocks.navigate).not.toHaveBeenCalled()
    expect(mocks.remove).not.toHaveBeenCalled()
    expect(mocks.invalidate).not.toHaveBeenCalled()
    expect(mocks.toast).toHaveBeenCalledWith(expect.objectContaining({ variant: 'destructive' }))
  })
  it('requires confirmation before deleting the inbox entry', async () => {
    vi.spyOn(window, 'confirm').mockReturnValueOnce(false)
    await action('discard')
    expect(mocks.remove).not.toHaveBeenCalled()
    vi.spyOn(window, 'confirm').mockReturnValueOnce(true)
    await action('discard')
    expect(mocks.remove).toHaveBeenCalledWith('/api/v1/dms/inbox/SYNTH-INBOX-1')
  })
})
