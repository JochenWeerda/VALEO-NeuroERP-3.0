import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Wizard } from '@/components/patterns/Wizard'

describe('Wizard', () => {
  const mockSteps = [
    {
      id: 'step1',
      title: 'Schritt 1',
      content: <div>Inhalt Schritt 1</div>,
    },
    {
      id: 'step2',
      title: 'Schritt 2',
      content: <div>Inhalt Schritt 2</div>,
    },
  ]

  it('sollte rendern', () => {
    render(
      <Wizard
        title="Test Wizard"
        steps={mockSteps}
        onFinish={vi.fn()}
        onCancel={vi.fn()}
      />,
    )
    
    expect(screen.getByText('Test Wizard')).toBeInTheDocument()
    expect(screen.getByText('Schritt 1')).toBeInTheDocument()
  })

  it('sollte ersten Schritt-Inhalt anzeigen', () => {
    render(
      <Wizard
        title="Test Wizard"
        steps={mockSteps}
        onFinish={vi.fn()}
        onCancel={vi.fn()}
      />,
    )
    
    expect(screen.getByText('Inhalt Schritt 1')).toBeInTheDocument()
  })

  it('sollte Weiter-Button haben', () => {
    render(
      <Wizard
        title="Test Wizard"
        steps={mockSteps}
        onFinish={vi.fn()}
        onCancel={vi.fn()}
      />,
    )
    
    const weiterButton = screen.getByRole('button', { name: /weiter/i })
    expect(weiterButton).toBeInTheDocument()
  })

  it('sollte onFinish aufrufen im letzten Schritt', () => {
    const onFinish = vi.fn()
    
    render(
      <Wizard
        title="Test Wizard"
        steps={mockSteps}
        onFinish={onFinish}
        onCancel={vi.fn()}
      />,
    )
    
    // Navigiere zum letzten Schritt
    const weiterButton = screen.getByRole('button', { name: /weiter/i })
    fireEvent.click(weiterButton)
    
    // Im letzten Schritt sollte Abschließen-Button erscheinen
    const abschliessenButton = screen.getByRole('button', { name: /abschließen/i })
    fireEvent.click(abschliessenButton)
    
    expect(onFinish).toHaveBeenCalled()
  })
})
