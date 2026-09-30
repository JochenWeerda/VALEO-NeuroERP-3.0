export type NativeDetailLoadState = 'empty' | 'error' | 'loading' | 'ready'

/** ScreenDefinition and entity fetch must not leave the mask on “Wird geladen” forever. */
export function nativeDetailLoadState(input: {
  entityId?: string
  schemaError: unknown
  entityError: unknown
  hasPlan: boolean
  schemaFetching: boolean
  hasSchema: boolean
}): NativeDetailLoadState {
  if (!input.entityId) return 'empty'
  if (input.schemaError || input.entityError) return 'error'
  if (input.hasPlan) return 'ready'
  if (input.schemaFetching) return 'loading'
  if (!input.hasSchema) return 'error'
  return 'loading'
}
