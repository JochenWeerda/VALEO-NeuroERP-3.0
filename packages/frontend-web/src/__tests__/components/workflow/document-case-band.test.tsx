import { render, screen } from '@testing-library/react'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import { MemoryRouter } from '@/app/routing/test-router'
import { DocumentCaseBand } from '@/components/workflow/DocumentCaseBand'

/**
 * FSX-012-Nachlauf und FSX-013-Rollout auf bestehende Belege.
 *
 * Die heikle Aussage dieser Flaeche ist die **Abwesenheit**: „Kein Vorgang zu
 * diesem Beleg" ist eine Behauptung, und sie darf erst fallen, wenn wirklich
 * gesucht wurde. Waehrend der Suche ist Schweigen die richtige Antwort.
 *
 * Nach einem **Abrufsfehler** dagegen nicht mehr — das war F5 aus der
 * Begehung: Ein fehlendes Band war nicht von „kein Prozess" zu unterscheiden.
 * Der Ausfall bekommt deshalb eine eigene Zeile, die ueber den Vorgang nichts
 * behauptet, sondern ueber den eigenen Kenntnisstand: nicht ermittelt.
 */

const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: { get: getMock },
}))

// Das Prozessband selbst ist anderswo getestet; hier zaehlt nur, ob es kommt.
vi.mock('@/components/workflow/WorkflowProcessBand', () => ({
  WorkflowProcessBand: ({ context }: { context: { instanceId: string } }) => (
    <div data-testid="process-band-stub" data-instance={context.instanceId} />
  ),
}))

function renderBand(props: Partial<Parameters<typeof DocumentCaseBand>[0]> = {}) {
  return render(
    <MemoryRouter>
      <DocumentCaseBand documentType="purchase_order" documentId="BE-1" {...props} />
    </MemoryRouter>,
  )
}

