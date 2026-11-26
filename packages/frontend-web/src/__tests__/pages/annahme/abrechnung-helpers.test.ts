import { AxiosError } from 'axios'
import { describe, expect, it } from 'vitest'
import {
  approvalStatusLabel,
  deductionModeLabel,
  deductionTypeLabel,
  describeApiError,
  settlementStatusLabel,
} from '@/pages/annahme/abrechnung-legacy'

describe('abrechnung helpers (new-code coverage)', () => {
  it('mappt Settlement-/Freigabe-/Abzugs-Labels inkl. Defaults', () => {
    expect(settlementStatusLabel('draft')).toBe('Entwurf')
    expect(settlementStatusLabel('posted')).toBe('verbucht')
    expect(settlementStatusLabel('cancelled')).toBe('storniert')
    expect(settlementStatusLabel('other')).toBe('other')

    expect(approvalStatusLabel('ENTWURF')).toBe('Entwurf')
    expect(approvalStatusLabel('ZUR_FREIGABE')).toBe('Zur Freigabe')
    expect(approvalStatusLabel('TEILWEISE_FREIGEGEBEN')).toBe('Teilweise freigegeben')
    expect(approvalStatusLabel('FREIGEGEBEN')).toBe('Freigegeben')
    expect(approvalStatusLabel('ABGELEHNT')).toBe('Abgelehnt')
    expect(approvalStatusLabel('VERBUCHT')).toBe('Verbucht')
    expect(approvalStatusLabel('X')).toBe('X')

    expect(deductionTypeLabel('drying')).toBe('Trocknung')
    expect(deductionTypeLabel('cleaning')).toBe('Reinigung')
    expect(deductionTypeLabel('freight')).toBe('Fracht')
    expect(deductionTypeLabel('other')).toBe('Sonstiges')
    expect(deductionTypeLabel('custom')).toBe('custom')

    expect(deductionModeLabel('per_ton')).toBe('je t')
    expect(deductionModeLabel('fixed')).toBe('fix')
    expect(deductionModeLabel('pct')).toBe('pct')
  })

  it('extrahiert API-Fehlerdetails aus Axios und Fallbacks', () => {
    const withString = new AxiosError('boom')
    withString.response = { data: { detail: 'Zeile gesperrt' }, status: 400, statusText: 'Bad', headers: {}, config: {} as never }
    expect(describeApiError(withString)).toBe('Zeile gesperrt')

    const withMessage = new AxiosError('boom')
    withMessage.response = {
      data: { detail: { message: 'Konflikt' } },
      status: 409,
      statusText: 'Conflict',
      headers: {},
      config: {} as never,
    }
    expect(describeApiError(withMessage)).toBe('Konflikt')

    const withObject = new AxiosError('boom')
    withObject.response = { data: { detail: { code: 'x' } }, status: 500, statusText: 'Err', headers: {}, config: {} as never }
    expect(describeApiError(withObject)).toBe('boom')

    expect(describeApiError(new Error('lokal'))).toBe('lokal')
    expect(describeApiError('x')).toBe('Anfrage fehlgeschlagen')
  })
})
