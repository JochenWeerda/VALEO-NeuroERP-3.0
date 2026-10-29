import type { KeyboardEvent } from 'react'

/** Enter und Leertaste loesen an klickbaren Nicht-Schaltflaechen denselben Klick aus (Tastaturbedienung, WCAG 2.1.1). */
export function tastenKlick(event: KeyboardEvent<HTMLElement>): void {
  if (event.key !== 'Enter' && event.key !== ' ') return
  event.preventDefault()
  event.currentTarget.click()
}
