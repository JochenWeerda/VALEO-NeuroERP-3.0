import { fireEvent, render, renderHook, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FieldRenderer } from '@/components/mask-builder/renderers/FieldRenderer'
import type { ScreenFieldDefinition } from '@/components/mask-builder/schema'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'

// Bis 08.10.2026 fiel `multiselect` in das Textfeld durch; die Werte waren
// kommagetrennter Text. Jetzt eine Checkbox je Option, der Wert eine Liste.
const FELD: ScreenFieldDefinition = {
  key: 'verwendungen',
  label: 'Verwendung',
  type: 'multiselect',
  required: true,
  options: [
    { value: 'einkauf', label: 'Einkauf' },
    { value: 'fibu', label: 'Finanzbuchhaltung' },
    { value: 'dispo', label: 'Disposition' },
  ],
}

describe('FieldRenderer multiselect', () => {
  it('zeichnet eine Gruppe mit einer Checkbox je Option', () => {
    render(<FieldRenderer field={FELD} value={['fibu']} onChange={vi.fn()} voiceEnabled={false} />)
    expect(screen.getByRole('group', { name: 'Verwendung' })).toBeInTheDocument()
    expect(screen.getByRole('checkbox', { name: 'Finanzbuchhaltung' })).toBeChecked()
    expect(screen.getByRole('checkbox', { name: 'Einkauf' })).not.toBeChecked()
  })

  it('liefert die Liste in der Reihenfolge der Optionen', () => {
    const onChange = vi.fn()
    render(<FieldRenderer field={FELD} value={['dispo']} onChange={onChange} voiceEnabled={false} />)
    fireEvent.click(screen.getByRole('checkbox', { name: 'Einkauf' }))
    expect(onChange).toHaveBeenCalledWith(['einkauf', 'dispo'])
  })

  it('liest einen kommagetrennten Altwert', () => {
    render(<FieldRenderer field={FELD} value="einkauf, dispo" onChange={vi.fn()} voiceEnabled={false} />)
    expect(screen.getByRole('checkbox', { name: 'Disposition' })).toBeChecked()
  })

  it('ist nur lesend nicht aenderbar', () => {
    render(<FieldRenderer field={{ ...FELD, readOnly: true }} value={['fibu']} voiceEnabled={false} />)
    expect(screen.getByRole('checkbox', { name: 'Einkauf' })).toBeDisabled()
  })

  it('Pflichtfeld: eine leere Liste blockiert, eine gewaehlte Option nicht', () => {
    const screenDef = { schemaVersion: 1, id: 't/m', domain: 'platform', mode: 'detail', title: 'T', fields: [FELD] } as const
    const leer = renderHook(() => useUniversalFormState({ screen: screenDef, initialValues: { verwendungen: [] } }))
    expect(leer.result.current.validationPlan.hasBlockingErrors).toBe(true)
    const voll = renderHook(() => useUniversalFormState({ screen: screenDef, initialValues: { verwendungen: ['fibu'] } }))
    expect(voll.result.current.validationPlan.hasBlockingErrors).toBe(false)
  })
})
