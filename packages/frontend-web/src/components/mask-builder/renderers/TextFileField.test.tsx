import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { TextFileField } from './TextFileField'
import type { ScreenFieldDefinition } from '../schema'

const field: ScreenFieldDefinition = { key: 'csv_content', label: 'CSV-Datei', type: 'file', required: true,
  fileContent: { encoding: 'utf-8', accept: '.csv', maxBytes: 16 } }
const file = (bytes: number[]) => ({ size: bytes.length, arrayBuffer: async () => new Uint8Array(bytes).buffer })

describe('registered UTF-8 text file input', () => {
  it('clears the previous value and passes content, never a file path', async () => {
    const change = vi.fn()
    render(<TextFileField field={field} value="old" readOnly={false} onChange={change} />)
    fireEvent.change(screen.getByLabelText('CSV-Datei *'), { target: { files: [file([65, 59, 66])] } })
    expect(change).toHaveBeenNthCalledWith(1, undefined)
    await waitFor(() => expect(change).toHaveBeenLastCalledWith('A;B'))
  })
  it.each([[255], [65, 0, 66], Array(17).fill(65), []].map(bytes => ({ bytes })))('rejects malformed, binary, oversized or empty input', async ({ bytes }) => {
    const change = vi.fn()
    render(<TextFileField field={field} value="old" readOnly={false} onChange={change} />)
    fireEvent.change(screen.getByLabelText('CSV-Datei *'), { target: { files: [file(bytes)] } })
    expect(await screen.findByRole('alert')).toBeInTheDocument()
    expect(change.mock.calls).toEqual([[undefined]])
  })
  it('ignores a stale asynchronous selection and completion after unmount', async () => {
    let resolveFirst!: (value: ArrayBuffer) => void
    const change = vi.fn()
    const view = render(<TextFileField field={field} value="" readOnly={false} onChange={change} />)
    const input = screen.getByLabelText('CSV-Datei *')
    fireEvent.change(input, { target: { files: [{ size: 1, arrayBuffer: () => new Promise<ArrayBuffer>(resolve => { resolveFirst = resolve }) }] } })
    fireEvent.change(input, { target: { files: [file([66])] } })
    await waitFor(() => expect(change).toHaveBeenLastCalledWith('B'))
    view.unmount()
    resolveFirst(new Uint8Array([65]).buffer)
    await Promise.resolve()
    expect(change).toHaveBeenLastCalledWith('B')
  })
  it('keeps readonly values immutable and escapes preview markup', () => {
    render(<TextFileField field={field} value="<script>unsafe</script>" readOnly onChange={vi.fn()} />)
    expect(screen.queryByLabelText('CSV-Datei *')).toBeNull()
    expect(screen.getByLabelText('Dateivorschau')).toHaveTextContent('<script>unsafe</script>')
    expect(document.querySelector('script')).toBeNull()
  })
})
