import { afterEach, describe, expect, it, vi } from 'vitest'
import { renderHook, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { apiClient } from '@/lib/api-client'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { validateScreenDefinition } from '@/components/mask-builder/schema'
import { useUniversalMaskRuntime } from '@/components/mask-builder/runtime/useUniversalMaskRuntime'

const definition: ScreenDefinition = {
  schemaVersion: 1,
  id: 'fibu/anlage',
  domain: 'finance',
  mode: 'detail',
  title: 'Anlage',
  identityField: 'asset_number',
  dataSources: [{ key: 'entity', endpoint: '/api/v1/finance/asset-accounting/assets/{entity_id}' }],
  entityProjection: {
    id: 'asset.id',
    asset_number: 'asset.asset_number',
    description: 'asset.description',
    acquisition_cost: 'asset.acquisition_cost',
  },
  tabs: [{ key: 'kopf', label: 'Kopf', fields: [
    { key: 'id', label: 'ID', type: 'text' },
    { key: 'asset_number', label: 'Inventar-Nr.', type: 'text' },
    { key: 'description', label: 'Bezeichnung', type: 'text' },
    { key: 'acquisition_cost', label: 'Anschaffungswert', type: 'currency' },
  ] }],
}

afterEach(() => vi.restoreAllMocks())

describe('shared entity projection', () => {
  it('binds the projected form fields to the shared secured mask read', async () => {
    const requests: string[] = []
    vi.spyOn(apiClient, 'get').mockImplementation(async (url) => {
      requests.push(String(url))
      if (String(url).startsWith('/api/v1/ux/overlays/')) {
        return { data: { screen_id: 'fibu/anlage', schema_version: 1, overlay: {} } } as never
      }
      return { data: { screen_id: 'fibu/anlage', source_key: 'entity', data: {
        id: 'asset-42', asset_number: 'AN-42', description: 'Muehle', acquisition_cost: '1200.00',
      } } } as never
    })
    const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
    const wrapper = ({ children }: { children: ReactNode }) => (
      <QueryClientProvider client={client}>{children}</QueryClientProvider>
    )
    const { result } = renderHook(() => useUniversalMaskRuntime({
      screenId: definition.id, entityId: 'asset-42', schema: definition,
    }), { wrapper })

    await waitFor(() => expect(result.current.entityData).toEqual({
      id: 'asset-42', asset_number: 'AN-42', description: 'Muehle', acquisition_cost: '1200.00',
    }))
    expect(result.current.binding?.entityBinding.sharedEntityEndpoint)
      .toBe('/api/v1/masks/fibu%2Fanlage/data/entity?entity_id=asset-42')
    expect(requests).toContain('/api/v1/masks/fibu%2Fanlage/data/entity?entity_id=asset-42')
    expect(requests).not.toContain('/api/v1/finance/asset-accounting/assets/asset-42')
  })

  it('rejects unsafe or undeclared projection fields at the schema boundary', () => {
    expect(validateScreenDefinition(definition)).toEqual([])
    const invalid: ScreenDefinition = {
      ...definition, entityProjection: { ...definition.entityProjection, private_note: 'asset.__proto__' },
    }
    expect(validateScreenDefinition(invalid)).toContain('entityProjection has an invalid field or path: private_note')
  })
})
