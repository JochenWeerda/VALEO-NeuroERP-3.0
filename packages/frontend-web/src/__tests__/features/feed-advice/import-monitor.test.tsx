import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ImportMonitor } from '@/features/feed-advice/ImportMonitor'

const listImportJobsMock = vi.hoisted(() => vi.fn())
const acceptImportJobMock = vi.hoisted(() => vi.fn())
const rejectImportJobMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api/feeding-import-monitor', () => ({
  listImportJobs: listImportJobsMock,
  acceptImportJob: acceptImportJobMock,
  rejectImportJob: rejectImportJobMock,
}))

const validatedJob = {
  id: 'j-1', adapter: 'laboratory', status: 'validated', findings: [],
  mapped_excerpt: { external_id: 'probe-1', target_model: 'FeedIngredient' },
  created_by: 'import', created_at: '2026-07-16T08:00:00Z',
}
const quarantinedJob = {
  id: 'j-2', adapter: 'laboratory', status: 'quarantined',
  findings: [{ severity: 'high', message: 'Labor-TM muss in Prozent vorliegen.' }],
  mapped_excerpt: {}, created_by: 'import', created_at: '2026-07-16T08:05:00Z',
}

describe('ImportMonitor', () => {
  beforeEach(() => {
    listImportJobsMock.mockReset().mockResolvedValue([validatedJob, quarantinedJob])
    acceptImportJobMock.mockReset()
    rejectImportJobMock.mockReset()
  })

  it('zeigt Auftraege mit Status und Validierungsbefunden', async () => {
    render(<ImportMonitor />)

    expect(await screen.findByText('probe-1')).toBeInTheDocument()
    expect(screen.getByText(/Labor-TM muss in Prozent/)).toBeInTheDocument()
    expect(screen.getByText('Quarantäne')).toBeInTheDocument()
  })

  it('uebernimmt validierte Auftraege mit Guard und verlangt Begruendung beim Verwerfen', async () => {
    acceptImportJobMock.mockResolvedValue({ ...validatedJob, status: 'accepted', result_ref: 'imp-1' })
    rejectImportJobMock.mockResolvedValue({ ...quarantinedJob, status: 'rejected', decision_reason: 'unplausibel' })
    render(<ImportMonitor />)
    await screen.findByText('probe-1')

    await userEvent.click(screen.getByRole('button', { name: /Übernehmen/ }))
    await waitFor(() => expect(acceptImportJobMock).toHaveBeenCalledWith('j-1'))
    expect(await screen.findByText(/übernommen/i)).toBeInTheDocument()

    // Verwerfen ohne Begruendung bleibt deaktiviert (zweite Zeile = Quarantaene-Job)
    const rejectButtons = screen.getAllByRole('button', { name: /^Verwerfen$/ })
    await userEvent.click(rejectButtons[rejectButtons.length - 1])
    const reason = await screen.findByLabelText(/Begründung/)
    const confirm = screen.getByRole('button', { name: /Verwerfen bestätigen/ })
    expect(confirm).toBeDisabled()
    await userEvent.type(reason, 'Analysewerte unplausibel')
    expect(confirm).toBeEnabled()
    await userEvent.click(confirm)
    await waitFor(() => expect(rejectImportJobMock).toHaveBeenCalledWith('j-2', 'Analysewerte unplausibel'))
  })

  it('zeigt Ladefehler handlungsorientiert', async () => {
    listImportJobsMock.mockRejectedValueOnce(new Error('kaputt'))
    render(<ImportMonitor />)
    expect(await screen.findByRole('alert')).toHaveTextContent(/konnte nicht geladen werden/)
  })
})
