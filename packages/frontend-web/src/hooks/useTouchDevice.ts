/**
 * useTouchDevice — erkennt Touch-Gerät (Tablet/Smartphone) sicher.
 *
 * Zentraler Hook statt ad-hoc-Guards in Komponenten. Defensiv gegen:
 *  - SSR (window undefined)
 *  - JSDOM / Testumgebungen ohne matchMedia
 *  - Browser, die matchMedia werfen statt false zurückzugeben
 */
export function useTouchDevice(): boolean {
  if (typeof window === 'undefined') return false
  if (typeof window.matchMedia !== 'function') return false
  try {
    return window.matchMedia('(pointer: coarse)').matches
  } catch {
    return false
  }
}
