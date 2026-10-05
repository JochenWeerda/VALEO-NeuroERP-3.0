import { render, screen, waitFor } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { RationEditor } from '@/features/feed-advice/RationEditor'

const fetchRationDetailMock = vi.hoisted(() => vi.fn())
const evaluateRationDraftMock = vi.hoisted(() => vi.fn())
const createRationVersionMock = vi.hoisted(() => vi.fn())
const listFeedingFeedsMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api/rations-lifecycle', () => ({
  fetchRationDetail: fetchRationDetailMock,
}))

vi.mock('@/lib/api/feeding-ration-editor', () => ({
  evaluateRationDraft: evaluateRationDraftMock,
  createRationVersion: createRationVersionMock,
}))

vi.mock('@/lib/api/feeding-feed-catalog', () => ({
  listFeedingFeeds: listFeedingFeedsMock,
}))

const ration = {
  id: 'r-1',
  group_id: 'g-1',
  group_name: 'Hochleistung',
  name: 'Sommerration',
  latest_version_id: 'v-3',
  latest_version_no: 3,
  latest_status: 'draft',
  versions: [{
    id: 'v-3', version_no: 3, status: 'draft', snapshot: {
      components: [{ feed_id: 'f-gras', name: 'Grassilage', kg_fm: 24 }],
    }, snapshot_checksum: 'c',
  }],
  audit: [],
}

const evaluation = {
  group_id: 'g-1',
  requirement_profile_id: 'p-1',
  positions: [{ feed_id: 'f-gras', name: 'Grassilage', kg_fm: 24, kg_tm: 8.4, cost_eur: 1.68, me_mj: 88.2 }],
  totals: { dm_kg: 8.4, fm_kg: 24, cost_eur: 1.68, me_mj: 88.2, sidp_g: 588 },
  coverage: {},
  deltas: [{ metric: 'me_mj', actual: 88.2, target: 210, delta: -121.8 }],
  findings: [{ code: 'energy_deficit', severity: 'warning', metric: 'me_mj', actual: 88.2, target: 210, message: 'Energie: 88 deckt den Bedarf von 210 nicht.' }],
}

describe('RationEditor', () => {
  beforeEach(() => {
    fetchRationDetailMock.mockReset()
    evaluateRationDraftMock.mockReset()
    createRationVersionMock.mockReset()
    listFeedingFeedsMock.mockReset()
    listFeedingFeedsMock.mockResolvedValue([])
    fetchRationDetailMock.mockResolvedValue(ration)
    evaluateRationDraftMock.mockResolvedValue(evaluation)
  })

  it('laedt die Ration, zeigt Positionen und die permanente Bewertung mit Befundtext', async () => {
    render(<RationEditor rationId="r-1" />)

    expect(await screen.findByRole('heading', { name: /Sommerration/ })).toBeInTheDocument()
    expect(screen.getByDisplayValue('24')).toBeInTheDocument()
    expect(await screen.findByText(/deckt den Bedarf von 210 nicht/)).toBeInTheDocument()
    expect(screen.getByTestId('ration-editor-evaluation')).toHaveTextContent('8,4')
    // Herkunft der Bewertung ist sichtbar (Bedarfsprofil)
    expect(screen.getByTestId('ration-editor-evaluation')).toHaveTextContent('p-1')
  })

  it('bewertet nach Mengenaenderung neu und speichert als neue Version mit optimistischer Revision', async () => {
    createRationVersionMock.mockResolvedValue({ id: 'v-4', version_no: 4 })
    render(<RationEditor rationId="r-1" />)
    await screen.findByRole('heading', { name: /Sommerration/ })

    const amount = screen.getByLabelText(/Menge Grassilage/)
    await userEvent.clear(amount)
    await userEvent.type(amount, '30')
    await waitFor(() => {
      expect(evaluateRationDraftMock).toHaveBeenLastCalledWith(
        expect.objectContaining({
          group_id: 'g-1',
          components: [expect.objectContaining({ feed_id: 'f-gras', kg_fm: 30 })],
        }),
      )
    })

    await userEvent.click(screen.getByRole('button', { name: /Als neue Version speichern/ }))
    await waitFor(() => {
      expect(createRationVersionMock).toHaveBeenCalledWith('r-1', expect.objectContaining({
        expected_latest_version_no: 3,
        snapshot: expect.objectContaining({
          components: [expect.objectContaining({ feed_id: 'f-gras', kg_fm: 30 })],
        }),
      }))
    })
    expect(await screen.findByText(/Version 4 gespeichert/)).toBeInTheDocument()
  })

  it('zeigt Lade-Fehler handlungsorientiert mit erneutem Versuch', async () => {
    fetchRationDetailMock.mockRejectedValueOnce(new Error('kaputt'))
    render(<RationEditor rationId="r-1" />)

    expect(await screen.findByRole('alert')).toHaveTextContent(/konnte nicht geladen werden/)
    await userEvent.click(screen.getByRole('button', { name: /Erneut laden/ }))
    expect(await screen.findByRole('heading', { name: /Sommerration/ })).toBeInTheDocument()
  })

  it('bewahrt Min/Max im Draft, zeigt Grenzkonflikte und fokussiert die verursachende Position', async () => {
    evaluateRationDraftMock.mockResolvedValue({
      ...evaluation,
      findings: [{ code: 'bounds_conflict', severity: 'critical', metric: 'bounds',
        actual: 28, target: 20, feed_id: 'f-gras', message: 'Grassilage: Mindestmenge liegt ueber Hoechstmenge.',
        remediation: 'Minimum auf 20 kg senken.' }],
    })
    createRationVersionMock.mockResolvedValue({ id: 'v-4', version_no: 4 })
    render(<RationEditor rationId="r-1" />)
    await screen.findByRole('heading', { name: /Sommerration/ })

    await userEvent.type(screen.getByLabelText(/Minimum Grassilage/), '28')
    await userEvent.type(screen.getByLabelText(/Maximum Grassilage/), '20')
    await waitFor(() => expect(evaluateRationDraftMock).toHaveBeenLastCalledWith(expect.objectContaining({
      components: [expect.objectContaining({ feed_id: 'f-gras', min_kg_fm: 28, max_kg_fm: 20 })],
    })))

    await userEvent.click(await screen.findByRole('button', { name: /Mindestmenge liegt ueber/ }))
    expect(screen.getByText(/Abhilfe: Minimum auf 20 kg senken/)).toBeInTheDocument()
    expect(screen.getByLabelText(/Menge Grassilage/)).toHaveFocus()
    await userEvent.click(screen.getByRole('button', { name: /Als neue Version speichern/ }))
    await waitFor(() => expect(createRationVersionMock).toHaveBeenCalledWith('r-1', expect.objectContaining({
      snapshot: expect.objectContaining({ components: [expect.objectContaining({
        min_kg_fm: 28, max_kg_fm: 20,
      })] }),
    })))
  })
})

