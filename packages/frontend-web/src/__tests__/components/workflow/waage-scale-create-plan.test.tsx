import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { RenderPlan } from '@/components/mask-builder/render-plan/types'
import { ScaleCreateRenderer } from '@/components/mask-builder/specialized/weighing/scale-create-renderer'

function plan(disabled = false): RenderPlan {
  return {
    fieldsByKey: {
      standort: { key: 'standort', label: 'Standort', visible: true, required: true, readOnly: false },
      typ: { key: 'typ', label: 'Waagentyp', visible: true, required: true, readOnly: false },
      max_kapazitaet: { key: 'max_kapazitaet', label: 'Kapazität in Tonnen', visible: true, required: true, readOnly: false },
    },
    actions: [{ key: 'create', label: 'Waage anlegen', disabled }],
  } as unknown as RenderPlan
}
const state = {
  standort: '', typ: '', maxKapazitaet: '', pending: false, error: null,
  setStandort: vi.fn(), setTyp: vi.fn(), setMaxKapazitaet: vi.fn(), submit: vi.fn(),
}
describe('Waagenanlage aus RenderPlan', () => {
  it('zeigt deklarierte Feldnamen ohne erfundene Vorgaben', () => {
    render(<ScaleCreateRenderer plan={plan()} state={state} />)
    expect(screen.getByLabelText('Standort')).toHaveValue('')
    expect(screen.getByLabelText('Waagentyp')).toHaveValue('')
    expect(screen.getByLabelText('Kapazität in Tonnen')).toHaveValue(null)
    expect(screen.getByRole('button', { name: 'Waage anlegen' })).toBeEnabled()
  })
  it('sperrt die Anlage, wenn ein Pflichtfeld schreibgeschützt ist', () => {
    const definition = plan()
    definition.fieldsByKey.standort.readOnly = true
    render(<ScaleCreateRenderer plan={definition} state={state} />)
    expect(screen.getByRole('button', { name: 'Waage anlegen' })).toBeDisabled()
  })
  it('sperrt eine laut Plan nicht erlaubte Aktion', () => {
    render(<ScaleCreateRenderer plan={plan(true)} state={state} />)
    expect(screen.getByRole('button', { name: 'Waage anlegen' })).toBeDisabled()
  })
})
