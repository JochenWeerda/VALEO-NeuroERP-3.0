import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { StudioDialogue } from '@/features/screen-studio/StudioDialogue'
import { emptyStudioDraft } from '@/features/screen-studio/studio-defaults'

const send = vi.hoisted(() => vi.fn())
vi.mock('@/lib/api/studio', () => ({ sendStudioDialogue: send }))

describe('catalog-guided Studio conversation', () => {
  it('restores the saved conversation and explicit manual decisions without a model call', () => {
    const previousCalls = send.mock.calls.length
    render(<StudioDialogue disabled={false} onProposal={vi.fn()} initialTurns={[
      { role: 'user', content: 'Gespeicherte fachliche Anforderung' },
      { role: 'assistant', content: 'Gespeicherte Rueckfrage' },
    ]} initialDecisions={{ weighing: 'manual', acceptPreviewLimits: true }} />)
    expect(screen.getByText('Gespeicherte fachliche Anforderung')).toBeInTheDocument()
    expect(screen.getByText('Gespeicherte Rueckfrage')).toBeInTheDocument()
    expect(screen.getByLabelText('Wiegewerte übernehmen')).toHaveValue('manual')
    expect(screen.getByRole('checkbox', { name: /Nur Kalkulationsprobe/ })).toBeChecked()
    expect(send.mock.calls.length).toBe(previousCalls)
  })

  it('clarifies requirements before applying a proposal, preserves turns, invalidates changed consent', async () => {
    const onProposal = vi.fn()
    send.mockResolvedValueOnce({ ready: false, message: 'Wiegewerte manuell oder automatisch?', limitations: [] })
    send.mockResolvedValueOnce({ ready: true, message: 'Manuelle Probe bereit', limitations: ['Keine Buchung'], definition: emptyStudioDraft() })
    render(<StudioDialogue onProposal={onProposal} disabled={false} />)
    fireEvent.click(screen.getByRole('button', { name: 'Im Fachgespräch prüfen' }))
    await screen.findByText('Wiegewerte manuell oder automatisch?')
    expect(onProposal).not.toHaveBeenCalled()
    fireEvent.change(screen.getByLabelText('Wiegewerte übernehmen'), { target: { value: 'manual' } })
    fireEvent.click(screen.getByRole('checkbox', { name: /Nur Kalkulationsprobe/ }))
    fireEvent.change(screen.getByLabelText('Anforderung oder Antwort'), { target: { value: 'Manuelle Probe akzeptiert.' } })
    fireEvent.click(screen.getByRole('button', { name: 'Im Fachgespräch prüfen' }))
    await screen.findByRole('button', { name: 'Geprüften Vorschlag übernehmen' })
    expect(send.mock.calls[1][0]).toHaveLength(3)
    expect(send.mock.calls[1].slice(1)).toEqual(['manual', true])
    fireEvent.click(screen.getByRole('button', { name: 'Geprüften Vorschlag übernehmen' }))
    expect(onProposal).toHaveBeenCalledOnce()
    fireEvent.click(screen.getByRole('checkbox', { name: /Nur Kalkulationsprobe/ }))
    await waitFor(() => expect(screen.queryByRole('button', { name: 'Geprüften Vorschlag übernehmen' })).not.toBeInTheDocument())
  })
})
