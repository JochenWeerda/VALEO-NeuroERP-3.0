import { useCallback, useEffect, useMemo, useState } from 'react'

const STORAGE_KEY = 'valeo.start.pinnedTiles'
const SYNC_EVENT = 'valeo:pinned-tiles-changed'

function readPinnedTiles(): string[] {
  if (typeof window === 'undefined') {
    return []
  }

  const rawValue = window.localStorage.getItem(STORAGE_KEY)
  if (!rawValue) {
    return []
  }

  try {
    const parsed = JSON.parse(rawValue)
    if (!Array.isArray(parsed)) {
      return []
    }
    return parsed.filter((value): value is string => typeof value === 'string')
  } catch {
    return []
  }
}

export function usePinnedTiles() {
  const [pinnedTileIds, setPinnedTileIds] = useState<string[]>(() => readPinnedTiles())

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }

    const syncFromStorage = (): void => {
      const fresh = readPinnedTiles()
      setPinnedTileIds((current) => {
        if (JSON.stringify(current) === JSON.stringify(fresh)) {
          return current
        }
        return fresh
      })
    }

    const onStorage = (event: StorageEvent): void => {
      if (event.key === STORAGE_KEY) {
        syncFromStorage()
      }
    }

    const onSync = (): void => {
      syncFromStorage()
    }

    window.addEventListener('storage', onStorage)
    window.addEventListener(SYNC_EVENT, onSync)
    return () => {
      window.removeEventListener('storage', onStorage)
      window.removeEventListener(SYNC_EVENT, onSync)
    }
  }, [])

  useEffect(() => {
    if (typeof window === 'undefined') {
      return
    }
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(pinnedTileIds))
    window.dispatchEvent(new Event(SYNC_EVENT))
  }, [pinnedTileIds])

  const pinnedSet = useMemo(() => new Set(pinnedTileIds), [pinnedTileIds])

  const isPinned = useCallback((tileId: string): boolean => pinnedSet.has(tileId), [pinnedSet])

  const togglePin = useCallback((tileId: string): void => {
    setPinnedTileIds((current) => {
      if (current.includes(tileId)) {
        return current.filter((entry) => entry !== tileId)
      }
      return [...current, tileId]
    })
  }, [])

  return {
    pinnedTileIds,
    isPinned,
    togglePin,
  }
}
