import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ConsultingCases } from '@/features/feed-advice/ConsultingCases'

const listConsultingCasesMock = vi.hoisted(() => vi.fn())
const getConsultingCaseMock = vi.hoisted(() => vi.fn())
const createConsultingCaseMock = vi.hoisted(() => vi.fn())
const addConsultingObservationMock = vi.hoisted(() => vi.fn())
const closeConsultingCaseMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api/feeding-consulting', () => ({
  listConsultingCases: listConsultingCasesMock,
  getConsultingCase: getConsultingCaseMock,
  createConsultingCase: createConsultingCaseMock,
  addConsultingObservation: addConsultingObservationMock,
  closeConsultingCase: closeConsultingCaseMock,
}))

const openCase = {
  id: 'c-1', case_type: 'visit', title: 'Stallbesuch Hochleistung', status: 'open',
  initial_situation: 'Futteraufnahme schwankt.', created_by: 'berater', created_at: '2026-07-16T08:00:00Z',
  updated_at: '2026-07-16T08:00:00Z', observation_count: 1,
}

const caseDetail = {
  ...openCase,
  observations: [{
    id: 'o-1', case_id: 'c-1', category: 'fuetterung', text: 'Silage warm, Restfutter selektiert.',
    photo_document_refs: ['dms://beleg/1'], client_ref: 'web-1', created_by: 'berater',
    created_at: '2026-07-16T08:10:00Z',
  }],
}

describe('ConsultingCases', () => {
  beforeEach(() => {
    listConsultingCasesMock.mockReset().mockResolvedValue([openCase])
    getConsultingCaseMock.mockReset().mockResolvedValue(caseDetail)
    addConsultingObservationMock.mockReset()
    closeConsultingCaseMock.mockReset()
  })

  it('zeigt die Worklist und oeffnet den Fall mit chronologischen Beobachtungen', async () => {
    render(<ConsultingCases />)

    expect(await screen.findByText('Stallbesuch Hochleistung')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /Stallbesuch Hochleistung/ }))

    expect(await screen.findByText(/Silage warm/)).toBeInTheDocument()
    expect(screen.getByText(/Futteraufnahme schwankt/)).toBeInTheDocument()
  })

  it('erfasst eine Beobachtung mit Guard und eindeutiger client_ref', async () => {
    addConsultingObservationMock.mockResolvedValue({
      id: 'o-2', duplicate: false, category: 'tier', text: 'Neue Beobachtung',
      photo_document_refs: [], client_ref: 'x', case_id: 'c-1',
      created_by: 'berater', created_at: '2026-07-16T09:00:00Z',
    })
    render(<ConsultingCases initialCaseId="c-1" />)
    await screen.findByText(/Silage warm/)

    await userEvent.type(screen.getByLabelText(/^Beobachtung$/), 'Kuehe selektieren am Futtertisch')
    await userEvent.click(screen.getByRole('button', { name: /Beobachtung erfassen/ }))

    await waitFor(() => {
      expect(addConsultingObservationMock).toHaveBeenCalledWith('c-1', expect.objectContaining({
        text: 'Kuehe selektieren am Futtertisch',
        client_ref: expect.stringMatching(/.+/),
      }))
    })
    expect(await screen.findByText(/Beobachtung gespeichert/)).toBeInTheDocument()
  })

  it('zeigt Ladefehler handlungsorientiert', async () => {
    listConsultingCasesMock.mockRejectedValueOnce(new Error('kaputt'))
    render(<ConsultingCases />)
    expect(await screen.findByRole('alert')).toHaveTextContent(/konnten nicht geladen werden/)
  })
})
