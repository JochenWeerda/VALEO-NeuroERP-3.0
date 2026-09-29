import { describe, expect, it } from 'vitest'
import { matchesDatePreset } from '@/pages/crm/aktivitaeten'

const now = new Date('2026-09-17T12:00:00')

describe('matchesDatePreset', () => {
  it('laesst alle Termine durch', () => {
    expect(matchesDatePreset({ date: '2020-01-01', status: 'planned' }, 'all', now)).toBe(true)
  })

  it('filtert auf heute', () => {
    expect(matchesDatePreset({ date: '2026-09-17T08:00:00', status: 'planned' }, 'today', now)).toBe(true)
    expect(matchesDatePreset({ date: '2026-09-16T08:00:00', status: 'planned' }, 'today', now)).toBe(false)
  })

  it('filtert auf diese Woche ab Montag', () => {
    expect(matchesDatePreset({ date: '2026-09-14T08:00:00', status: 'planned' }, 'week', now)).toBe(true)
    expect(matchesDatePreset({ date: '2026-09-13T08:00:00', status: 'planned' }, 'week', now)).toBe(false)
  })

  it('filtert ueberfaellige offene Termine', () => {
    expect(matchesDatePreset({ date: '2026-09-16', status: 'planned' }, 'overdue', now)).toBe(true)
    expect(matchesDatePreset({ date: '2026-09-16', status: 'completed' }, 'overdue', now)).toBe(false)
    expect(matchesDatePreset({ date: '2026-09-17T18:00:00', status: 'planned' }, 'overdue', now)).toBe(false)
  })
})
