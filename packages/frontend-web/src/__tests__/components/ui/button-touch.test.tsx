import { createRef } from 'react'
import { fireEvent, render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { Button, buttonVariants } from '@/components/ui/button'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'

describe('shared compact action target', () => {
  it('retains the minimum target when a legacy toolbar supplies a short height', () => {
    render(<Button size="sm" className="h-6">Details</Button>)
    expect(screen.getByRole('button')).toHaveClass('min-h-touch', 'min-w-touch', 'h-6')
    expect(buttonVariants({ size: 'sm' })).toContain('h-11')
  })

  it('keeps default and icon buttons at 44 px when a mask forces h-7', () => {
    const { rerender } = render(<Button className="h-7 w-7">Suchen</Button>)
    expect(screen.getByRole('button', { name: 'Suchen' })).toHaveClass('min-h-touch', 'min-w-touch')
    rerender(<Button size="icon" className="h-7 w-7" aria-label="Hoch" />)
    expect(screen.getByRole('button', { name: 'Hoch' })).toHaveClass('min-h-touch', 'min-w-touch')
  })

  it('forwards focus and invokes the action once', () => {
    const action = vi.fn()
    const ref = createRef<HTMLButtonElement>()
    render(<Button ref={ref} size="sm" onClick={action}>Freigeben</Button>)
    ref.current?.focus()
    expect(screen.getByRole('button')).toHaveFocus()
    fireEvent.click(screen.getByRole('button'))
    expect(action).toHaveBeenCalledTimes(1)
  })

  it('preserves disabled actions', () => {
    const action = vi.fn()
    render(<Button size="sm" disabled onClick={action}>Freigeben</Button>)
    fireEvent.click(screen.getByRole('button'))
    expect(action).not.toHaveBeenCalled()
    expect(screen.getByRole('button')).toBeDisabled()
  })

  it('keeps compact inputs and checkboxes at the 44 px floor', () => {
    render(
      <>
        <Input aria-label="Betreff" className="h-7" />
        <Checkbox aria-label="gedruckt" />
      </>
    )
    expect(screen.getByRole('textbox', { name: 'Betreff' })).toHaveClass('min-h-touch', 'h-7')
    expect(screen.getByRole('checkbox', { name: 'gedruckt' })).toHaveClass('min-h-touch', 'min-w-touch')
  })

  it('applies the same target to navigation links without nesting a button', () => {
    render(<Button size="sm" asChild><a href="/verkauf/rechnungen">Rechnungen</a></Button>)
    expect(screen.getByRole('link')).toHaveClass('h-11', 'min-h-touch', 'min-w-touch')
    expect(screen.getByRole('link')).toHaveAttribute('href', '/verkauf/rechnungen')
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })
})