describe('DocumentCaseBand', () => {
  beforeEach(() => {
    getMock.mockReset()
  })

  it('sucht nicht, solange der Beleg keine Nummer hat', () => {
    renderBand({ documentId: undefined, onLink: vi.fn() })
    expect(getMock).not.toHaveBeenCalled()
    expect(screen.queryByTestId('document-case-link-offer')).not.toBeInTheDocument()
  })

  it('zeigt das Prozessband, wenn der Beleg zu einem Vorgang gehoert', async () => {
    getMock.mockResolvedValue({
      data: { instances: [{ instance_id: 'wf-1', process_key: 'procure-to-pay', role: 'leading' }] },
    })
    renderBand({ onLink: vi.fn() })

    const band = await screen.findByTestId('process-band-stub')
    expect(band).toHaveAttribute('data-instance', 'wf-1')
    expect(screen.queryByTestId('document-case-link-offer')).not.toBeInTheDocument()
  })

  it('bevorzugt den fuehrenden Vorgang vor einer blossen Beteiligung', async () => {
    getMock.mockResolvedValue({
      data: {
        instances: [
          { instance_id: 'wf-fremd', process_key: 'order-to-cash', role: 'participant' },
          { instance_id: 'wf-eigen', process_key: 'procure-to-pay', role: 'leading' },
        ],
      },
    })
    renderBand({ onLink: vi.fn() })

    // Der fuehrende Vorgang beschreibt diesen Beleg; die Beteiligung an einer
    // Sammelrechnung beschreibt einen anderen Vorgang.
    expect(await screen.findByTestId('process-band-stub')).toHaveAttribute('data-instance', 'wf-eigen')
  })

  it('bietet die Verknuepfung an, wenn kein Vorgang gefunden wurde', async () => {
    getMock.mockResolvedValue({ data: { instances: [] } })
    renderBand({ onLink: vi.fn(), linkLabel: 'Beschaffungsvorgang verknuepfen' })

    expect(await screen.findByTestId('document-case-link-offer')).toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Beschaffungsvorgang verknuepfen' })).toBeInTheDocument()
  })

  it('meldet nach einem Abrufsfehler den eigenen Kenntnisstand (F5)', async () => {
    getMock.mockRejectedValue(new Error('Netz weg'))
    renderBand({ onLink: vi.fn() })

    // Frueher blieb die Flaeche hier leer. Genau das war F5: Ein fehlendes Band
    // war nicht von „kein Prozess" zu unterscheiden — der Beleg sah in beiden
    // Faellen gleich aus, und das Schweigen wurde als Auskunft gelesen.
    const hinweis = await screen.findByTestId('document-case-unknown')
    expect(hinweis).toHaveTextContent('Prozessstand nicht ermittelt')
    // Ueber den Vorgang selbst wird weiterhin nichts behauptet.
    expect(hinweis).toHaveTextContent(/keine Aussage darueber, dass keiner existiert/)
    expect(screen.queryByTestId('document-case-link-offer')).not.toBeInTheDocument()
  })

  it('schweigt, solange die Suche laeuft', async () => {
    let aufloesen: (wert: unknown) => void = () => {}
    getMock.mockReturnValue(new Promise((resolve) => {
      aufloesen = resolve
    }))
    const { container } = renderBand({ onLink: vi.fn() })

    // Waehrend der Suche ist Schweigen richtig: Das ist ein Augenblick, keine
    // Auskunft. Erst ihr Ausgang ist eine.
    expect(container).toBeEmptyDOMElement()

    aufloesen({ data: { instances: [] } })
    expect(await screen.findByTestId('document-case-link-offer')).toBeInTheDocument()
  })

  it('nennt die Abwesenheit auch ohne Verknuepfungsangebot', async () => {
    getMock.mockResolvedValue({ data: { instances: [] } })
    renderBand({ onLink: undefined })

    // Die Auskunft haengt nicht daran, ob die Maske etwas dagegen tun kann:
    // Sonst fiele der gepruefte Fall wieder mit dem unbekannten zusammen.
    expect(await screen.findByTestId('document-case-link-offer')).toBeInTheDocument()
    // Eine Schaltflaeche ohne Wirkung waere aber weiterhin schlimmer als keine.
    expect(screen.queryByRole('button')).not.toBeInTheDocument()
  })

  it('sucht nach erfolgreicher Verknuepfung erneut', async () => {
    getMock.mockResolvedValue({ data: { instances: [] } })
    const onLink = vi.fn().mockResolvedValue(undefined)
    const user = userEvent.setup()
    renderBand({ onLink })

    await screen.findByTestId('document-case-link-offer')
    getMock.mockResolvedValue({
      data: { instances: [{ instance_id: 'wf-neu', process_key: 'procure-to-pay', role: 'leading' }] },
    })
    await user.click(screen.getByRole('button', { name: 'Vorgang verknuepfen' }))

    expect(await screen.findByTestId('process-band-stub')).toHaveAttribute('data-instance', 'wf-neu')
  })

  it('zeigt einen Fehlschlag der Verknuepfung an, statt ihn zu verschlucken', async () => {
    getMock.mockResolvedValue({ data: { instances: [] } })
    const onLink = vi.fn().mockRejectedValue(new Error('Vorgang bereits an anderen Beleg gebunden'))
    const user = userEvent.setup()
    renderBand({ onLink })

    await screen.findByTestId('document-case-link-offer')
    await user.click(screen.getByRole('button', { name: 'Vorgang verknuepfen' }))

    expect(await screen.findByText(/bereits an anderen Beleg gebunden/)).toBeInTheDocument()
  })

  it('nimmt den Handover aus dem Leitstand, ohne zu suchen', async () => {
    renderBand({
      handoverContext: {
        process: 'procure-to-pay',
        instanceId: 'wf-handover',
        caseNumber: 'WF-1',
        label: '',
        partnerName: '',
        subject: '',
        entryMode: '',
      },
      onLink: vi.fn(),
    })

    expect(screen.getByTestId('process-band-stub')).toHaveAttribute('data-instance', 'wf-handover')
    expect(getMock).not.toHaveBeenCalled()
  })
})
