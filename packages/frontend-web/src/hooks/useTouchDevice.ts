/**
 * useTouchDevice — erkennt Touch- oder schmale Geräte (Tablet/Smartphone).
 *
 * Zentraler Guard statt ad-hoc-Abfragen. Defensiv gegen:
 *  - SSR (window undefined)
 *  - JSDOM / Testumgebungen ohne matchMedia
 *  - Browser, die matchMedia werfen statt false zurückzugeben
 *
 * Schmale Viewports (< 768 px) zählen mit: Außendienst und Waage bedienen
 * oft ein Handy im Browser, ohne dass `(pointer: coarse)` gesetzt ist.
 */
import { useEffect, useState } from 'react'

export function readTouchDevice(): boolean {
  if (typeof window === 'undefined') return false
  try {
    if (typeof window.matchMedia === 'function') {
      if (window.matchMedia('(pointer: coarse)').matches) return true
      if (window.matchMedia('(max-width: 767px)').matches) return true
    }
  } catch {
    // matchMedia fehlt oder wirft — Viewport-Breite als Rückfall.
  }
  return typeof window.innerWidth === 'number' && window.innerWidth > 0 && window.innerWidth < 768
}

export function useTouchDevice(): boolean {
  const [isTouch, setIsTouch] = useState(readTouchDevice)

  useEffect(() => {
    const update = (): void => {
      setIsTouch(readTouchDevice())
    }
    const media: MediaQueryList[] = []
    try {
      if (typeof window.matchMedia === 'function') {
        media.push(window.matchMedia('(pointer: coarse)'))
        media.push(window.matchMedia('(max-width: 767px)'))
      }
    } catch {
      // matchMedia fehlt oder wirft — nur resize als Rückfall.
    }
    media.forEach((mq) => {
      if (typeof mq.addEventListener === 'function') mq.addEventListener('change', update)
      else mq.addListener(update)
    })
    window.addEventListener('resize', update)
    update()
    return () => {
      media.forEach((mq) => {
        if (typeof mq.removeEventListener === 'function') mq.removeEventListener('change', update)
        else mq.removeListener(update)
      })
      window.removeEventListener('resize', update)
    }
  }, [])

  return isTouch
}
