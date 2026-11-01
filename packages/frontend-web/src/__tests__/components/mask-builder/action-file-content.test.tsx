import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { afterEach, expect, it, vi } from 'vitest'
import { ActionInputDialog } from '@/components/mask-builder/renderers/ActionInputDialog'
import { FastFormRenderer } from '@/components/mask-builder/renderers/FastFormRenderer'
import { compileRenderPlanFromScreenDefinition } from '@/components/mask-builder/render-plan/schema-compiler'
import type { ScreenActionDefinition, ScreenFieldDefinition } from '@/components/mask-builder/schema'
const transport = vi.hoisted(() => ({ get: vi.fn(), request: vi.fn() }))
vi.mock('@/lib/api-client', () => ({ apiClient: transport }))
afterEach(() => { vi.restoreAllMocks(); vi.clearAllMocks() })
const field: ScreenFieldDefinition = { key: 'csv', label: 'CSV-Datei', type: 'file', required: true,
  fileContent: { encoding: 'utf-8', maxBytes: 16, accept: ['.csv'] } }
function mount(fileField = field, initialValues?: Record<string, unknown>) {
  const submit = vi.fn()
  const action: ScreenActionDefinition = { key: 'import', label: 'Datei importieren', inputFields: [fileField] }
  render(<QueryClientProvider client={new QueryClient()}><ActionInputDialog action={action} open initialValues={initialValues}
    onSubmit={submit} onCancel={vi.fn()} /></QueryClientProvider>)
  return submit
}
it('blocks required empty/pending input and submits decoded text without reading or writing an API', async () => {
  const submit = mount()
  fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
  expect(submit).not.toHaveBeenCalled()
  fireEvent.change(screen.getByLabelText('CSV-Datei'), { target: { files: [new File(['a;b\n1;2'], 'data.csv')] } })
  fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
  expect(submit).not.toHaveBeenCalled()
  await screen.findByText('Textdatei geladen.')
  fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
  expect(submit).toHaveBeenCalledExactlyOnceWith({ csv: 'a;b\n1;2' })
  expect(transport.get).not.toHaveBeenCalled()
  expect(transport.request).not.toHaveBeenCalled()
})
it('blocks an invalid replacement even for an optional file', async () => {
  const submit = mount({ ...field, required: false }, { csv: 'old' })
  fireEvent.change(screen.getByLabelText('CSV-Datei'), { target: { files: [new File(['bad'], 'bad.pdf')] } })
  await screen.findByText(/Bitte eine Datei mit/)
  fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
  expect(submit).not.toHaveBeenCalled()
  fireEvent.click(screen.getByRole('button', { name: 'Dateiauswahl leeren' }))
  fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
  expect(submit).toHaveBeenCalledExactlyOnceWith({})
})
it.each([['oversize', 'x'.repeat(17)], ['wrong type', { text: 'data' }], ['invalid Unicode', '\uD800']])('rejects invalid prefilled input: %s', async (_label, value) => {
  const submit = mount(field, { csv: value })
  fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
  await waitFor(() => expect(screen.getAllByRole('alert').length).toBeGreaterThan(0))
  expect(submit).not.toHaveBeenCalled()
})
it('preserves the contract through the actual fast-form projection', () => {
  const plan = compileRenderPlanFromScreenDefinition({ schemaVersion: 1, id: 'test/file-form', domain: 'sales', mode: 'detail', title: 'Datei', fields: [field] })
  render(<FastFormRenderer fieldKeys={plan.rootFieldKeys} fieldsByKey={plan.fieldsByKey} payload={{ csv: 'text' }} />)
  expect(screen.getByLabelText('CSV-Datei')).toHaveAttribute('type', 'file')
  expect(screen.getByLabelText('CSV-Datei')).toHaveAttribute('accept', '.csv')
  expect(screen.getByText(/maximal 16 Bytes/)).toBeInTheDocument()
})
it('does not overwrite an external dialog reset with a late file read', async () => {
  let reader: FileReader | undefined
  vi.spyOn(FileReader.prototype, 'readAsArrayBuffer').mockImplementation(function (this: FileReader) { reader = this })
  const submit = vi.fn()
  const cancel = vi.fn()
  const action: ScreenActionDefinition = { key: 'import-reset', label: 'Import', inputFields: [field] }
  const client = new QueryClient()
  const view = (initialValues: Record<string, unknown>) => <QueryClientProvider client={client}>
    <ActionInputDialog action={action} open initialValues={initialValues} onSubmit={submit} onCancel={cancel} />
  </QueryClientProvider>
  const { rerender } = render(view({ csv: 'old' }))
  fireEvent.change(screen.getByLabelText('CSV-Datei'), { target: { files: [new File(['x'], 'file.csv')] } })
  expect(screen.getByText('Datei wird gelesen…')).toBeInTheDocument()
  rerender(view({ csv: 'reset' }))
  await waitFor(() => expect(screen.queryByText('Datei wird gelesen…')).not.toBeInTheDocument())
  if (!reader) throw new Error('Reader was not started')
  const buffer = new ArrayBuffer(1)
  new Uint8Array(buffer)[0] = 120
  Object.defineProperty(reader, 'result', { value: buffer })
  await act(async () => { reader?.dispatchEvent(new ProgressEvent('load')) })
  fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
  expect(submit).toHaveBeenCalledExactlyOnceWith({ csv: 'reset' })
})
