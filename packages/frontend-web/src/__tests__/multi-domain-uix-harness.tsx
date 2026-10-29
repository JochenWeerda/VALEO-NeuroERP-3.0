import { createElement, type ComponentType } from 'react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, cleanup, screen, fireEvent, waitFor, within } from '@testing-library/react'
import { beforeEach, afterEach, expect, vi } from 'vitest'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { MemoryRouter } from '@/app/routing/test-router'
import definitions from './fixtures/multi-domain-uix-builder-contracts.json'

const state = vi.hoisted(() => ({ get: vi.fn(), request: vi.fn(), navigate: vi.fn(), touch: false,
  roles: [] as string[], downloads: [] as Blob[] }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: state.get, request: state.request },
  getAxiosErrorMessage: (error: Error) => error.message }))
vi.mock('@/hooks/useAuth', () => ({ useAuth: () => ({ user: { id: 'synthetic-user', roles: state.roles, scopes: [] } }) }))
vi.mock('@/app/routing/typed-router', async importOriginal => ({
  ...await importOriginal<typeof import('@/app/routing/typed-router')>(), useNavigate: () => state.navigate,
}))

beforeEach(() => {
  vi.restoreAllMocks(); vi.clearAllMocks(); state.roles = []; state.touch = false; state.downloads = []
  vi.spyOn(HTMLElement.prototype, 'getBoundingClientRect').mockReturnValue({
    width: 1440, height: 600, top: 0, left: 0, right: 1440, bottom: 600, x: 0, y: 0, toJSON: () => ({}),
  })
  vi.stubGlobal('matchMedia', (query: string) => ({ matches: state.touch && /pointer: coarse|max-width/.test(query),
    media: query, onchange: null, addListener() {}, removeListener() {}, addEventListener() {}, removeEventListener() {}, dispatchEvent: () => false }))
  vi.stubGlobal('URL', Object.assign(class extends URL {}, { createObjectURL: (blob: Blob) => {
    state.downloads.push(blob); return 'blob:synthetic-download'
  }, revokeObjectURL() {} }))
  vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(() => {})
})
afterEach(() => vi.unstubAllGlobals())

export async function mountDomainPage(Page: ComponentType, id: keyof typeof definitions, touch = false, testRows?: Record<string, unknown>[]) {
  cleanup()
  state.touch = touch
  const schema = definitions[id] as unknown as ScreenDefinition
  const row: Record<string, unknown> = { id: 'synthetic-record', version: 1 }
  for (const table of schema.tables ?? []) for (const col of table.columns) {
    row[col.key] = col.numeric ? 5 : col.renderKind === 'date' ? '2026-10-27' : col.renderKind === 'boolean' ? true : `SYNTHETIC-${col.key}`
  }
  const rows = testRows ?? [row]
  state.get.mockImplementation(async (url: string) => {
    if (url === `/api/v1/masks/${id.replaceAll('/', '__')}/screen-definition`) return { data: schema }
    if (url.startsWith(`/api/v1/masks/${encodeURIComponent(id)}/data/`)) return { data: { data: { items: rows, total: rows.length } } }
    if (url.startsWith('/api/v1/ux/overlays/')) return { data: { screen_id: id, overlay: {} } }
    if (schema.dataSources?.some(source => url.startsWith(source.endpoint))) return { data: { items: rows, total: rows.length } }
    throw new Error(`Unmapped HTTP contract: ${url}`)
  })
  const client = new QueryClient({ defaultOptions: { queries: { retry: false }, mutations: { retry: false } } })
  const mounted = render(createElement(QueryClientProvider, { client }, createElement(MemoryRouter, null, createElement(Page))))
  await waitFor(() => expect(mounted.container.querySelector('[data-screen-definition]')).toHaveAttribute('data-screen-definition', id))
  expect(state.get).toHaveBeenCalledWith(`/api/v1/masks/${id.replaceAll('/', '__')}/screen-definition`, expect.anything())
  return { ...mounted, schema, row }
}

export async function expectSearchWorkArea(label: string) {
  const input = await screen.findByRole('searchbox', { name: `Suche in ${label}` })
  expect(input).toHaveClass('min-h-touch')
  const table = await screen.findByTestId('virtual-data-table')
  expect(input.compareDocumentPosition(table) & Node.DOCUMENT_POSITION_FOLLOWING).toBeTruthy()
  fireEvent.change(input, { target: { value: 'SYNTHETIC' } })
  await waitFor(() => expect(state.get.mock.calls.some(([url]) => String(url).includes('q=SYNTHETIC'))).toBe(true))
  if (state.touch) {
    expect(within(table).queryByRole('columnheader')).not.toBeInTheDocument()
    expect(table.querySelector('[data-index="0"]')).toBeInTheDocument()
  } else {
    expect(within(table).getAllByRole('columnheader').length).toBeGreaterThan(0)
  }
}

export async function expectCsvDownload() {
  const button = screen.getByRole('button', { name: 'CSV-Export' })
  expect(button).toHaveClass('min-h-touch')
  fireEvent.click(button)
  await waitFor(() => expect(state.downloads).toHaveLength(1))
  const csv = await new Promise<string>((resolve, reject) => {
    const reader = new FileReader(); reader.onload = () => resolve(String(reader.result)); reader.onerror = reject
    reader.readAsText(state.downloads[0])
  })
  expect(csv).toContain('SYNTHETIC-')
  expect(csv.split('\n').length).toBeGreaterThan(1)
  return csv
}

export { state }
