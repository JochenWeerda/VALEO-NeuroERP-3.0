import { useState } from 'react'
import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, expect, it, vi } from 'vitest'
import { FieldRenderer } from '@/components/mask-builder/renderers/FieldRenderer'
import type { ScreenFieldDefinition } from '@/components/mask-builder/schema'
const field: ScreenFieldDefinition = { key: 'csv', label: 'CSV-Datei', type: 'file', required: true,
  fileContent: { encoding: 'utf-8', maxBytes: 16, accept: ['.csv'] } }
afterEach(() => vi.restoreAllMocks())
function Form({ onChange = vi.fn() }: { onChange?: (value: unknown) => void }) {
  const [value, setValue] = useState<unknown>('old')
  return <FieldRenderer field={field} value={value} voiceEnabled={false} onChange={next => { setValue(next); onChange(next) }} />
}
it('reads real local bytes and emits only decoded text after clearing old content', async () => {
  const change = vi.fn()
  render(<Form onChange={change} />)
  fireEvent.change(screen.getByLabelText('CSV-Datei'), { target: { files: [new File(['ä;1\n'], 'import.csv')] } })
  expect(change).toHaveBeenNthCalledWith(1, null)
  await screen.findByText('Textdatei geladen.')
  expect(change).toHaveBeenLastCalledWith('ä;1\n')
  expect(screen.getByLabelText('CSV-Datei')).toHaveAttribute('accept', '.csv')
})
it('invalid replacement clears previous content and can be cleared explicitly', async () => {
  const change = vi.fn()
  render(<Form onChange={change} />)
  fireEvent.change(screen.getByLabelText('CSV-Datei'), { target: { files: [new File(['bad'], 'file.pdf')] } })
  await screen.findByRole('alert')
  expect(change.mock.calls).toEqual([[null]])
  fireEvent.click(screen.getByRole('button', { name: 'Dateiauswahl leeren' }))
  expect(change).toHaveBeenLastCalledWith('')
  expect(screen.queryByRole('alert')).not.toBeInTheDocument()
})
it('disables readonly file inputs and inputs without change handlers', () => {
  const change = vi.fn()
  const { rerender } = render(<FieldRenderer field={{ ...field, readOnly: true }} value="old" onChange={change} voiceEnabled={false} />)
  expect(screen.getByLabelText('CSV-Datei')).toBeDisabled()
  rerender(<FieldRenderer field={field} value="old" voiceEnabled={false} />)
  expect(screen.getByLabelText('CSV-Datei')).toBeDisabled()
  expect(change).not.toHaveBeenCalled()
})
it('keeps the newest selection when reads finish in reverse order', async () => {
  const readers: FileReader[] = []
  vi.spyOn(FileReader.prototype, 'readAsArrayBuffer').mockImplementation(function (this: FileReader) { readers.push(this) })
  const change = vi.fn()
  render(<Form onChange={change} />)
  const input = screen.getByLabelText('CSV-Datei')
  fireEvent.change(input, { target: { files: [new File(['first'], 'first.csv')] } })
  fireEvent.change(input, { target: { files: [new File(['second'], 'second.csv')] } })
  function finish(reader: FileReader, value: string) {
    const buffer = new ArrayBuffer(value.length)
    new Uint8Array(buffer).set(Array.from(value, char => char.charCodeAt(0)))
    Object.defineProperty(reader, 'result', { value: buffer })
    reader.dispatchEvent(new ProgressEvent('load'))
  }
  finish(readers[1], 'second')
  await waitFor(() => expect(change).toHaveBeenLastCalledWith('second'))
  finish(readers[0], 'first')
  await waitFor(() => expect(screen.queryByText('Datei wird gelesen…')).not.toBeInTheDocument())
  expect(change.mock.calls).toEqual([[null], [null], ['second']])
})
it('discards outstanding results after clearing and unmounting', async () => {
  let reader: FileReader | undefined
  vi.spyOn(FileReader.prototype, 'readAsArrayBuffer').mockImplementation(function (this: FileReader) { reader = this })
  const change = vi.fn()
  const { unmount } = render(<Form onChange={change} />)
  fireEvent.change(screen.getByLabelText('CSV-Datei'), { target: { files: [new File(['x'], 'file.csv')] } })
  fireEvent.click(screen.getByRole('button', { name: 'Dateiauswahl leeren' }))
  unmount()
  if (!reader) throw new Error('Reader was not started')
  const buffer = new ArrayBuffer(1)
  new Uint8Array(buffer)[0] = 120
  Object.defineProperty(reader, 'result', { value: buffer })
  reader.dispatchEvent(new ProgressEvent('load'))
  await Promise.resolve()
  expect(change.mock.calls).toEqual([[null], ['']])
})
it('reports read errors and leaves invalid form state', async () => {
  vi.spyOn(FileReader.prototype, 'readAsArrayBuffer').mockImplementation(function (this: FileReader) { this.dispatchEvent(new ProgressEvent('error')) })
  const change = vi.fn()
  render(<Form onChange={change} />)
  fireEvent.change(screen.getByLabelText('CSV-Datei'), { target: { files: [new File(['x'], 'file.csv')] } })
  await screen.findByText('Die Datei konnte nicht gelesen werden.')
  expect(change.mock.calls).toEqual([[null]])
})
it('ignores an outstanding result after the field becomes readonly', async () => {
  let reader: FileReader | undefined
  vi.spyOn(FileReader.prototype, 'readAsArrayBuffer').mockImplementation(function (this: FileReader) { reader = this })
  const change = vi.fn()
  const { rerender } = render(<FieldRenderer field={field} value="old" onChange={change} voiceEnabled={false} />)
  fireEvent.change(screen.getByLabelText('CSV-Datei'), { target: { files: [new File(['x'], 'file.csv')] } })
  rerender(<FieldRenderer field={{ ...field, readOnly: true }} value={null} onChange={change} voiceEnabled={false} />)
  if (!reader) throw new Error('Reader was not started')
  const buffer = new ArrayBuffer(1)
  new Uint8Array(buffer)[0] = 120
  Object.defineProperty(reader, 'result', { value: buffer })
  reader.dispatchEvent(new ProgressEvent('load'))
  await Promise.resolve()
  expect(change.mock.calls).toEqual([[null]])
  expect(screen.getByLabelText('CSV-Datei')).toBeDisabled()
})
it('discards a read after unmount without requiring a prior clear', async () => {
  let reader: FileReader | undefined
  vi.spyOn(FileReader.prototype, 'readAsArrayBuffer').mockImplementation(function (this: FileReader) { reader = this })
  const change = vi.fn()
  const { unmount } = render(<Form onChange={change} />)
  fireEvent.change(screen.getByLabelText('CSV-Datei'), { target: { files: [new File(['x'], 'file.csv')] } })
  unmount()
  if (!reader) throw new Error('Reader was not started')
  const buffer = new ArrayBuffer(1)
  new Uint8Array(buffer)[0] = 120
  Object.defineProperty(reader, 'result', { value: buffer })
  await act(async () => { reader?.dispatchEvent(new ProgressEvent('load')) })
  expect(change.mock.calls).toEqual([[null]])
})
