import { act, renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, expect, it, vi } from 'vitest'
import type { ReactNode } from 'react'
import { auth } from '@/lib/auth'
import { apiClient } from '@/lib/api-client'
import { aktivesKundenkonto, usePortalKonto } from '@/lib/portal-konto'
import { usePortalKonten } from '@/components/portal/PortalKontoWahl'

const jwt = (tenant: string) => `e30.${btoa(JSON.stringify({ tenant_id: tenant }))}.sig`
const accounts = ['eins', 'zwei'].map(customer_id => ({ customer_id, name: null, customer_number: null, rolle: 'inhaber', rechte: [] }))

afterEach(() => {
  usePortalKonto.getState().waehle(null)
  vi.restoreAllMocks()
})

it('partitioniert Kontolisten und gibt die neue Wahl erst nach Abbruch alter Anfragen frei', async () => {
  let tenant = 'a'
  vi.spyOn(auth, 'getUser').mockReturnValue({ sub: 'person', email: '', name: '', roles: [], scopes: [], exp: 9999999999 })
  vi.spyOn(auth, 'getAccessToken').mockImplementation(() => jwt(tenant))
  vi.spyOn(apiClient, 'get').mockResolvedValue({ data: accounts } as never)
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const wrapper = ({ children }: { children: ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>
  const { result, rerender } = renderHook(() => usePortalKonten(), { wrapper })
  await waitFor(() => expect(result.current.konten).toHaveLength(2))
  usePortalKonto.getState().waehle(accounts[0])
  await waitFor(() => expect(result.current.aktiv?.customer_id).toBe('eins'))
  let release!: () => void
  const cancellation = new Promise<void>(resolve => { release = resolve })
  const cancel = vi.spyOn(client, 'cancelQueries').mockReturnValueOnce(cancellation)
  act(() => result.current.wechsle(accounts[1]))
  expect(cancel).toHaveBeenCalled()
  expect(aktivesKundenkonto()).toBeNull()
  await act(async () => { release(); await cancellation })
  await waitFor(() => expect(aktivesKundenkonto()).toBe('zwei'))
  tenant = 'b'
  act(() => { window.dispatchEvent(new Event('valeo-auth-changed')); rerender() })
  await waitFor(() => expect(client.getQueryCache().findAll({ queryKey: ['portal-kundenkonten'] })).toHaveLength(2))
  expect(aktivesKundenkonto()).toBeNull()
  const keys = client.getQueryCache().findAll({ queryKey: ['portal-kundenkonten'] }).map(q => q.queryKey)
  expect(keys[0]).not.toEqual(keys[1])
  expect(JSON.stringify(keys)).not.toContain(jwt('a'))
})

it('uebernimmt geaenderte Rechte desselben Kontos bei mehreren beobachtenden Komponenten', async () => {
  vi.spyOn(auth, 'getUser').mockReturnValue({ sub: 'person', email: '', name: '', roles: [], scopes: [], exp: 9999999999 })
  vi.spyOn(auth, 'getAccessToken').mockReturnValue(jwt('a'))
  vi.spyOn(apiClient, 'get').mockResolvedValue({ data: accounts } as never)
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const wrapper = ({ children }: { children: ReactNode }) => <QueryClientProvider client={client}>{children}</QueryClientProvider>
  const first = renderHook(() => usePortalKonten(), { wrapper })
  const second = renderHook(() => usePortalKonten(), { wrapper })
  await waitFor(() => expect(first.result.current.konten).toHaveLength(2))
  act(() => usePortalKonto.getState().waehle(accounts[0]))
  await waitFor(() => expect(second.result.current.aktiv?.rolle).toBe('inhaber'))
  const updated = { ...accounts[0], rolle: 'berater', rechte: ['feldbuch_lesen'] }
  act(() => {
    const query = client.getQueryCache().find({ queryKey: ['portal-kundenkonten'], exact: false })!
    client.setQueryData(query.queryKey, [updated, accounts[1]])
  })
  await waitFor(() => expect(usePortalKonto.getState().aktiv).toEqual(updated))
  expect(first.result.current.aktiv?.rechte).toEqual(['feldbuch_lesen'])
})
