import { useCallback, useEffect, useRef, useState } from 'react'
import {
  EMPTY_LAUNCHPAD_OVERLAY,
  LAUNCHPAD_OVERLAY_STORAGE_KEY,
  launchpadOverlayStorageKey,
  parseLaunchpadOverlay,
  readLaunchpadOverlayRaw,
  writeLaunchpadOverlayRaw,
  type LaunchpadOverlay,
} from '@/app/navigation/launchpad-personalization'
import { useAuth } from '@/hooks/useAuth'
import { auth } from '@/lib/auth'
import { tenantFromToken } from '@/lib/tenant-from-token'

const SYNC_EVENT = 'valeo:launchpad-overlay-changed'

function readOverlay(sub?: string | null, tenantId?: string | null): LaunchpadOverlay {
  if (typeof window === 'undefined') {
    return { ...EMPTY_LAUNCHPAD_OVERLAY }
  }
  const raw = readLaunchpadOverlayRaw(window.localStorage, sub, tenantId)
  if (!raw) {
    return { ...EMPTY_LAUNCHPAD_OVERLAY }
  }
  try {
    return parseLaunchpadOverlay(JSON.parse(raw))
  } catch {
    return { ...EMPTY_LAUNCHPAD_OVERLAY }
  }
}

function writeOverlay(overlay: LaunchpadOverlay, sub?: string | null, tenantId?: string | null): void {
  if (typeof window === 'undefined') {
    return
  }
  writeLaunchpadOverlayRaw(window.localStorage, JSON.stringify(overlay), sub, tenantId)
  window.dispatchEvent(new Event(SYNC_EVENT))
}

export function useLaunchpadPersonalization() {
  const { user } = useAuth()
  const sub = user?.sub
  const tenantId = tenantFromToken(auth.getAccessToken())
  const [overlay, setOverlayState] = useState<LaunchpadOverlay>(() => readOverlay(sub, tenantId))
  const overlayRef = useRef(overlay)
  const persistAfterCommit = useRef(false)
  overlayRef.current = overlay

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }
    const sync = (): void => {
      const fresh = readOverlay(sub, tenantId)
      setOverlayState((current) =>
        JSON.stringify(current) === JSON.stringify(fresh) ? current : fresh,
      )
    }
    const watched = new Set([
      launchpadOverlayStorageKey(sub, tenantId),
      launchpadOverlayStorageKey(sub),
      LAUNCHPAD_OVERLAY_STORAGE_KEY,
    ])
    const onStorage = (event: StorageEvent): void => {
      if (event.key != null && watched.has(event.key)) {
        sync()
      }
    }
    sync()
    window.addEventListener('storage', onStorage)
    window.addEventListener(SYNC_EVENT, sync)
    return () => {
      window.removeEventListener('storage', onStorage)
      window.removeEventListener(SYNC_EVENT, sync)
    }
  }, [sub, tenantId])

  useEffect(() => {
    if (!persistAfterCommit.current) {
      return
    }
    persistAfterCommit.current = false
    writeOverlay(overlay, sub, tenantId)
  }, [overlay, sub, tenantId])

  const setOverlay = useCallback((next: LaunchpadOverlay | ((current: LaunchpadOverlay) => LaunchpadOverlay)) => {
    const resolved = typeof next === 'function' ? next(overlayRef.current) : next
    if (resolved === overlayRef.current) {
      return
    }
    overlayRef.current = resolved
    persistAfterCommit.current = true
    setOverlayState(resolved)
  }, [])

  return { overlay, setOverlay }
}
