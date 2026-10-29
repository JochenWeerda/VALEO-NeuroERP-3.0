import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { ActionInputDialog } from '@/components/mask-builder/renderers/ActionInputDialog'
import { useState } from 'react'
import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, renderHook, act } from '@testing-library/react'
import { FieldRenderer } from '@/components/mask-builder/renderers/FieldRenderer'
import { FastFormRenderer } from '@/components/mask-builder/renderers/FastFormRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import { useUniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import { FormStateContext } from '@/components/mask-builder/runtime/FormStateContext'
import type { ScreenFieldDefinition, ScreenDefinition } from '@/components/mask-builder/schema'

const field: ScreenFieldDefinition = { key: 'items', label: 'Positionen', type: 'table',
  rowFields: [{ key: 'article', label: 'Artikel', type: 'text' }, { key: 'quantity', label: 'Menge', type: 'number' },
    { key: 'net', label: 'Netto', type: 'currency', readOnly: true }],
  tableEditing: { allowAdd: true, allowDelete: true, maxRows: 2 } }
const initial = [{ article: 'SYNTH', quantity: 1, net: 10, hidden_id: 'preserved' }]
function Harness({ definition = field, changed = () => undefined }: { definition?: ScreenFieldDefinition; changed?: (value: unknown) => void }) {
  const [value, setValue] = useState(initial)
  return <FieldRenderer field={definition} value={value} voiceEnabled={false} onChange={next => { changed(next); setValue(next as typeof initial) }} />
}

