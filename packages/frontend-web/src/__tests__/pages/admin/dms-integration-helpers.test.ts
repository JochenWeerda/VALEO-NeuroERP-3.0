import { afterEach, describe, expect, it, vi } from 'vitest'
import {
  formatBootstrapSummary,
  isNonEmptyString,
  openExternal,
} from '@/pages/admin/setup/dms-integration-legacy'

describe('dms-integration helpers', () => {
  afterEach(() => {
    vi.restoreAllMocks()
  })

  it('prüft Strings und formatiert Bootstrap-Zusammenfassung', () => {
    expect(isNonEmptyString(' a ')).toBe(true)
    expect(isNonEmptyString('')).toBe(false)
    expect(isNonEmptyString('   ')).toBe(false)
    expect(isNonEmptyString(1)).toBe(false)
    expect(formatBootstrapSummary({})).toBe('0 Dokumenttypen, 0 Metadaten, 0 Bindings, 0 aktualisiert')
    expect(formatBootstrapSummary({
      ok: true,
      document_types: 2,
      metadata_types: 3,
      created: 4,
      updated: 1,
    })).toBe('2 Dokumenttypen, 3 Metadaten, 4 Bindings, 1 aktualisiert')
  })

  it('öffnet externe URLs nur bei nicht-leerem Ziel', () => {
    const open = vi.spyOn(window, 'open').mockImplementation(() => null)
    openExternal(undefined)
    openExternal('  ')
    expect(open).not.toHaveBeenCalled()
    openExternal('https://dms.example')
    expect(open).toHaveBeenCalledWith('https://dms.example', '_blank', 'noopener')
  })
})
