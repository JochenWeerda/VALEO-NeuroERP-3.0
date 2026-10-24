import { act, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { apiClient } from '@/lib/api-client'
import { auth } from '@/lib/auth'
import { useWorkspaceLiveSignals } from '@/workspace/live-signals'

const session = vi.hoisted(() => ({ token: 'first-token' as string | null }))

vi.mock('@/lib/api-client', () => ({ apiClient: { get: vi.fn() } }))
vi.mock('@/lib/auth', () => ({
  auth: {
    getAccessToken: () => session.token,
    getFreshAccessToken: vi.fn(async () => session.token),
  },
}))

class FakeEventSource {
  static instances: FakeEventSource[] = []
  url: string
  closed = false
  onopen: (() => void) | null = null
  onmessage: ((event: MessageEvent<string>) => void) | null = null
  onerror: (() => void) | null = null
  constructor(url: string) {
    this.url = url
    FakeEventSource.instances.push(this)
  }
  addEventListener(): void {}
  close(): void { this.closed = true }
  open(): void { this.onopen?.() }
  fail(): void { this.onerror?.() }
  emit(type: string, count: number): void {
    this.onmessage?.(new MessageEvent('message', { data: JSON.stringify({ type, payload: { count } }) }))
  }
}

function Probe(): JSX.Element {
  const signals = useWorkspaceLiveSignals(new Date('2026-10-22T08:00:00'))
  return <output data-testid="signals">{signals.map((signal) => `${signal.id}:${signal.count}`).join('|')}</output>
}

describe('workspace SSE recovery', () => {
  beforeEach(() => {
    session.token = 'first-token'
    FakeEventSource.instances = []
    vi.stubGlobal('EventSource', FakeEventSource)
    vi.mocked(apiClient.get).mockReset()
    vi.mocked(auth.getFreshAccessToken).mockClear()
  })

  afterEach(() => {
    vi.useRealTimers()
    vi.unstubAllGlobals()
  })

  it('uses a fresh token and replaces stale queue and SSE counts after reconnect', async () => {
    let phase = 1
    vi.mocked(apiClient.get).mockImplementation(async (path) => ({
      data: { count: String(path).includes('approvals') ? (phase === 1 ? 4 : 0) : (phase === 1 ? 0 : 2) },
    }) as never)
    render(<Probe />)
    await waitFor(() => expect(FakeEventSource.instances).toHaveLength(1))
    await waitFor(() => expect(screen.getByTestId('signals')).toHaveTextContent('queue-approval:4'))
    const first = FakeEventSource.instances[0]
    expect(first.url).toContain('token=first-token')
    act(() => first.open())
    vi.useFakeTimers()
    act(() => first.emit('finance.ap_invoice.approval_requested', 7))
    expect(screen.getByTestId('signals')).toHaveTextContent('sse:finance.ap_invoice.approval_requested:7')

    phase = 2
    session.token = 'refreshed-token'
    act(() => first.fail())
    expect(first.closed).toBe(true)
    await act(async () => { await vi.advanceTimersByTimeAsync(1_000) })
    expect(FakeEventSource.instances).toHaveLength(2)
    const second = FakeEventSource.instances[1]
    expect(second.url).toContain('token=refreshed-token')
    act(() => second.open())
    await act(async () => { await Promise.resolve() })

    expect(screen.getByTestId('signals')).toHaveTextContent('queue-inbox:2')
    expect(screen.getByTestId('signals')).not.toHaveTextContent('queue-approval:4')
    expect(screen.getByTestId('signals')).not.toHaveTextContent('sse:finance.ap_invoice.approval_requested:7')
    expect(vi.mocked(apiClient.get).mock.calls.length).toBeGreaterThanOrEqual(6)
  })

  it('confirms a completion event against the queue and clears its stale signal at zero', async () => {
    let approvalCount = 1
    vi.mocked(apiClient.get).mockImplementation(async (path) => ({
      data: { count: String(path).includes('approvals') ? approvalCount : 0 },
    }) as never)
    render(<Probe />)
    await waitFor(() => expect(FakeEventSource.instances).toHaveLength(1))
    await waitFor(() => expect(screen.getByTestId('signals')).toHaveTextContent('queue-approval:1'))
    act(() => FakeEventSource.instances[0].open())
    await waitFor(() => expect(vi.mocked(apiClient.get).mock.calls.length).toBeGreaterThanOrEqual(4))

    approvalCount = 0
    vi.useFakeTimers()
    act(() => FakeEventSource.instances[0].emit('finance.ap_invoice.approved', 1))
    expect(screen.getByTestId('signals')).toHaveTextContent('sse:finance.ap_invoice.approved:1')
    await act(async () => { await vi.advanceTimersByTimeAsync(250) })
    expect(screen.getByTestId('signals')).not.toHaveTextContent('queue-approval:1')
    expect(screen.getByTestId('signals')).not.toHaveTextContent('sse:finance.ap_invoice.approved:1')
  })

  it('refreshes queues when the first socket failed before it ever opened', async () => {
    let approvalCount = 2
    vi.mocked(apiClient.get).mockImplementation(async (path) => ({
      data: { count: String(path).includes('approvals') ? approvalCount : 0 },
    }) as never)
    render(<Probe />)
    await waitFor(() => expect(FakeEventSource.instances).toHaveLength(1))
    await waitFor(() => expect(screen.getByTestId('signals')).toHaveTextContent('queue-approval:2'))
    approvalCount = 0
    vi.useFakeTimers()
    act(() => FakeEventSource.instances[0].fail())
    await act(async () => { await vi.advanceTimersByTimeAsync(1_000) })
    expect(FakeEventSource.instances).toHaveLength(2)
    act(() => FakeEventSource.instances[1].open())
    await act(async () => { await Promise.resolve() })
    expect(screen.getByTestId('signals')).not.toHaveTextContent('queue-approval:2')
  })

  it('stops after five unsuccessful reconnects and closes on unmount', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: { count: 0 } } as never)
    const view = render(<Probe />)
    await waitFor(() => expect(FakeEventSource.instances).toHaveLength(1))
    vi.useFakeTimers()
    for (const delay of [1_000, 2_000, 4_000, 8_000, 16_000]) {
      act(() => FakeEventSource.instances.at(-1)?.fail())
      await act(async () => { await vi.advanceTimersByTimeAsync(delay) })
    }
    expect(FakeEventSource.instances).toHaveLength(6)
    act(() => FakeEventSource.instances.at(-1)?.fail())
    await act(async () => { await vi.advanceTimersByTimeAsync(60_000) })
    expect(FakeEventSource.instances).toHaveLength(6)
    view.unmount()
    expect(FakeEventSource.instances.at(-1)?.closed).toBe(true)
  })

  it('does not reconnect without a valid session token', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: { count: 0 } } as never)
    const view = render(<Probe />)
    await waitFor(() => expect(FakeEventSource.instances).toHaveLength(1))
    session.token = null
    vi.useFakeTimers()
    act(() => FakeEventSource.instances[0].fail())
    await act(async () => { await vi.advanceTimersByTimeAsync(1_000) })
    expect(FakeEventSource.instances).toHaveLength(1)
    view.unmount()
  })

  it('cancels a pending reconnect when the workspace unmounts', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: { count: 0 } } as never)
    const view = render(<Probe />)
    await waitFor(() => expect(FakeEventSource.instances).toHaveLength(1))
    vi.useFakeTimers()
    act(() => FakeEventSource.instances[0].fail())
    view.unmount()
    await act(async () => { await vi.advanceTimersByTimeAsync(60_000) })
    expect(FakeEventSource.instances).toHaveLength(1)
  })

  it('retries a temporary token refresh error without an unhandled rejection', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: { count: 0 } } as never)
    vi.mocked(auth.getFreshAccessToken).mockRejectedValueOnce(new Error('provider temporarily unavailable'))
    vi.useFakeTimers()
    render(<Probe />)
    await act(async () => { await Promise.resolve() })
    expect(FakeEventSource.instances).toHaveLength(0)
    await act(async () => { await vi.advanceTimersByTimeAsync(1_000) })
    expect(FakeEventSource.instances).toHaveLength(1)
    expect(FakeEventSource.instances[0].url).toContain('token=first-token')
  })
})
