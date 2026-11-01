import { describe, expect, it, vi } from 'vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { validateScreenDefinition, type ScreenDefinition } from '@/components/mask-builder/schema'
import { FinanceWorkbench } from '@/components/mask-builder/specialized/finance/finance-workbench'
import { UniversalMaskRenderer } from '@/components/mask-builder/UniversalMaskRenderer'
import fixtures from './fixtures/finance-workbenches.json'

vi.mock('@/components/mask-builder/specialized/intake/domain-data', () => ({ useDomainIdentity: () => ({ tenantId: 't1', actor: 'u1' }) }))
vi.mock('@/features/finance/useBankOptions', () => ({ useBankOptions: () => ({ data: [] }) }))
vi.mock('@/lib/api-client', () => ({ apiClient: { get: vi.fn().mockResolvedValue({ data: { items: [] } }) } }))
const schemas = fixtures as unknown as ScreenDefinition[]
const provider = (child: JSX.Element) => <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>{child}</QueryClientProvider>

describe('native Finance-Workbench-Verträge', () => {
  it.each(schemas)('kompiliert $id mit festem Fachvertrag und gefilterten Aktionen', schema => {
    expect(validateScreenDefinition(schema)).toEqual([])
    const plan = compileRenderPlanFromScreenDefinition(schema, { permissions: [] })
    expect(plan.specialized).toEqual({ type: 'finance_workbench', id: schema.id })
    expect(plan.shell.tableProfile).toBe('financial')
    expect(plan.actions.every(action => !['import', 'validate', 'run', 'sendEmail', 'sendPost'].includes(action.key))).toBe(true)
    const permissions = (schema.actions ?? []).flatMap(action => action.permission ? [action.permission] : [])
    const granted = compileRenderPlanFromScreenDefinition(schema, { permissions, roleHash: 'finance-write' })
    expect(granted.actions.length).toBe(schema.actions?.length)
  })
  it('rendert Bank über den zentralen Renderer und verbirgt generische Feldduplikate', () => {
    const schema = schemas[0]
    const plan = compileRenderPlanFromScreenDefinition(schema, { permissions: [], roleHash: 'bank-readonly' })
    render(provider(<UniversalMaskRenderer plan={plan} />))
    expect(screen.getByRole('region', { name: 'Bankabgleich Arbeitsbereich' })).toBeInTheDocument()
    expect(screen.getAllByLabelText('Bankkonto')).toHaveLength(1)
  })
  it('leitet berechtigte Kopfaktionen über den gemeinsamen Renderer weiter', () => {
    const schema = schemas[0]
    const permissions = (schema.actions ?? []).flatMap(action => action.permission ? [action.permission] : [])
    const plan = compileRenderPlanFromScreenDefinition(schema, { permissions, roleHash: 'bank-dispatch' })
    const dispatch = vi.fn()
    render(provider(<UniversalMaskRenderer plan={plan} onAction={dispatch} />))
    fireEvent.click(screen.getByRole('button', { name: 'Kontoauszug importieren' }))
    expect(dispatch).toHaveBeenCalledWith('import', expect.any(Object))
  })
  it('sperrt bei entferntem Pflichtfeld die Fachoberfläche', () => {
    const schema = schemas[0]
    const plan = compileRenderPlanFromScreenDefinition(schema, { permissions: [], roleHash: 'hidden-field' })
    plan.fieldsByKey.kontoId = { ...plan.fieldsByKey.kontoId, visible: false }
    render(provider(<FinanceWorkbench contract={plan.specialized!} plan={plan} />))
    expect(screen.getByRole('alert')).toHaveTextContent('ausgeblendeten Pflichtbereichen')
    expect(screen.queryByLabelText('Bankkonto')).not.toBeInTheDocument()
  })
  it('verwirft eine fremde Fachbindung', () => {
    const schema = { ...schemas[0], specialized: { type: 'finance_workbench', id: 'mahnwesen/mahnlauf' } } as ScreenDefinition
    expect(() => compileRenderPlanFromScreenDefinition(schema)).toThrow('Invalid native specialized contract')
  })
})

