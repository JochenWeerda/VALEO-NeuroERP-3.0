import { useBlocker } from '@/app/routing/react-router-compat'

/**
 * Blockiert die Navigation, wenn hasDirtyState true ist (ungespeicherte Änderungen).
 * Die aufrufende Seite soll bei blocker.state === 'blocked' einen
 * LeaveConfirmDialog anzeigen (Speichern / Verwerfen / Abbrechen).
 */
export function useUnsavedChanges(hasDirtyState: boolean): ReturnType<typeof useBlocker> {
  return useBlocker(
    ({ currentLocation, nextLocation }) =>
      Boolean(hasDirtyState && currentLocation.pathname !== nextLocation.pathname),
  )
}