describe('RationEditor Komfortstufe (FEED-EDITOR-041)', () => {
  beforeEach(() => {
    fetchRationDetailMock.mockReset()
    evaluateRationDraftMock.mockReset()
    createRationVersionMock.mockReset()
    listFeedingFeedsMock.mockReset()
    listFeedingFeedsMock.mockResolvedValue([])
    fetchRationDetailMock.mockResolvedValue({
      ...ration,
      versions: [{
        id: 'v-3', version_no: 3, status: 'draft', snapshot: {
          components: [
            { feed_id: 'f-gras', name: 'Grassilage', kg_fm: 24 },
            { feed_id: 'f-min', name: 'Mineral', kg_fm: 0.2 },
          ],
        }, snapshot_checksum: 'c',
      }],
    })
    evaluateRationDraftMock.mockResolvedValue({
      ...evaluation,
      positions: [
        { ...evaluation.positions[0], ca_g: 42, p_g: 24.5 },
        { feed_id: 'f-min', name: 'Mineral', kg_fm: 0.2, kg_tm: 0.18, cost_eur: 0.09 },
      ],
    })
  })

  it('macht Aenderungen rueckgaengig und stellt sie wieder her (auch per Tastatur)', async () => {
    render(<RationEditor rationId="r-1" />)
    await screen.findByRole('heading', { name: /Sommerration/ })

    const undoButton = screen.getByRole('button', { name: /^Rückgängig$/ })
    const redoButton = screen.getByRole('button', { name: /^Wiederholen$/ })
    expect(undoButton).toBeDisabled()
    expect(redoButton).toBeDisabled()

    const amount = screen.getByLabelText(/Menge Grassilage/)
    await userEvent.clear(amount)
    await userEvent.type(amount, '30')
    expect(screen.getByLabelText(/Menge Grassilage/)).toHaveValue(30)

    // Undo stellt exakt den vorherigen Draft her (zusammenhaengende Eingabe = 1 Schritt)
    await userEvent.click(undoButton)
    expect(screen.getByLabelText(/Menge Grassilage/)).toHaveValue(24)
    expect(undoButton).toBeDisabled()

    await userEvent.click(redoButton)
    expect(screen.getByLabelText(/Menge Grassilage/)).toHaveValue(30)

    // Tastatur: Strg+Z
    await userEvent.keyboard('{Control>}z{/Control}')
    expect(screen.getByLabelText(/Menge Grassilage/)).toHaveValue(24)
  })

  it('sortiert die Mischreihenfolge und persistiert sie im Snapshot', async () => {
    createRationVersionMock.mockResolvedValue({ id: 'v-4', version_no: 4 })
    render(<RationEditor rationId="r-1" />)
    await screen.findByRole('heading', { name: /Sommerration/ })

    // erste Position kann nicht weiter nach oben
    expect(screen.getByRole('button', { name: /Grassilage nach oben/ })).toBeDisabled()
    await userEvent.click(screen.getByRole('button', { name: /Grassilage nach unten/ }))

    const rows = screen.getAllByRole('row').slice(1) // ohne Kopfzeile
    expect(rows[0]).toHaveTextContent('Mineral')
    expect(rows[1]).toHaveTextContent('Grassilage')

    await userEvent.click(screen.getByRole('button', { name: /Als neue Version speichern/ }))
    await waitFor(() => {
      expect(createRationVersionMock).toHaveBeenCalledWith('r-1', expect.objectContaining({
        snapshot: expect.objectContaining({
          components: [
            expect.objectContaining({ feed_id: 'f-min', mixing_sequence: 1 }),
            expect.objectContaining({ feed_id: 'f-gras', mixing_sequence: 2 }),
          ],
        }),
      }))
    })
  })

  it('springt mit Enter zur naechsten Position (Tastatur-Journey)', async () => {
    render(<RationEditor rationId="r-1" />)
    await screen.findByRole('heading', { name: /Sommerration/ })

    const first = screen.getByLabelText(/Menge Grassilage/)
    first.focus()
    await userEvent.keyboard('{Enter}')
    expect(screen.getByLabelText(/Menge Mineral/)).toHaveFocus()
  })

  it('blendet Expertenspalten (Mineralstoffe) erst nach Aktivierung ein', async () => {
    render(<RationEditor rationId="r-1" />)
    await screen.findByRole('heading', { name: /Sommerration/ })

    expect(screen.queryByRole('columnheader', { name: 'Ca (g)' })).not.toBeInTheDocument()
    const toggle = screen.getByRole('button', { name: /Expertenspalten/ })
    expect(toggle).toHaveAttribute('aria-pressed', 'false')

    await userEvent.click(toggle)
    expect(toggle).toHaveAttribute('aria-pressed', 'true')
    expect(screen.getByRole('columnheader', { name: 'Ca (g)' })).toBeInTheDocument()
    expect(screen.getByRole('columnheader', { name: 'P (g)' })).toBeInTheDocument()
    // Wert vorhanden -> formatiert; fehlend -> "–" (nie 0 fabriziert)
    expect(screen.getByText('42,0')).toBeInTheDocument()
    const mineralRow = screen.getAllByRole('row').find((row) => row.textContent?.includes('Mineral'))
    expect(mineralRow?.textContent).toContain('–')
  })
})

