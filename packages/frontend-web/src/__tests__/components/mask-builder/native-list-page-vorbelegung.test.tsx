import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { beforeEach, expect, it, vi } from 'vitest'
import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const { request, dialog } = vi.hoisted(() => ({ request: vi.fn(), dialog: vi.fn() }))
const definition = {
  schemaVersion: 1, id: 'einkauf/warengruppen', domain: 'einkauf', mode: 'list', title: 'Warengruppen',
  dataSources: [{ key: 'list', endpoint: '/api/v1/stammdaten/warengruppen' }],
  actions: [],
  tables: [{ key: 'list', label: 'Warengruppen', dataSourceKey: 'list', columns: [{ key: 'gruppe_nr', label: 'Nr.' }],
    rowActions: [{ key: 'bearbeiten', label: 'Bearbeiten', dangerLevel: 'safe', method: 'PUT',
      commandEndpoint: '/api/v1/stammdaten/warengruppen/{gruppe_nr}',
      inputFields: [{ key: 'gruppe_nr', label: 'Nr.', type: 'text' }, { key: 'bezeichnung', label: 'Bezeichnung', type: 'text' }] }] }],
} as unknown as ScreenDefinition

vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: definition }) }))
vi.mock('@/components/mask-builder/runtime/screen-permissions', () => ({ useScreenPermissions: () => [] }))
vi.mock('@/app/routing/typed-router', () => ({ useNavigate: () => vi.fn() }))
vi.mock('@/hooks/use-toast', () => ({ useToast: () => ({ toast: vi.fn() }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { request, get: vi.fn() }, getAxiosErrorMessage: (e: Error) => e.message }))
vi.mock('@/components/mask-builder/renderers/ActionInputDialog', () => ({
  ActionInputDialog: (props: { initialValues?: object; onSubmit: (werte: object) => void }) => {
    dialog(props.initialValues)
    return <button onClick={() => props.onSubmit({ ...props.initialValues, bezeichnung: 'Saatgut neu' })}>Speichern</button>
  },
}))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ onAction }: { onAction: (key: string, payload: object) => void }) => (
    <button onClick={() => onAction('bearbeiten', { id: 'uuid-1', gruppe_nr: 'WG 10', bezeichnung: 'Saatgut', ober_id: 'o-1' })}>
      Zeile bearbeiten
    </button>
  ),
}))

beforeEach(() => { vi.clearAllMocks() })

it('belegt Zeilenaktionen mit den Zeilenwerten vor und setzt Feld-Platzhalter in den Kommandoweg', async () => {
  request.mockResolvedValue({ data: { id: 'uuid-1' } })
  render(<QueryClientProvider client={new QueryClient()}><NativeListPage screenId="einkauf/warengruppen" /></QueryClientProvider>)
  fireEvent.click(screen.getByRole('button', { name: 'Zeile bearbeiten' }))
  expect(dialog).toHaveBeenLastCalledWith({ gruppe_nr: 'WG 10', bezeichnung: 'Saatgut' })
  fireEvent.click(screen.getByRole('button', { name: 'Speichern' }))
  fireEvent.click(await screen.findByRole('button', { name: 'Bearbeiten' }))
  await waitFor(() => expect(request).toHaveBeenCalledTimes(1))
  expect(request.mock.calls[0][0]).toMatchObject({
    url: '/api/v1/stammdaten/warengruppen/WG%2010', method: 'PUT',
    data: expect.objectContaining({ gruppe_nr: 'WG 10', bezeichnung: 'Saatgut neu' }),
  })
})
