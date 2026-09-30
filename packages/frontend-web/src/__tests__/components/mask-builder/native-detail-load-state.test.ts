import { describe, expect, it } from 'vitest'
import { nativeDetailLoadState } from '@/components/mask-builder/native-detail-load-state'

describe('nativeDetailLoadState', () => {
  it('asks for a record when the route has no id', () => {
    expect(nativeDetailLoadState({
      schemaError: null,
      entityError: null,
      hasPlan: false,
      schemaFetching: false,
      hasSchema: false,
    })).toBe('empty')
  })

  it('shows a load error when the ScreenDefinition never arrives', () => {
    expect(nativeDetailLoadState({
      entityId: 'GAP00216',
      schemaError: null,
      entityError: null,
      hasPlan: false,
      schemaFetching: false,
      hasSchema: false,
    })).toBe('error')
  })

  it('keeps loading only while the schema request is in flight', () => {
    expect(nativeDetailLoadState({
      entityId: 'GAP00216',
      schemaError: null,
      entityError: null,
      hasPlan: false,
      schemaFetching: true,
      hasSchema: false,
    })).toBe('loading')
  })

  it('renders the mask once a plan exists, even if entity data is still coming', () => {
    expect(nativeDetailLoadState({
      entityId: 'GAP00216',
      schemaError: null,
      entityError: null,
      hasPlan: true,
      schemaFetching: false,
      hasSchema: true,
    })).toBe('ready')
  })
})
