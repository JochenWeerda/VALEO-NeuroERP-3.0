import { describe, it, expect, vi } from 'vitest'
import { renderHook, act } from '@testing-library/react'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import type { ScreenDefinition } from '@/components/mask-builder/schema'

const SCREEN: ScreenDefinition = {
  schemaVersion: 1,
  id: 'test/form',
  domain: 'crm',
  mode: 'detail',
  title: 'Test',
  fields: [
    { key: 'name', label: 'Name', type: 'text', required: true },
    { key: 'email', label: 'E-Mail', type: 'text' },
  ],
}

describe('useUniversalFormState', () => {
  it('initializes with given values', () => {
    const { result } = renderHook(() =>
      useUniversalFormState({ screen: SCREEN, initialValues: { name: 'Müller' } }),
    )
    expect(result.current.values['name']).toBe('Müller')
    expect(result.current.dirtyState.isDirty).toBe(false)
  })

  it('marks field dirty on setValue', () => {
    const { result } = renderHook(() => useUniversalFormState({ screen: SCREEN }))
    act(() => result.current.setValue('name', 'Schmidt'))
    expect(result.current.values['name']).toBe('Schmidt')
    expect(result.current.dirtyState.isDirty).toBe(true)
    expect(result.current.dirtyState.dirtyFields.has('name')).toBe(true)
  })

  it('blocking error when required field empty', () => {
    const { result } = renderHook(() => useUniversalFormState({ screen: SCREEN, initialValues: { name: '' } }))
    expect(result.current.validationPlan.hasBlockingErrors).toBe(true)
    expect(result.current.fieldErrors['name']).toHaveLength(1)
    expect(result.current.fieldErrors['name'][0].severity).toBe('blocking')
  })

  it('no error when required field has value', () => {
    const { result } = renderHook(() =>
      useUniversalFormState({ screen: SCREEN, initialValues: { name: 'Test' } }),
    )
    expect(result.current.validationPlan.hasBlockingErrors).toBe(false)
    expect(result.current.fieldErrors['name']).toBeUndefined()
  })

  it('canSubmit is false when hasBlockingErrors', () => {
    const { result } = renderHook(() => useUniversalFormState({ screen: SCREEN }))
    act(() => result.current.setValue('email', 'x@y.de'))
    expect(result.current.canSubmit).toBe(false) // name still missing
  })

  it('canSubmit is true when valid and dirty', () => {
    const { result } = renderHook(() =>
      useUniversalFormState({ screen: SCREEN, initialValues: { name: 'X' } }),
    )
    act(() => result.current.setValue('name', 'Updated'))
    expect(result.current.canSubmit).toBe(true)
  })

  it('submit calls onSubmit and clears dirty state on success', async () => {
    const onSubmit = vi.fn().mockResolvedValue(undefined)
    const { result } = renderHook(() =>
      useUniversalFormState({ screen: SCREEN, initialValues: { name: 'Start' }, onSubmit }),
    )
    act(() => result.current.setValue('name', 'Changed'))
    await act(async () => { await result.current.submit() })
    expect(onSubmit).toHaveBeenCalledWith({ name: 'Changed' })
    expect(result.current.submitState).toBe('success')
    expect(result.current.dirtyState.isDirty).toBe(false)
  })

  it('submit sets error state on failure', async () => {
    const onSubmit = vi.fn().mockRejectedValue(new Error('Server error'))
    const { result } = renderHook(() =>
      useUniversalFormState({ screen: SCREEN, initialValues: { name: 'X' }, onSubmit }),
    )
    act(() => result.current.setValue('name', 'Changed'))
    await act(async () => { await result.current.submit() })
    expect(result.current.submitState).toBe('error')
    expect(result.current.submitError).toBe('Server error')
  })

  it('resetForm restores to initial values', () => {
    const { result } = renderHook(() =>
      useUniversalFormState({ screen: SCREEN, initialValues: { name: 'Init' } }),
    )
    act(() => result.current.setValue('name', 'Changed'))
    act(() => result.current.resetForm())
    expect(result.current.values['name']).toBe('Init')
    expect(result.current.dirtyState.isDirty).toBe(false)
  })

  it('submit is blocked when already submitting (no double submit)', async () => {
    let resolve: () => void
    const onSubmit = vi.fn().mockReturnValue(new Promise<void>((r) => { resolve = r }))
    const { result } = renderHook(() =>
      useUniversalFormState({ screen: SCREEN, initialValues: { name: 'X' }, onSubmit }),
    )
    act(() => result.current.setValue('name', 'Y'))
    // Fire two submits in parallel
    let p1: Promise<void>
    let p2: Promise<void>
    act(() => {
      p1 = result.current.submit()
      p2 = result.current.submit()
    })
    resolve!()
    await act(async () => { await Promise.all([p1!, p2!]) })
    expect(onSubmit).toHaveBeenCalledTimes(1)
  })

  // Sichtpruefung 07.10.2026: Eine frisch geoeffnete Maske meldete "Pflichtfeld"
  // fuer Felder, die noch niemand angefasst hatte. Die Pruefung bleibt vollstaendig
  // (validationPlan, fieldErrors); nur die Anzeige wartet auf Beruehrung oder Versuch.
  describe('sichtbare Fehler', () => {
    it('zeigt beim Oeffnen keinen Fehler, sperrt aber trotzdem', () => {
      const { result } = renderHook(() => useUniversalFormState({ screen: SCREEN, initialValues: { name: '' } }))
      expect(result.current.validationPlan.hasBlockingErrors).toBe(true)
      expect(result.current.visibleFieldErrors).toEqual({})
    })

    it('zeigt den Fehler eines bearbeiteten Feldes', () => {
      const { result } = renderHook(() => useUniversalFormState({ screen: SCREEN, initialValues: { name: 'A' } }))
      act(() => result.current.setValue('name', ''))
      expect(result.current.visibleFieldErrors?.name).toHaveLength(1)
    })

    it('zeigt alle Fehler nach revealErrors und nach einem Absendeversuch', async () => {
      const onSubmit = vi.fn()
      const { result } = renderHook(() => useUniversalFormState({ screen: SCREEN, initialValues: { name: '' }, onSubmit }))
      act(() => result.current.revealErrors?.())
      expect(result.current.visibleFieldErrors?.name).toHaveLength(1)
      act(() => result.current.resetForm())
      expect(result.current.visibleFieldErrors).toEqual({})
      await act(async () => { await result.current.submit() })
      expect(onSubmit).not.toHaveBeenCalled()
      expect(result.current.visibleFieldErrors?.name).toHaveLength(1)
    })
  })
})
