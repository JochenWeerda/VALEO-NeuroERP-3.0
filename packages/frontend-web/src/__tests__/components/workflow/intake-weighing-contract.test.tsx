import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import type { RenderPlan } from '@/components/mask-builder/render-plan/types'
import { canDomainAction, fieldsEditable, DomainContractBoundary } from '@/components/mask-builder/specialized/intake/domain-runtime'
import { Intake } from '@/components/mask-builder/specialized/intake/intake'
import { Weighing } from '@/components/mask-builder/specialized/weighing/weighing'
import { mapScale } from '@/components/mask-builder/specialized/weighing/scale-data'
import { ActionBarRenderer } from '@/components/mask-builder/renderers/ActionBarRenderer'
import { validateScreenDefinition, type ScreenDefinition } from '@/components/mask-builder/schema'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import definitions from '@/__tests__/fixtures/intake-weighing-screens.json'

vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({ UniversalNativeCockpitPage: () => null }))
vi.mock('@/components/mask-builder/specialized/intake/domain-data', () => ({ useDomainIdentity: () => ({ tenantId: 'tenant-a', actor: 'operator-a' }) }))
vi.mock('@/components/mask-builder/specialized/intake/registration-surface', () => ({ default: () => <div>Registration mounted</div> }))
vi.mock('@/components/mask-builder/specialized/intake/quality-surface', () => ({ default: () => <div>Quality mounted</div> }))
vi.mock('@/components/mask-builder/specialized/intake/queue-surface', () => ({ default: () => <div>Queue mounted</div> }))
vi.mock('@/components/mask-builder/specialized/weighing/scales-surface', () => ({ default: () => <div>Scales mounted</div> }))
vi.mock('@/components/mask-builder/specialized/weighing/tickets-surface', () => ({ default: () => <div>Tickets mounted</div> }))
vi.mock('@/components/mask-builder/specialized/weighing/scale-create-surface', () => ({ default: () => <div>Create mounted</div> }))

function plan(): RenderPlan {
  return { screenId: 'annahme/warteschlange', fieldsByKey: { status: { visible: true, readOnly: false } }, actions: [{ key: 'save', disabled: false }] } as unknown as RenderPlan
}
describe('Intake/weighing compiled contract boundary', () => {
  it('does not grant undeclared, disabled or unevaluated conditional actions', () => {
    const value = plan()
    expect(canDomainAction(value, 'repair')).toBe(false)
    expect(canDomainAction(value, 'save')).toBe(true)
    value.actions[0].disabled = true
    expect(canDomainAction(value, 'save')).toBe(false)
    value.actions[0].disabled = false
    value.actions[0].enabledWhen = 'unknown-policy'
    expect(canDomainAction(value, 'save')).toBe(false)
  })
  it('blocks mounting a specialist when an overlay hides a required field', () => {
    const value = plan()
    value.fieldsByKey.status.visible = false
    render(<DomainContractBoundary plan={value} fields={['status']}><div>Sensitive data</div></DomainContractBoundary>)
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.queryByText('Sensitive data')).not.toBeInTheDocument()
  })
  it('does not treat missing or read-only inputs as editable', () => {
    const value = plan()
    expect(fieldsEditable(value, ['status'])).toBe(true)
    value.fieldsByKey.status.readOnly = true
    expect(fieldsEditable(value, ['status'])).toBe(false)
    expect(fieldsEditable(value, ['missing'])).toBe(false)
  })
  it('rejects another screen id before mounting intake or weighing data hooks', () => {
    const value = plan()
    render(<Intake contract={{ type: 'intake', id: 'annahme/qualitaets-check' }} plan={value} />)
    expect(screen.getByRole('alert')).toBeInTheDocument()
    expect(screen.queryByText('Quality mounted')).not.toBeInTheDocument()
  })
  it('opens scale creation as its own surface rather than the scales list', () => {
    const value = { ...plan(), screenId: 'waage/neu', specialized: { type: 'weighing', id: 'waage/neu' }, fieldsByKey: Object.fromEntries(['standort', 'typ', 'max_kapazitaet'].map(key => [key, { visible: true }])) } as unknown as RenderPlan
    render(<Weighing contract={{ type: 'weighing', id: 'waage/neu' }} plan={value} />)
    expect(screen.getByText('Create mounted')).toBeInTheDocument()
    expect(screen.queryByText('Scales mounted')).not.toBeInTheDocument()
  })
  it('opens a tenant clone only through its compiled canonical specialized binding', () => {
    const value = { ...plan(), screenId: 'tenant/operator/waage-create', specialized: { type: 'weighing', id: 'waage/neu' }, fieldsByKey: Object.fromEntries(['standort', 'typ', 'max_kapazitaet'].map(key => [key, { visible: true }])) } as unknown as RenderPlan
    render(<Weighing contract={{ type: 'weighing', id: 'waage/neu' }} plan={value} />)
    expect(screen.getByText('Create mounted')).toBeInTheDocument()
  })
  it('rejects a tenant definition whose native base names another specialist', () => {
    const definition = { schemaVersion: 1, id: 'tenant/operator/waage-create', baseScreenId: 'waage/neu', domain: 'agrar', mode: 'cockpit', title: 'Waage anlegen', specialized: { type: 'weighing', id: 'waage/neu' }, layout: { floorplan: 'transaction', density: 'expertDense', contextRail: 'combined', tableProfile: 'inventory' } } as ScreenDefinition
    expect(validateScreenDefinition(definition)).not.toContain('specialized native binding is invalid')
    definition.baseScreenId = 'waage/wiegungen'
    expect(validateScreenDefinition(definition)).toContain('specialized native binding is invalid')
  })
  it('maps real scale capacity and dates without manufacturing missing calibration', () => {
    expect(mapScale({ id: 'scale-a', standort: 'Hof', typ: 'LKW', max_kapazitaet: 60, letzte_eichung: null, naechste_eichung: '2027-06-01', status: 'aktiv' })).toEqual({ id: 'scale-a', standort: 'Hof', typ: 'LKW', maxKapazitaet: 60, letzteEichung: '', naechsteEichung: '2027-06-01', status: 'aktiv' })
  })
  it('keeps contextual actions guarded while omitting duplicate toolbar buttons', () => {
    const value = plan()
    value.actions[0].surfaceOnly = true
    render(<ActionBarRenderer domain="agrar" mode="cockpit" title="Annahme" headerClassName="" touchTargetClass="" payload={{}}
      actions={[{ key: 'save', label: 'Kontextaktion', surfaceOnly: true }, { key: 'refresh', label: 'Aktualisieren' }]} />)
    expect(screen.queryByRole('button', { name: 'Kontextaktion' })).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Aktualisieren' })).toBeInTheDocument()
    expect(canDomainAction(value, 'save')).toBe(true)
  })
  it('invalidates the compiled action presentation when surface placement changes', () => {
    const definition = structuredClone(definitions['waage/neu']) as unknown as ScreenDefinition
    const permissions = definition.actions!.flatMap(action => action.permission ? [action.permission] : [])
    const first = compileRenderPlanFromScreenDefinition(definition, { permissions })
    definition.actions![0].surfaceOnly = true
    const second = compileRenderPlanFromScreenDefinition(definition, { permissions })
    expect(second.cacheKey).not.toBe(first.cacheKey)
    expect(second.actions[0].surfaceOnly).toBe(true)
    expect(canDomainAction(second, 'create')).toBe(true)
  })
})
