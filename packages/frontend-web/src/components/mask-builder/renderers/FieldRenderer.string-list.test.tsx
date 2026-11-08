import '@testing-library/jest-dom/vitest'
import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FieldRenderer } from './FieldRenderer'
import type { ScreenFieldDefinition } from '../schema'

const field = { key: 'topics', label: 'Themen', type: 'stringList' } as ScreenFieldDefinition

describe('string list field', () => {
  it('renders an empty array and preserves line order and empty lines', () => {
    const change = vi.fn()
    const { rerender } = render(<FieldRenderer field={field} value={[]} onChange={change} voiceEnabled={false} />)
    const input = screen.getByLabelText('Themen')
    expect(input).toHaveValue('')
    fireEvent.change(input, { target: { value: 'First\n\n Third ' } })
    expect(change).toHaveBeenLastCalledWith(['First', '', ' Third '])
    rerender(<FieldRenderer field={field} value={['First', '', ' Third ']} onChange={change} voiceEnabled={false} />)
    fireEvent.change(input, { target: { value: '' } })
    expect(change).toHaveBeenLastCalledWith([])
  })
  it('allows entry when the value is initially unset', () => {
    const change = vi.fn()
    render(<FieldRenderer field={field} value={undefined} onChange={change} voiceEnabled={false} />)
    const input = screen.getByLabelText('Themen')
    expect(input).not.toHaveAttribute('readonly')
    fireEvent.change(input, { target: { value: 'first' } })
    expect(change).toHaveBeenCalledWith(['first'])
  })
  it('renders readonly arrays as multiline text with theme tokens', () => {
    const change = vi.fn()
    render(<FieldRenderer field={{ ...field, readOnly: true }} value={['First', 'Second']} onChange={change} voiceEnabled={false} />)
    const input = screen.getByLabelText('Themen')
    expect(input).toHaveValue('First\nSecond')
    expect(input).toHaveAttribute('readonly')
    expect(input.className).toContain('bg-background')
    fireEvent.change(input, { target: { value: 'forged' } })
    expect(change).not.toHaveBeenCalled()
  })
  it('blocks malformed values and reports the error', () => {
    const change = vi.fn()
    render(<FieldRenderer field={field} value={{ text: 'wrong' }} onChange={change} voiceEnabled={false} />)
    const input = screen.getByLabelText('Themen')
    expect(input).toHaveValue('')
    expect(input).toHaveAttribute('readonly')
    expect(input).toHaveAttribute('aria-invalid', 'true')
    expect(screen.getByRole('alert')).toHaveTextContent('Ungültiger Listenwert')
    fireEvent.change(input, { target: { value: 'replacement' } })
    expect(change).not.toHaveBeenCalled()
  })
})


describe('readonly select field', () => {
  const select = { key: 'status', label: 'Status', type: 'select', readOnly: true,
    options: [{ value: 'planned', label: 'Geplant' }] } as ScreenFieldDefinition
  it('shows a copyable label without dispatching changes', () => {
    const change = vi.fn()
    render(<FieldRenderer field={select} value="planned" onChange={change} voiceEnabled={false} />)
    const input = screen.getByLabelText('Status')
    expect(input).toHaveValue('Geplant')
    expect(input).toHaveAttribute('readonly')
    expect(input).not.toBeDisabled()
    fireEvent.change(input, { target: { value: 'forged' } })
    expect(change).not.toHaveBeenCalled()
  })
  it('preserves an unknown value', () => {
    render(<FieldRenderer field={select} value="unknown" voiceEnabled={false} />)
    expect(screen.getByLabelText('Status')).toHaveValue('unknown')
  })
})