describe('structured table input', () => {
  it('preserves hidden data and original rows while editing typed values', () => {
    const changed = vi.fn()
    render(<Harness changed={changed} />)
    fireEvent.change(screen.getByLabelText('Menge, Zeile 1'), { target: { value: '2.5' } })
    expect(changed).toHaveBeenLastCalledWith([{ ...initial[0], quantity: 2.5 }])
    expect(initial[0].quantity).toBe(1)
    expect(screen.getByLabelText('Netto, Zeile 1')).toHaveAttribute('readonly')
  })
  it('adds and removes only explicitly enabled rows and enforces the limit', () => {
    const changed = vi.fn()
    render(<Harness changed={changed} />)
    fireEvent.click(screen.getByRole('button', { name: 'Zeile hinzufügen' }))
    expect(changed).toHaveBeenLastCalledWith([initial[0], {}])
    expect(screen.getByRole('button', { name: 'Zeile hinzufügen' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Zeile 1 entfernen' }))
    expect(changed).toHaveBeenLastCalledWith([{}])
  })
  it('does not offer structural changes by default', () => {
    render(<Harness definition={{ ...field, tableEditing: undefined }} />)
    expect(screen.queryByRole('button', { name: 'Zeile hinzufügen' })).toBeNull()
    expect(screen.queryByRole('button', { name: 'Zeile 1 entfernen' })).toBeNull()
  })
  it('readonly prevents every change even if a callback exists', () => {
    const changed = vi.fn()
    render(<Harness definition={{ ...field, readOnly: true }} changed={changed} />)
    expect(screen.getByLabelText('Artikel, Zeile 1')).toHaveAttribute('readonly')
    expect(screen.getByRole('button', { name: 'Zeile hinzufügen' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Zeile 1 entfernen' }))
    expect(changed).not.toHaveBeenCalled()
  })
  it.each([undefined, [{ key: '__proto__', label: 'Invalid', type: 'text' }],
    [{ key: 'a', label: 'A', type: 'table' }], [{ key: 'a', label: 'A', type: 'lookup' }],
    [{ key: 'a', label: 'A', type: 'text' }, { key: 'a', label: 'A', type: 'text' }]])('rejects invalid column structures', columns => {
    render(<Harness definition={{ ...field, rowFields: columns as ScreenFieldDefinition[] }} />)
    expect(screen.getByRole('alert')).toBeVisible()
    expect(screen.queryByRole('table')).toBeNull()
  })
  it.each(['not-a-list', [null], [1], [{}, {}, {}]])('does not silently truncate or convert malformed rows', value => {
    render(<FieldRenderer field={field} value={value} onChange={vi.fn()} voiceEnabled={false} />)
    expect(screen.getByRole('alert')).toBeVisible()
    expect(screen.queryByRole('table')).toBeNull()
  })
  it('carries columns through compiler, form state and the shared renderer', () => {
    const schema: ScreenDefinition = { schemaVersion: 1, id: 'test/rows', domain: 'sales', mode: 'detail', title: 'Test', fields: [field] }
    const plan = compileRenderPlanFromScreenDefinition(schema)
    expect(plan.fieldsByKey.items.componentKind).toBe('table')
    function Integrated() {
      const form = useUniversalFormState({ screen: schema, initialValues: { items: initial } })
      return <FormStateContext.Provider value={form}><FastFormRenderer fieldKeys={['items']} fieldsByKey={plan.fieldsByKey}
        payload={form.values} className="" voiceEnabled={false} /></FormStateContext.Provider>
    }
    render(<Integrated />)
    fireEvent.change(screen.getByLabelText('Artikel, Zeile 1'), { target: { value: 'CHANGED' } })
    expect(screen.getByLabelText('Artikel, Zeile 1')).toHaveValue('CHANGED')
  })
})


it('blocks submit for incomplete or malformed required table cells', () => {
  const required = { ...field, rowFields: [{ key: 'quantity', label: 'Menge', type: 'number' as const, required: true }] }
  const schema: ScreenDefinition = { schemaVersion: 1, id: 'test/required-rows', domain: 'sales', mode: 'detail', title: 'Test', fields: [required] }
  const { result } = renderHook(() => useUniversalFormState({ screen: schema, initialValues: { items: [{}] } }))
  expect(result.current.canSubmit).toBe(false)
  act(() => result.current.setValue('items', [{ quantity: 'invalid' }]))
  expect(result.current.canSubmit).toBe(false)
  act(() => result.current.setValue('items', [{ quantity: 0 }]))
  expect(result.current.validationPlan.hasBlockingErrors).toBe(false)
  act(() => result.current.setValue('items', [{ quantity: true }]))
  expect(result.current.validationPlan.hasBlockingErrors).toBe(true)
})

it.each([null, ['not-a-column'], [null]])('rejects malformed column metadata without throwing', columns => {
  render(<Harness definition={{ ...field, rowFields: columns as unknown as ScreenFieldDefinition[] }} />)
  expect(screen.getByRole('alert')).toBeVisible()
})


it('does not reinterpret existing unconfigured legacy table fields', () => {
  const legacy: ScreenDefinition = { schemaVersion: 1, id: 'test/legacy-table', domain: 'sales', mode: 'detail', title: 'Test',
    fields: [{ key: 'items', label: 'Legacy', type: 'table' }] }
  expect(compileRenderPlanFromScreenDefinition(legacy).fieldsByKey.items.componentKind).toBe('text')
  const { result } = renderHook(() => useUniversalFormState({ screen: legacy, initialValues: { items: 'legacy-input' } }))
  expect(result.current.validationPlan.hasBlockingErrors).toBe(false)
})


it('command dialogs submit typed rows through the same form renderer', () => {
  const submit=vi.fn()
  render(<QueryClientProvider client={new QueryClient()}><ActionInputDialog open action={{key:'edit',label:'Positionen bearbeiten',
    inputFields:[{...field,rowFields:[{key:'article',label:'Artikel',type:'text',required:true},{key:'quantity',label:'Menge',type:'number',required:true}]}]}}
    onCancel={vi.fn()} onSubmit={submit}/></QueryClientProvider>)
  fireEvent.click(screen.getByRole('button',{name:'Zeile hinzufügen'}))
  fireEvent.change(screen.getByLabelText('Artikel, Zeile 1'),{target:{value:'SYNTH'}})
  fireEvent.change(screen.getByLabelText('Menge, Zeile 1'),{target:{value:'0'}})
  fireEvent.click(screen.getByRole('button',{name:'Weiter'}))
  expect(submit).toHaveBeenCalledWith({items:[{article:'SYNTH',quantity:0}]})
})

it('command dialogs retain an explicitly emptied table list', () => {
  const submit=vi.fn()
  render(<QueryClientProvider client={new QueryClient()}><ActionInputDialog open action={{key:'edit',label:'Positionen bearbeiten',inputFields:[field]}}
    onCancel={vi.fn()} onSubmit={submit}/></QueryClientProvider>)
  fireEvent.click(screen.getByRole('button',{name:'Zeile hinzufügen'}))
  fireEvent.click(screen.getByRole('button',{name:'Zeile 1 entfernen'}))
  fireEvent.click(screen.getByRole('button',{name:'Weiter'}))
  expect(submit).toHaveBeenCalledWith({items:[]})
})
