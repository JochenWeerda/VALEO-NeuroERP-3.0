import { useCallback, useEffect, useRef, useState } from 'react'
import { useAuth } from '@/hooks/useAuth'
import { auth } from '@/lib/auth'
import { tenantFromToken } from '@/lib/tenant-from-token'
import type { WorkspacePersonalizationKeys } from '@/studio/workspace-composition'
import {
  COMPOSITION_OVERLAY_SYNC_EVENT,
  EMPTY_COMPOSITION_OVERLAY,
  compositionOverlayStorageKey,
  parseCompositionOverlay,
  readCompositionOverlayRaw,
  serializeCompositionOverlay,
  writeCompositionOverlayRaw,
  type CompositionPersonalizationOverlay,
} from '@/studio/workspace-composition-overlay'

function readOverlay(
  keys: WorkspacePersonalizationKeys,
  sub?: string | null,
  tenantId?: string | null,
): CompositionPersonalizationOverlay {
  if (typeof window === 'undefined') {
    return { ...EMPTY_COMPOSITION_OVERLAY }
  }
  const raw = readCompositionOverlayRaw(window.localStorage, keys.pinStorageKey, sub, tenantId)
  if (!raw) {
    return { ...EMPTY_COMPOSITION_OVERLAY }
  }
  try {
    return parseCompositionOverlay(JSON.parse(raw), keys)
  } catch {
    return { ...EMPTY_COMPOSITION_OVERLAY }
  }
}

function writeOverlay(
  overlay: CompositionPersonalizationOverlay,
  keys: WorkspacePersonalizationKeys,
  sub?: string | null,
  tenantId?: string | null,
): void {
  if (typeof window === 'undefined') {
    return
  }
  writeCompositionOverlayRaw(
    window.localStorage,
    serializeCompositionOverlay(overlay, keys),
    keys.pinStorageKey,
    sub,
    tenantId,
  )
  window.dispatchEvent(new Event(COMPOSITION_OVERLAY_SYNC_EVENT))
}

/**
 * Pin/Fixieren der Composition-Views — Schreiben erst im Effect nach dem Commit
 * (gleiches Muster wie useLaunchpadPersonalization).
 */
export function useWorkspaceCompositionOverlay(personalization: WorkspacePersonalizationKeys) {
  const { user } = useAuth()
  const sub = user?.sub
  const tenantId = tenantFromToken(auth.getAccessToken())
  const keysRef = useRef(personalization)
  keysRef.current = personalization

  const [overlay, setOverlayState] = useState<CompositionPersonalizationOverlay>(() =>
    readOverlay(personalization, sub, tenantId),
  )
  const overlayRef = useRef(overlay)
  const persistAfterCommit = useRef(false)
  overlayRef.current = overlay

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }
    const keys = keysRef.current
    const sync = (): void => {
      const fresh = readOverlay(keys, sub, tenantId)
      setOverlayState((current) =>
        JSON.stringify(current) === JSON.stringify(fresh) ? current : fresh,
      )
    }
    const watched = new Set([
      compositionOverlayStorageKey(keys.pinStorageKey, sub, tenantId),
      compositionOverlayStorageKey(keys.pinStorageKey, sub),
      compositionOverlayStorageKey(keys.pinStorageKey),
    ])
    const onStorage = (event: StorageEvent): void => {
      if (event.key != null && watched.has(event.key)) {
        sync()
      }
    }
    sync()
    window.addEventListener('storage', onStorage)
    window.addEventListener(COMPOSITION_OVERLAY_SYNC_EVENT, sync)
    return () => {
      window.removeEventListener('storage', onStorage)
      window.removeEventListener(COMPOSITION_OVERLAY_SYNC_EVENT, sync)
    }
  }, [personalization.pinStorageKey, sub, tenantId])

  useEffect(() => {
    if (!persistAfterCommit.current) {
      return
    }
    persistAfterCommit.current = false
    writeOverlay(overlay, keysRef.current, sub, tenantId)
  }, [overlay, sub, tenantId])

  const setOverlay = useCallback(
    (
      next:
        | CompositionPersonalizationOverlay
        | ((current: CompositionPersonalizationOverlay) => CompositionPersonalizationOverlay),
    ) => {
      const resolved = typeof next === 'function' ? next(overlayRef.current) : next
      if (resolved === overlayRef.current) {
        return
      }
      overlayRef.current = resolved
      persistAfterCommit.current = true
      setOverlayState(resolved)
    },
    [],
  )

  return { overlay, setOverlay }
}
