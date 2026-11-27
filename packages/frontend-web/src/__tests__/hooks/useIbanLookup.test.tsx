import { act, renderHook, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { useIbanLookup } from '@/hooks/useIbanLookup'

const lookupIBAN = vi.hoisted(() => vi.fn())
vi.mock('@/lib/utils/iban-validator', async (importOriginal) => {
  const actual = await importOriginal<typeof import('@/lib/utils/iban-validator')>()
  return {
    ...actual,
    lookupIBAN: (...args: unknown[]) => lookupIBAN(...args),
  }
})

describe('useIbanLookup', () => {
  beforeEach(() => {
    lookupIBAN.mockReset()
  })

  it('lehnt kurze IBANs ab und meldet ungültige/fehlerhafte Lookups', async () => {
    const onError = vi.fn()
    const onSuccess = vi.fn()
    const { result } = renderHook(() => useIbanLookup({ onError, onSuccess }))

    await act(async () => {
      expect(await result.current.performLookup('')).toBeNull()
      expect(await result.current.performLookup('DE89')).toBeNull()
    })

    lookupIBAN.mockResolvedValueOnce({ valid: false, message: 'Ungültig' })
    await act(async () => {
      await result.current.performLookup('DE89370400440532013000')
    })
    expect(onError).toHaveBeenCalledWith(expect.objectContaining({ message: 'Ungültig' }))

    lookupIBAN.mockRejectedValueOnce('network')
    await act(async () => {
      expect(await result.current.performLookup('DE89370400440532013000')).toBeNull()
    })
    expect(onError).toHaveBeenCalledWith(expect.objectContaining({ message: 'Failed to lookup IBAN' }))

    lookupIBAN.mockResolvedValueOnce({ valid: true, bankName: 'Testbank' })
    await act(async () => {
      const formatted = await result.current.handleIbanChange('de89 3704 0044 0532 0130 00')
      expect(formatted).toContain('DE89')
    })
    await waitFor(() => expect(onSuccess).toHaveBeenCalled())

    act(() => {
      result.current.reset()
    })
    expect(result.current.lookupData).toBeNull()
    expect(result.current.isLoading).toBe(false)
  })
})
