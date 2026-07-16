import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { ConsultingCases } from '@/features/feed-advice/ConsultingCases'

const listConsultingCasesMock = vi.hoisted(() => vi.fn())
const getConsultingCaseMock = vi.hoisted(() => vi.fn())
const createConsultingCaseMock = vi.hoisted(() => vi.fn())
const addConsultingObservationMock = vi.hoisted(() => vi.fn())
const closeConsultingCaseMock = vi.hoisted(() => vi.fn())
const listCaseMeasuresMock = vi.hoisted(() => vi.fn())
const transitionFeedingMeasureMock = vi.hoisted(() => vi.fn())
const createConsultingReportDraftMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api/feeding-consulting', () => ({
  listConsultingCases: listConsultingCasesMock,
  getConsultingCase: getConsultingCaseMock,
  createConsultingCase: createConsultingCaseMock,
  addConsultingObservation: addConsultingObservationMock,
  closeConsultingCase: closeConsultingCaseMock,
  listCaseMeasures: listCaseMeasuresMock,
  transitionFeedingMeasure: transitionFeedingMeasureMock,
  createConsultingReportDraft: createConsultingReportDraftMock,
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
    listCaseMeasuresMock.mockReset().mockResolvedValue([])
    transitionFeedingMeasureMock.mockReset()
    createConsultingReportDraftMock.mockReset()
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

  it('schliesst eine Massnahme nur nach expliziter Wirksamkeitskontrolle', async () => {
    listCaseMeasuresMock.mockResolvedValue([{
      measure_id: 'm-1', title: 'Waage pruefen', version: 3, status: 'review_due',
      owner_subject: 'stall-team', due_date: '2026-07-18', escalation_status: 'none',
    }])
    transitionFeedingMeasureMock.mockResolvedValue({
      measure_id: 'm-1', version: 4, status: 'completed', effectiveness: 'effective',
    })
    render(<ConsultingCases initialCaseId="c-1" />)

    expect(await screen.findByText('Waage pruefen')).toBeInTheDocument()
    await userEvent.click(screen.getByRole('button', { name: /Wirksamkeit bestätigen/ }))
    await userEvent.selectOptions(screen.getByLabelText('Bewertung der Wirksamkeit'), 'effective')
    await userEvent.type(
      screen.getByLabelText('Ergebnis der Wirksamkeitskontrolle'),
      'Abweichung liegt an drei Folgetagen unter der Warnschwelle',
    )
    await userEvent.click(screen.getByRole('button', { name: /Maßnahme abschließen/ }))
    await waitFor(() => expect(transitionFeedingMeasureMock).toHaveBeenCalledWith('m-1', {
      expected_version: 3,
      target_status: 'completed',
      reason: 'Wirksamkeitskontrolle im Beratungsfall abgeschlossen',
      effectiveness: 'effective',
      effectiveness_result: 'Abweichung liegt an drei Folgetagen unter der Warnschwelle',
    }))
  })

  it.each([
    {
      status: 'open',
      action: /Bearbeitung starten/,
      targetStatus: 'in_progress',
      reason: 'Bearbeitung im Beratungsfall gestartet',
    },
    {
      status: 'in_progress',
      action: /Wirksamkeitskontrolle einplanen/,
      targetStatus: 'review_due',
      reason: 'Umsetzung erfolgt und Wirksamkeitskontrolle eingeplant',
    },
  ])('fuehrt eine Massnahme aus $status in den naechsten Arbeitsstand', async ({
    status, action, targetStatus, reason,
  }) => {
    listCaseMeasuresMock.mockResolvedValue([{
      measure_id: 'm-next', title: 'Mischreihenfolge pruefen', version: 2, status,
      owner_subject: 'stall-team', due_date: '2026-07-18', escalation_status: 'none',
    }])
    transitionFeedingMeasureMock.mockResolvedValue({
      measure_id: 'm-next', version: 3, status: targetStatus,
    })
    render(<ConsultingCases initialCaseId="c-1" />)

    await userEvent.click(await screen.findByRole('button', { name: action }))
    await waitFor(() => expect(transitionFeedingMeasureMock).toHaveBeenCalledWith('m-next', {
      expected_version: 2,
      target_status: targetStatus,
      reason,
    }))
  })

  it('erzeugt einen reproduzierbaren Berichtentwurf ohne PDF-Versprechen', async () => {
    createConsultingReportDraftMock.mockResolvedValue({
      id: 'r-1', case_id: 'c-1', version: 2, content_hash: 'abc', content: {},
    })
    render(<ConsultingCases initialCaseId="c-1" />)
    await screen.findByText(/Silage warm/)
    await userEvent.click(screen.getByRole('button', { name: /Berichtentwurf erzeugen/ }))
    await waitFor(() => expect(createConsultingReportDraftMock).toHaveBeenCalledWith(
      'c-1', 'Aktuellen Beratungsstand reproduzierbar festhalten'))
    expect(await screen.findByText(/Berichtentwurf v2/)).toBeInTheDocument()
    expect(screen.queryByText(/PDF erstellt/)).not.toBeInTheDocument()
  })
})
