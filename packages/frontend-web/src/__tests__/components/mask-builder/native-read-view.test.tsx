import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, expect, it, vi } from 'vitest'
import { ReadViewDialog, readViewEndpoint } from '@/components/mask-builder/renderers/ReadViewDialog'
import type { ScreenActionDefinition } from '@/components/mask-builder/schema'
const { get, state } = vi.hoisted(() => ({ get: vi.fn(), state: { tenant: 'tenant-a', actor: 'actor-a' } }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { sub: state.actor } }) }))
vi.mock('@/lib/auth', () => ({ auth: { getAccessToken: () => state.tenant } }))
vi.mock('@/lib/tenant-from-token', () => ({ tenantFromToken: (token: string) => token }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get } }))
vi.mock('@/lib/api/ux-overlays', () => ({ useUserScreenOverlay: () => ({ data: undefined }), overlayKeys: { screen: (s: string) => [s] } }))
vi.mock('@/components/mask-builder/runtime/useFlowSpineCatalogRuntime', () => ({ useFlowSpineCatalogRuntime: () => ({ loading: false, failed: false }) }))
const action: ScreenActionDefinition = { key: 'history', label: 'Zustellversuche', localEffect: 'view', readView: {
  endpoint: '/api/v1/webhooks/{id}/zustellversuche', columns: [{ key: 'fehler', label: 'Fehler' }],
} }
beforeEach(() => { vi.clearAllMocks(); state.tenant = 'tenant-a'; state.actor = 'actor-a' })
function view(allowed = true) { return <ReadViewDialog screenId="admin/webhooks-liste" action={action} row={{ id: 'wh-1' }} identity={JSON.stringify(['tenant-a', 'actor-a'])} allowed={allowed} onClose={() => {}} /> }
it('loads real related rows via GET through the universal runtime', async () => {
  get.mockResolvedValue({ data: [{ fehler: 'HTTP 500' }] })
  render(<QueryClientProvider client={new QueryClient()}>{view()}</QueryClientProvider>)
  expect(await screen.findByText('HTTP 500')).toBeVisible()
  expect(screen.getByRole('dialog')).toHaveAccessibleDescription('Lesende Ansicht zum ausgewählten Eintrag.')
  expect(get).toHaveBeenCalledTimes(1)
  expect(get.mock.calls[0][0]).toMatch(/^\/api\/v1\/webhooks\/wh-1\/zustellversuche\?/)
  expect(get.mock.calls[0][0]).not.toContain('/masks/')
})
it('hides loaded rows after identity change and makes no foreign request', async () => {
  get.mockResolvedValue({ data: [{ fehler: 'private-row' }] })
  const client = new QueryClient()
  const mounted = render(<QueryClientProvider client={client}>{view()}</QueryClientProvider>)
  await screen.findByText('private-row')
  state.tenant = 'tenant-b'
  mounted.rerender(<QueryClientProvider client={client}>{view()}</QueryClientProvider>)
  expect(screen.queryByText('private-row')).not.toBeInTheDocument()
  expect(screen.getByRole('alert')).toBeVisible()
  expect(get).toHaveBeenCalledTimes(1)
})
it('blocks missing permission before HTTP', () => {
  render(<QueryClientProvider client={new QueryClient()}>{view(false)}</QueryClientProvider>)
  expect(screen.getByRole('alert')).toBeVisible()
  expect(get).not.toHaveBeenCalled()
})
it.each(['.', '..', '', Number.NaN, undefined])('rejects invalid object identity %s', id => {
  expect(() => readViewEndpoint(action, { id })).toThrow()
})
it.each(['/api/v1/x/{tenant_id}', '/api/v1/x/{mandant}', 'https://foreign.test/x', '/api/v1/x?tenant_id=b'])('rejects unsafe template %s', endpoint => {
  expect(() => readViewEndpoint({ ...action, readView: { ...action.readView!, endpoint } }, { id: 'wh-1', tenant_id: 'b', mandant: 'b' })).toThrow()
})

it('hides previously loaded rows when permission is withdrawn', async () => {
  get.mockResolvedValue({ data: [{ fehler: 'revoked-row' }] })
  const client = new QueryClient()
  const mounted = render(<QueryClientProvider client={client}>{view()}</QueryClientProvider>)
  await screen.findByText('revoked-row')
  mounted.rerender(<QueryClientProvider client={client}>{view(false)}</QueryClientProvider>)
  expect(screen.queryByText('revoked-row')).not.toBeInTheDocument()
  expect(screen.getByRole('alert')).toBeVisible()
  expect(get).toHaveBeenCalledTimes(1)
})
