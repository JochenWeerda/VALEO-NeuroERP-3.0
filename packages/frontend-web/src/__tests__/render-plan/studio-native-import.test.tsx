import { afterEach, expect, it, vi } from 'vitest'
import { cleanup, render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { StudioNativeImport } from '@/features/screen-studio/StudioNativeImport'
import { apiClient } from '@/lib/api-client'

vi.mock('@/lib/auth', () => ({ auth: { getAccessToken: () => null, getUser: () => ({ sub: 'synthetic' }) } }))
afterEach(() => { cleanup(); vi.restoreAllMocks() })

it('imports the displayed source revision without selecting a tenant or activating it', async () => {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const user = userEvent.setup()
  const imported = vi.fn()
  vi.spyOn(apiClient, 'get').mockResolvedValue({ data: { total: 1,
    items: [{ screen_id: 'agrar/duenger', title: 'Düngemittel', source_hash: 'a'.repeat(64) }] } } as never)
  const post = vi.spyOn(apiClient, 'post').mockResolvedValue({ data: { id: 'draft', status: 'draft' } } as never)
  render(<QueryClientProvider client={client}><StudioNativeImport onImported={imported} /></QueryClientProvider>)
  await screen.findByRole('option', { name: 'Düngemittel' })
  await user.selectOptions(screen.getByLabelText('Vorhandene Maske'), 'agrar/duenger')
  await user.click(screen.getByRole('button', { name: 'Als versionierte Ausgangsfassung übernehmen' }))
  expect(post).toHaveBeenCalledWith('/api/v1/studio/native-imports', {
    screen_id: 'agrar/duenger', expected_source_hash: 'a'.repeat(64), idempotency_key: expect.any(String),
  })
  expect(imported).toHaveBeenCalledWith({ id: 'draft', status: 'draft' })
  expect(screen.getByText(/Die vorhandene Maske bleibt aktiv/)).toBeInTheDocument()
  client.clear()
})

it('retains its idempotency key after an uncertain network failure', async () => {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  const user = userEvent.setup()
  vi.spyOn(apiClient, 'get').mockResolvedValue({ data: { total: 1,
    items: [{ screen_id: 'agrar/duenger', title: 'Düngemittel', source_hash: 'a'.repeat(64) }] } } as never)
  const post = vi.spyOn(apiClient, 'post').mockRejectedValueOnce(new Error('network'))
    .mockResolvedValueOnce({ data: { id: 'draft' } } as never)
  render(<QueryClientProvider client={client}><StudioNativeImport onImported={vi.fn()} /></QueryClientProvider>)
  await screen.findByRole('option', { name: 'Düngemittel' })
  await user.selectOptions(screen.getByLabelText('Vorhandene Maske'), 'agrar/duenger')
  const button = screen.getByRole('button', { name: 'Als versionierte Ausgangsfassung übernehmen' })
  await user.click(button)
  await screen.findByRole('alert')
  await user.click(button)
  expect(post.mock.calls[0][1]).toEqual(post.mock.calls[1][1])
  client.clear()
})
