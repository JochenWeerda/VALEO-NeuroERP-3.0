import { afterEach, expect, it, vi } from 'vitest'
import { appendSseAuthToken, SSEClient } from '@/lib/sse-client'
afterEach(() => { vi.unstubAllEnvs(); vi.unstubAllGlobals() })
it.each(['https://foreign.example/events', '//foreign.example/events', 'javascript:alert(1)', 'https://[invalid', 'https://user:pass@foreign.example/events'])('rejects untrusted destination %s', url => {
  expect(appendSseAuthToken(url, 'synthetic-token')).toBeNull()
})
it('keeps relative routing and escapes tokens', () => {
  expect(appendSseAuthToken('/api/events?stream=mcp', 'a+b')).toBe('/api/events?stream=mcp&token=a%2Bb')
})
it('accepts an explicitly configured secure SSE origin only', () => {
  vi.stubEnv('VITE_MCP_EVENTS_URL', 'https://events.example/api/events')
  expect(appendSseAuthToken('https://events.example/api/events', 't')).toBe('https://events.example/api/events?token=t')
  expect(appendSseAuthToken('https://other.example/api/events', 't')).toBeNull()
})
it('does not open EventSource without a required token or for a foreign origin', () => {
  const construct = vi.fn()
  vi.stubGlobal('EventSource', class { constructor(...args: unknown[]) { construct(...args) } })
  new SSEClient({ onEvent: vi.fn() }, { getToken: () => undefined }).start()
  new SSEClient({ onEvent: vi.fn() }, { url: 'https://foreign.example/events', getToken: () => 'secret' }).start()
  expect(construct).not.toHaveBeenCalled()
})
it('rejects HTTPS downgrade and permits explicitly configured local development', () => {
  vi.stubGlobal('window', { location: { origin: 'https://erp.example' } })
  vi.stubEnv('VITE_MCP_EVENTS_URL', 'http://localhost:8000/api/events')
  expect(appendSseAuthToken('http://localhost:8000/api/events', 't')).toBeNull()
  vi.stubGlobal('window', { location: { origin: 'http://localhost:3000' } })
  expect(appendSseAuthToken('http://localhost:8000/api/events', 't')).toBe('http://localhost:8000/api/events?token=t')
})

it('keeps same-origin streams working with malformed unrelated configuration', () => {
  vi.stubEnv('VITE_MCP_EVENTS_URL', 'https://[invalid')
  expect(appendSseAuthToken('/api/events', 't')).toBe('/api/events?token=t')
  expect(appendSseAuthToken('https://foreign.example/events', 't')).toBeNull()
})

it('resolves path-relative streams against the current page', () => {
  vi.stubGlobal('window', { location: { origin: 'https://erp.example', href: 'https://erp.example/nested/page' } })
  expect(appendSseAuthToken('events', 't')).toBe('https://erp.example/nested/events?token=t')
})

it('retries a missing token with bounded backoff and stops pending retries', () => {
  vi.useFakeTimers()
  const construct = vi.fn()
  class FakeEventSource {
    static OPEN = 1
    readyState = 1
    onmessage = null
    constructor(...args: unknown[]) { construct(...args) }
    addEventListener() {}
    removeEventListener() {}
    close() {}
  }
  vi.stubGlobal('EventSource', FakeEventSource)
  let token: string | undefined
  const client = new SSEClient({ onEvent: vi.fn() }, { getToken: () => token, retryBaseMs: 100, maxRetryMs: 200 })
  client.start(); client.start()
  expect(vi.getTimerCount()).toBe(1)
  vi.advanceTimersByTime(100)
  expect(construct).not.toHaveBeenCalled()
  token = 'later'
  vi.advanceTimersByTime(199)
  expect(construct).not.toHaveBeenCalled()
  vi.advanceTimersByTime(1)
  expect(construct).toHaveBeenCalledTimes(1)
  expect(construct.mock.calls[0][0]).toContain('token=later')
  client.stop()
  expect(vi.getTimerCount()).toBe(0)
  token = undefined
  client.start()
  expect(vi.getTimerCount()).toBe(1)
  client.stop()
  vi.advanceTimersByTime(1000)
  expect(construct).toHaveBeenCalledTimes(1)
  expect(vi.getTimerCount()).toBe(0)
  vi.useRealTimers()
})