describe('RationEditor Befund-Navigation (FEED-EDITOR-022)', () => {
  beforeEach(() => {
    fetchRationDetailMock.mockReset()
    evaluateRationDraftMock.mockReset()
    createRationVersionMock.mockReset()
    listFeedingFeedsMock.mockReset()
    listFeedingFeedsMock.mockResolvedValue([])
    fetchRationDetailMock.mockResolvedValue({
      ...ration,
      versions: [{
        id: 'v-3', version_no: 3, status: 'draft', snapshot: {
          components: [
            { feed_id: 'f-gras', name: 'Grassilage', kg_fm: 24 },
            { feed_id: 'f-min', name: 'Mineral', kg_fm: 0.2 },
          ],
        }, snapshot_checksum: 'c',
      }],
    })
    evaluateRationDraftMock.mockResolvedValue({
      ...evaluation,
      positions: [
        ...evaluation.positions,
        { feed_id: 'f-min', name: 'Mineral', kg_fm: 0.2, kg_tm: 0.18, cost_eur: 0.09 },
      ],
      coverage: { sidp_g: { complete: false, missing_feed_ids: ['f-min'] } },
      findings: [
        { code: 'energy_deficit', severity: 'high', metric: 'me_mj', actual: 88.2, target: 210, message: 'Energie: Unterdeckung.' },
        { code: 'sidp_g_incomplete', severity: 'info', metric: 'sidp_g', actual: 588, target: null, message: 'sidP: Summe unvollstaendig.' },
      ],
    })
  })

  it('fokussiert per Befund-Klick die verursachende Position (Warnung -> Ursache)', async () => {
    render(<RationEditor rationId="r-1" />)
    await screen.findByRole('heading', { name: /Sommerration/ })
    await screen.findByText(/Summe unvollstaendig/)

    await userEvent.click(screen.getByRole('button', { name: /sidP: Summe unvollstaendig/ }))
    expect(screen.getByLabelText(/Menge Mineral/)).toHaveFocus()

    await userEvent.click(screen.getByRole('button', { name: /Energie: Unterdeckung/ }))
    expect(screen.getByLabelText(/Menge Grassilage/)).toHaveFocus()
  })

  it('zeigt die vier Prioritaetsstufen mit Textlabel', async () => {
    render(<RationEditor rationId="r-1" />)
    await screen.findByText(/Summe unvollstaendig/)
    expect(screen.getByText('Hoch')).toBeInTheDocument()
    expect(screen.getByText('Hinweis')).toBeInTheDocument()
  })
})
