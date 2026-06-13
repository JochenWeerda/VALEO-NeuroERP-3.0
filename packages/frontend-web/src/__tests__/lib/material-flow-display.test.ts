import { describe, expect, it } from 'vitest'

import {
  flowEdgeStatusGermanLabel,
  flowNodeStatusBorderClass,
  flowNodeStatusGermanLabel,
  qsStatusGermanLabel,
  qsStatusToBadgeVariant,
} from '@/lib/material-flow-display'

describe('material-flow-display', () => {
  it('maps qs_status to badge variant', () => {
    expect(qsStatusToBadgeVariant('frei')).toBe('secondary')
    expect(qsStatusToBadgeVariant('gesperrt')).toBe('destructive')
    expect(qsStatusToBadgeVariant('in_pruefung')).toBe('outline')
  })

  it('maps qs_status to German labels', () => {
    expect(qsStatusGermanLabel('in_pruefung')).toBe('in Prüfung')
    expect(qsStatusGermanLabel(undefined)).toBe('frei')
  })

  it('maps node status to labels and border classes', () => {
    expect(flowNodeStatusGermanLabel('maintenance')).toBe('Wartung')
    expect(flowNodeStatusBorderClass('blocked')).toContain('red')
    expect(flowNodeStatusBorderClass('active')).toContain('emerald')
  })

  it('maps edge status to German labels', () => {
    expect(flowEdgeStatusGermanLabel('open')).toBe('offen')
    expect(flowEdgeStatusGermanLabel('blocked')).toBe('gesperrt')
  })
})
