import { useCallback, useEffect, useState } from 'react'
import {
  EMPTY_LAUNCHPAD_OVERLAY,
  LAUNCHPAD_OVERLAY_STORAGE_KEY,
  parseLaunchpadOverlay,
  type LaunchpadOverlay,
} from '@/app/navigation/launchpad-personalization'

const SYNC_EVENT = 'valeo:launchpad-overlay-changed'

function readOverlay(): LaunchpadOverlay {
  if (typeof window === 'undefined') {
    return { ...EMPTY_LAUNCHPAD_OVERLAY }
  }
  const raw = window.localStorage.getItem(LAUNCHPAD_OVERLAY_STORAGE_KEY)
  if (!raw) {
    return { ...EMPTY_LAUNCHPAD_OVERLAY }
  }
  try {
    return parseLaunchpadOverlay(JSON.parse(raw))
  } catch {
    return { ...EMPTY_LAUNCHPAD_OVERLAY }
  }
}

function writeOverlay(overlay: LaunchpadOverlay): void {
  if (typeof window === 'undefined') {
    return
  }
  window.localStorage.setItem(LAUNCHPAD_OVERLAY_STORAGE_KEY, JSON.stringify(overlay))
  window.dispatchEvent(new Event(SYNC_EVENT))
}

export function useLaunchpadPersonalization() {
  const [overlay, setOverlayState] = useState<LaunchpadOverlay>(() => readOverlay())

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }
    const sync = (): void => {
      const fresh = readOverlay()
      setOverlayState((current) =>
        JSON.stringify(current) === JSON.stringify(fresh) ? current : fresh,
      )
    }
    const onStorage = (event: StorageEvent): void => {
      if (event.key === LAUNCHPAD_OVERLAY_STORAGE_KEY) {
        sync()
      }
    }
    window.addEventListener('storage', onStorage)
    window.addEventListener(SYNC_EVENT, sync)
    return () => {
      window.removeEventListener('storage', onStorage)
      window.removeEventListener(SYNC_EVENT, sync)
    }
  }, [])

  const setOverlay = useCallback((next: LaunchpadOverlay | ((current: LaunchpadOverlay) => LaunchpadOverlay)) => {
    setOverlayState((current) => {
      const resolved = typeof next === 'function' ? next(current) : next
      writeOverlay(resolved)
      return resolved
    })
  }, [])

  return { overlay, setOverlay }
}
