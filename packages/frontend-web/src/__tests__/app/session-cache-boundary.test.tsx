import { useState, type ReactNode } from 'react'
import { act, cleanup, fireEvent, render, screen } from '@testing-library/react'
import { QueryClient, useQueryClient } from '@tanstack/react-query'
import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import DataBootstrap from '@/app/DataBootstrap'
const session = vi.hoisted(() => ({ user: { sub: 'alice', roles: ['admin', 'reader'], scopes: ['read', 'write'] }, token: '' }))
vi.mock('@/lib/auth', () => ({ auth: { getUser: () => session.user }, getAccessToken: () => session.token }))
vi.mock('@/app/providers/FeatureFlagProvider', () => ({ FeatureFlagProvider: ({ children }: { children: ReactNode }) => children }))
let currentClient: QueryClient
function Child() {
  currentClient = useQueryClient()
  const [queue] = useState(() => `${session.user.sub}:${session.token}`)
  const [draft, setDraft] = useState('')
  return <><output data-testid="queue">{queue}</output><input aria-label="draft" value={draft} onChange={event => setDraft(event.target.value)} /></>
}
function token(tenant: string, refresh = 1) { return `header.${btoa(JSON.stringify({ tenant_id: tenant, refresh }))}.signature` }
function change() { act(() => { window.dispatchEvent(new Event('valeo-auth-changed')) }) }
afterEach(cleanup)
beforeEach(() => { session.user = { sub: 'alice', roles: ['admin', 'reader'], scopes: ['read', 'write'] }; session.token = token('tenant-a') })
describe('session cache boundary', () => {
  it.each(['tenant', 'user', 'roles', 'scopes'])('discards caches and mounted local state when %s changes', kind => {
    render(<DataBootstrap><Child /></DataBootstrap>)
    const oldClient = currentClient
    oldClient.setQueryData(['private'], 'old private data')
    const oldQueue = screen.getByTestId('queue').textContent
    fireEvent.change(screen.getByLabelText('draft'), { target: { value: 'private draft' } })
    if (kind === 'tenant') session.token = token('tenant-b')
    if (kind === 'user') session.user = { ...session.user, sub: 'bob' }
    if (kind === 'roles') session.user = { ...session.user, roles: ['reader'] }
    if (kind === 'scopes') session.user = { ...session.user, scopes: ['read'] }
    change()
    expect(currentClient).not.toBe(oldClient)
    expect(currentClient.getQueryData(['private'])).toBeUndefined()
    expect(oldClient.getQueryData(['private'])).toBeUndefined()
    expect((screen.getByLabelText('draft') as HTMLInputElement).value).toBe('')
    if (kind === 'tenant' || kind === 'user') expect(screen.getByTestId('queue').textContent).not.toBe(oldQueue)
  })
  it('preserves client, cache and draft on refresh with reordered permissions', () => {
    render(<DataBootstrap><Child /></DataBootstrap>)
    const original = currentClient
    original.setQueryData(['private'], 'current private data')
    fireEvent.change(screen.getByLabelText('draft'), { target: { value: 'my draft' } })
    session.token = token('tenant-a', 2)
    session.user = { ...session.user, roles: ['reader', 'admin'], scopes: ['write', 'read'] }
    change()
    expect(currentClient).toBe(original)
    expect(original.getQueryData(['private'])).toBe('current private data')
    expect((screen.getByLabelText('draft') as HTMLInputElement).value).toBe('my draft')
  })
  it('keeps a late response from the old session out of the new cache', async () => {
    render(<DataBootstrap><Child /></DataBootstrap>)
    const oldClient = currentClient
    let resolveOld!: (value: string) => void
    const pending = oldClient.fetchQuery({ queryKey: ['late-private'], queryFn: () => new Promise<string>(resolve => { resolveOld = resolve }) }).catch(() => undefined)
    session.token = token('tenant-b')
    change()
    await act(async () => { resolveOld('old private response'); await pending })
    expect(currentClient).not.toBe(oldClient)
    expect(currentClient.getQueryData(['late-private'])).toBeUndefined()
    expect(oldClient.getQueryData(['late-private'])).toBeUndefined()
  })
})
