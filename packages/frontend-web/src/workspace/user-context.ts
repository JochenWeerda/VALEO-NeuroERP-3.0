import type { LaunchpadOverlay } from '@/app/navigation/launchpad-personalization'
import type { UserContext } from './types'

const EMPTY_CONTEXT: UserContext = {
  roles: [],
  scopes: [],
  favorites: [],
  pinned: [],
  surfaceLocked: false,
  locale: 'de',
}

export function emptyUserContext(overrides: Partial<UserContext> = {}): UserContext {
  return { ...EMPTY_CONTEXT, ...overrides }
}

/**
 * Liest Pin/Fixieren/Favoriten aus dem Launchpad-Overlay.
 * Rollen und Scopes kommen aus der Session, nie aus Kachel-Metadaten.
 */
export function userContextFromPersonalization(input: {
  overlay: LaunchpadOverlay
  roles?: string[]
  scopes?: string[]
  locale?: string
}): UserContext {
  const favorites = new Set<string>()
  for (const page of input.overlay.customPages) {
    for (const tileId of page.tileIds) {
      favorites.add(tileId)
    }
  }
  for (const tileId of Object.keys(input.overlay.tileLabels)) {
    favorites.add(tileId)
  }

  return {
    roles: [...(input.roles ?? [])],
    scopes: [...(input.scopes ?? [])],
    favorites: [...favorites],
    pinned: [...(input.overlay.pinnedTileIds ?? [])],
    surfaceLocked: input.overlay.surfaceLocked === true,
    locale: input.locale ?? 'de',
  }
}

export function hasRequiredScope(required: string[], granted: string[]): boolean {
  if (required.length === 0) {
    return true
  }
  if (granted.includes('admin:all')) {
    return true
  }
  return required.some((scope) => granted.includes(scope))
}
