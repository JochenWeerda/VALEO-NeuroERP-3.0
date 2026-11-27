import { act, renderHook, waitFor } from '@testing-library/react'
import { expect, it, vi } from 'vitest'
import { useIbanLookup } from '@/hooks/useIbanLookup'

const mocks = vi.hoisted(() => ({ lookup: vi.fn() }))
vi.mock('@/lib/utils/iban-validator', () => ({
  validateIBAN: () => true,
  formatIBAN: (s: string) => s,
  lookupIBAN: mocks.lookup,
}))

const IBAN_A = 'DE89370400440532013000'
const IBAN_B = 'DE02370400440532013001'

it('enriches once for a completed IBAN without duplicate lookups', async () => {
  mocks.lookup.mockResolvedValue({ valid: true, bank_name: 'Bank', bic: 'BIC123' })
  const onSuccess = vi.fn()
  const { result } = renderHook(() => useIbanLookup({ onSuccess }))

  await act(async () => {
    await result.current.performLookup(IBAN_A)
  })

  await waitFor(() => expect(result.current.lookupData?.bic).toBe('BIC123'))
  expect(result.current.lookupData?.bank_name).toBe('Bank')
  expect(mocks.lookup).toHaveBeenCalledTimes(1)
  expect(onSuccess).toHaveBeenCalledWith(expect.objectContaining({ bic: 'BIC123' }))
})

it('ignores a late result for the previous IBAN', async () => {
  let resolveOld!: (result: { valid: boolean; bank_name: string; bic: string }) => void
  mocks.lookup.mockReset()
    .mockImplementationOnce(() => new Promise(resolve => { resolveOld = resolve }))
    .mockResolvedValue({ valid: true, bank_name: 'Neue Bank', bic: 'NEU' })

  const { result } = renderHook(() => useIbanLookup())

  void act(() => {
    void result.current.performLookup(IBAN_A)
  })
  await waitFor(() => expect(mocks.lookup).toHaveBeenCalledTimes(1))

  await act(async () => {
    await result.current.performLookup(IBAN_B)
  })
  await waitFor(() => expect(result.current.lookupData?.bic).toBe('NEU'))

  await act(async () => {
    resolveOld({ valid: true, bank_name: 'Alte Bank', bic: 'ALT' })
  })
  await new Promise(resolve => setTimeout(resolve, 0))

  expect(result.current.lookupData?.bic).toBe('NEU')
  expect(result.current.lookupData?.bank_name).not.toBe('Alte Bank')
})
