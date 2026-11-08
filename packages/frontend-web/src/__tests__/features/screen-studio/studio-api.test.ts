import { beforeEach, expect, it, vi } from 'vitest'
import { emptyStudioDraft } from '@/features/screen-studio/studio-defaults'
import { proposeStudioDraft, saveStudioDraft, submitStudioReview, publishStudioDraft, saveStudioMigrationPlan } from '@/lib/api/studio'

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
  await saveStudioDraft(definition, 'draft-a', 'draft-revision')
  await submitStudioReview('draft-a', 'draft-revision')
  await publishStudioDraft('draft-a', 'reviewed-revision')
  expect(client.post.mock.calls).toEqual([
    ['/api/v1/studio/propose', { intent: 'Kunden' }],
    ['/api/v1/studio/drafts', { definition, idempotency_key: expect.any(String) }],
    ['/api/v1/studio/drafts/draft-a/submit-review', { expected_revision: 'draft-revision', idempotency_key: expect.any(String) }],
    ['/api/v1/studio/drafts/draft-a/publish', { expected_revision: 'reviewed-revision', idempotency_key: expect.any(String) }],
  ])
  expect(client.put).toHaveBeenCalledWith('/api/v1/studio/drafts/draft-a', { definition, expected_revision: 'draft-revision', idempotency_key: expect.any(String) })
})

it('keeps one key for repeated status intent but separates changed revisions', async () => {
  await publishStudioDraft('retry-draft', 'revision-a')
  await publishStudioDraft('retry-draft', 'revision-a')
  await publishStudioDraft('retry-draft', 'revision-b')
  const bodies = client.post.mock.calls.map(call => call[1])
  expect(bodies[0].idempotency_key).toBe(bodies[1].idempotency_key)
  expect(bodies[0].idempotency_key).not.toBe(bodies[2].idempotency_key)
})

it('binds save retry keys to definition and displayed revision', async () => {
  const definition = emptyStudioDraft()
  await saveStudioDraft(definition)
  await saveStudioDraft({ ...definition })
  await saveStudioDraft({ ...definition, title: 'Changed' })
  const bodies = client.post.mock.calls.map(call => call[1])
  expect(bodies[0].idempotency_key).toBe(bodies[1].idempotency_key)
  expect(bodies[0].idempotency_key).not.toBe(bodies[2].idempotency_key)
})

it('binds plan retries to the saved revision and escapes the draft path', async () => {
  await saveStudioMigrationPlan('draft/one', 'revision-a')
  await saveStudioMigrationPlan('draft/one', 'revision-a')
  await saveStudioMigrationPlan('draft/one', 'revision-b')
  const calls = client.post.mock.calls
  expect(calls[0][0]).toBe('/api/v1/studio/drafts/draft%2Fone/migration-plan')
  expect(calls[0][1]).toEqual({ expected_revision: 'revision-a', schema_changes: [], idempotency_key: expect.any(String) })
  expect(calls[0][1].idempotency_key).toBe(calls[1][1].idempotency_key)
  expect(calls[0][1].idempotency_key).not.toBe(calls[2][1].idempotency_key)
})
