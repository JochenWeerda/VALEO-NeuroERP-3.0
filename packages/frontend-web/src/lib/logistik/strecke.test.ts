import { describe, expect, it } from 'vitest'
import { fahrtposition, streckeKm, streckeText, webfleetPunkt } from './strecke'

describe('Fahrtposition', () => {
  it('nimmt den Zielort, solange Webfleet keinen Fix A hat', () => {
    expect(webfleetPunkt(53_550_000, 8_580_000, 'L')).toBeNull()
    expect(fahrtposition(webfleetPunkt(53_100_000, 8_200_000, 'L'), [53.55, 8.58])).toEqual([53.55, 8.58])
  })

  it('behält eine Webfleet-Position', () => {
    expect(fahrtposition([53.1, 8.2], [48.1, 11.5])).toEqual([53.1, 8.2])
  })

  it('nennt einen einzelnen Zielort keine Strecke', () => {
    expect(streckeKm([[53.55, 8.58]])).toBeNull()
    expect(streckeText(null)).toBe('ohne Strecke')
  })
})
