import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createDocflowSaveSession } from '@/lib/api/docflow-save-session'
const http = vi.hoisted(() => ({ post: vi.fn(), put: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: http }))

beforeEach(() => { vi.resetAllMocks() })
describe('DocFlow logical save attempts', () => {
  it('uses the read version and reuses the key after a lost response', async () => {
    const session = createDocflowSaveSession()
    http.put.mockRejectedValueOnce(new Error('synthetic lost response')).mockResolvedValue({ data: { id: 'doc-a', version: 5 } })
    await expect(session.save('doc-a', 4, { currency: 'EUR' })).rejects.toThrow('lost response')
    await expect(session.save('doc-a', 4, { currency: 'EUR' })).resolves.toEqual({ id: 'doc-a', version: 5 })
    expect(http.put.mock.calls[0][1]).toEqual(http.put.mock.calls[1][1])
    expect(http.put.mock.calls[0][1].expected_version).toBe(4)
    expect(http.put.mock.calls[0][1].idempotency_key.length).toBeGreaterThanOrEqual(8)
  })
  it('joins duplicate clicks while the same save is pending', async () => {
    let finish!: (result: unknown) => void
    http.put.mockImplementation(() => new Promise(resolve => { finish = resolve }))
    const session = createDocflowSaveSession()
    const first = session.save('doc-a', 4, {})
    expect(session.save('doc-a', 4, {})).toBe(first)
    await expect(session.save('doc-a', 4, { currency: 'USD' })).rejects.toThrow('läuft bereits')
    finish({ data: { id: 'doc-a', version: 5 } })
    await first
    expect(http.put).toHaveBeenCalledOnce()
  })
  it('issues a new key for a different body or version', async () => {
    http.put.mockResolvedValue({ data: { id: 'doc-a', version: 5 } })
    const session = createDocflowSaveSession()
    await session.save('doc-a', 4, { currency: 'EUR' })
    await session.save('doc-a', 5, { currency: 'USD' })
    expect(http.put.mock.calls[0][1].idempotency_key).not.toBe(http.put.mock.calls[1][1].idempotency_key)
  })
  it.each([undefined, 0, -1, 1.5])('blocks existing documents without valid version %s', async version => {
    await expect(createDocflowSaveSession().save('doc-a', version, {})).rejects.toThrow('Belegversion fehlt')
    expect(http.put).not.toHaveBeenCalled()
  })
  it('keeps creation retry identity when transport fails', async () => {
    http.post.mockRejectedValueOnce(new Error('offline')).mockResolvedValue({ data: { id: 'new-a', version: 1 } })
    const session = createDocflowSaveSession()
    await expect(session.save(null, undefined, { status: 'draft' })).rejects.toThrow('offline')
    await session.save(null, undefined, { status: 'draft' })
    expect(http.post.mock.calls[0][1]).toEqual(http.post.mock.calls[1][1])
    expect(http.post.mock.calls[0][1]).not.toHaveProperty('expected_version')
  })
  it('does not accept an incomplete or foreign confirmation', async () => {
    http.put.mockResolvedValue({ data: { id: 'other', version: 5 } })
    await expect(createDocflowSaveSession().save('doc-a', 4, {})).rejects.toThrow('Speicherbestätigung')
  })
})
