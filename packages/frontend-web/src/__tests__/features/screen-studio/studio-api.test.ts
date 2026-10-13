import { beforeEach, expect, it, vi } from 'vitest'
import { emptyStudioDraft } from '@/features/screen-studio/studio-defaults'
import { proposeStudioDraft, saveStudioDraft, submitStudioReview, publishStudioDraft } from '@/lib/api/studio'

const client = vi.hoisted(() => ({ post: vi.fn(), put: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: client }))
beforeEach(() => {
  vi.clearAllMocks()
  client.post.mockResolvedValue({ data: {} })
  client.put.mockResolvedValue({ data: {} })
})
it('uses the authenticated client without caller-selected identities on all studio writes', async () => {
  const definition = emptyStudioDraft()
  await proposeStudioDraft('Kunden')
  await saveStudioDraft(definition)
  await saveStudioDraft(definition, 'draft-a')
  await submitStudioReview('draft-a')
  await publishStudioDraft('draft-a')
  expect(client.post.mock.calls).toEqual([
    ['/api/v1/studio/propose', { intent: 'Kunden' }],
    ['/api/v1/studio/drafts', { definition }],
    ['/api/v1/studio/drafts/draft-a/submit-review', {}],
    ['/api/v1/studio/drafts/draft-a/publish', {}],
  ])
  expect(client.put).toHaveBeenCalledWith('/api/v1/studio/drafts/draft-a', { definition })
})
