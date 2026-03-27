import { describe, it, expect, vi } from 'vitest'
import { render, screen, fireEvent, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
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

  function renderWizard(onFinish = vi.fn()) {
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })

    return render(
      <QueryClientProvider client={queryClient}>
        <Wizard
          title="Test Wizard"
          steps={mockSteps}
          onFinish={onFinish}
          onCancel={vi.fn()}
        />
      </QueryClientProvider>,
    )
  }

  it('sollte rendern', () => {
    renderWizard()

    expect(screen.getByText('Test Wizard')).toBeInTheDocument()
    expect(screen.getAllByText('Schritt 1').length).toBeGreaterThan(0)
  })

  it('sollte ersten Schritt-Inhalt anzeigen', () => {
    renderWizard()

    expect(screen.getByText('Inhalt Schritt 1')).toBeInTheDocument()
  })

  it('sollte Weiter-Button haben', () => {
    renderWizard()

    const weiterButton = screen.getByRole('button', { name: /weiter/i })
    expect(weiterButton).toBeInTheDocument()
  })

  it('sollte onFinish aufrufen im letzten Schritt', async () => {
    const onFinish = vi.fn()

    renderWizard(onFinish)

    // Navigiere zum letzten Schritt
    const weiterButton = screen.getByRole('button', { name: /weiter/i })
    fireEvent.click(weiterButton)

    // Im letzten Schritt sollte der "Abschliessen"-Button erscheinen
    const abschliessenButton = await screen.findByRole('button', { name: /abschliessen/i })
    fireEvent.click(abschliessenButton)

    await waitFor(() => {
      expect(onFinish).toHaveBeenCalled()
    })
  })

  it('blockiert den Schrittwechsel, wenn die Validierung einen Fehler meldet', async () => {
    const onStepValidationError = vi.fn()
    const queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
        },
      },
    })

    render(
      <QueryClientProvider client={queryClient}>
        <Wizard
          title="Test Wizard"
          steps={mockSteps}
          onCancel={vi.fn()}
          getStepValidationError={(stepId) => (stepId === 'step1' ? 'Schritt 1 ist unvollstaendig.' : null)}
          onStepValidationError={onStepValidationError}
        />
      </QueryClientProvider>,
    )

    fireEvent.click(screen.getByRole('button', { name: /weiter/i }))

    await waitFor(() => {
      expect(onStepValidationError).toHaveBeenCalledWith('step1', 'Schritt 1 ist unvollstaendig.')
    })
    expect(screen.getByText('Inhalt Schritt 1')).toBeInTheDocument()
    expect(screen.queryByText('Inhalt Schritt 2')).not.toBeInTheDocument()
  })
})
