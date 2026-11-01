import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { DomainWizard } from '@/components/mask-builder/specialized/intake/domain-wizard'

describe('Embedded intake wizard', () => {
  it('validates before advancing and finishes only after the last step', async () => {
    const finish = vi.fn(), validationError = vi.fn()
    let complete = false
    render(<DomainWizard title="Registration" steps={[{ id: 'vehicle', title: 'Fahrzeug', content: <div>Vehicle fields</div> }, { id: 'confirm', title: 'Bestätigung', content: <div>Confirmation</div> }]}
      getStepValidationError={step => step === 'vehicle' && !complete ? 'Kennzeichen fehlt' : null} onStepValidationError={validationError} onFinish={finish} />)
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await waitFor(() => expect(validationError).toHaveBeenCalledWith('vehicle', 'Kennzeichen fehlt'))
    expect(screen.getByText('Vehicle fields')).toBeInTheDocument()
    expect(finish).not.toHaveBeenCalled()
    complete = true
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await screen.findByText('Confirmation')
    fireEvent.click(screen.getByRole('button', { name: 'Abschliessen' }))
    await waitFor(() => expect(finish).toHaveBeenCalledTimes(1))
    expect(screen.queryByRole('heading', { level: 1 })).not.toBeInTheDocument()
  })
  it('allows reading steps while the compiled finishing action is unavailable', async () => {
    const finish = vi.fn()
    render(<DomainWizard title="Quality" finishDisabled steps={[{ id: 'quality', title: 'Qualität', content: <div>Read values</div> }]} onFinish={finish} />)
    expect(screen.getByRole('button', { name: 'Abschliessen' })).toBeDisabled()
    fireEvent.click(screen.getByRole('button', { name: 'Abschliessen' }))
    expect(finish).not.toHaveBeenCalled()
  })
})
