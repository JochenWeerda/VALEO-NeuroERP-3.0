import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, beforeEach, vi } from 'vitest'
import { MemoryRouter } from '@/app/routing/react-router-compat'
import BestellungAnlegenPage from '@/pages/einkauf/bestellung-anlegen'

const postMock = vi.hoisted(() => vi.fn())
const getMock = vi.hoisted(() => vi.fn())
const toastMock = vi.hoisted(() => vi.fn())

const translations: Record<string, string> = {
  'crud.entities.supplier': 'Lieferant',
  'crud.fields.supplier': 'Lieferant',
  'crud.fields.deliveryDate': 'Liefertermin',
  'crud.fields.paymentTerms': 'Zahlungsbedingung',
  'crud.fields.paymentTermsNet30': '30 Tage',
  'crud.fields.paymentTermsNet14': '14 Tage',
  'crud.fields.paymentTermsNet7': '7 Tage',
  'crud.fields.paymentTermsPrepay': 'Vorkasse',
  'crud.fields.incoterms': 'Incoterms',
  'crud.tooltips.placeholders.incoterms': 'Incoterms auswaehlen',
  'crud.fields.deliveryAddress': 'Lieferadresse',
  'crud.tooltips.placeholders.deliveryAddress': 'Lieferadresse erfassen',
  'crud.fields.requisition': 'Bedarfsmeldung',
  'crud.fields.contract': 'Vertrag',
  'crud.fields.rfq': 'Anfrage',
  'crud.fields.items': 'Positionen',
  'crud.fields.product': 'Artikel',
  'crud.fields.quantity': 'Menge',
  'crud.fields.unit': 'Einheit',
  'crud.fields.price': 'Preis',
  'crud.fields.total': 'Summe',
  'crud.actions.addItem': 'Position hinzufuegen',
  'crud.entities.delivery': 'Lieferung',
  'crud.fields.notes': 'Notizen',
  'common.optional': 'optional',
  'crud.detail.summary': 'Zusammenfassung',
  'crud.detail.basicInfo': 'Grunddaten',
  'crud.actions.new': 'Neu',
  'crud.actions.create': 'anlegen',
  'crud.fields.standard': 'Standard',
  'crud.messages.validationError': 'Validierung fehlgeschlagen',
  'common.error': 'Fehler',
  'crud.messages.createError': 'Erstellen fehlgeschlagen.',
}

vi.mock('react-i18next', () => ({
  useTranslation: () => ({
    t: (key: string, options?: { defaultValue?: string }) => options?.defaultValue ?? translations[key] ?? key,
  }),
}))

vi.mock('@/components/patterns/Wizard', async () => {
  const React = await vi.importActual<typeof import('react')>('react')

  return {
    Wizard: ({
      title,
      steps,
      onFinish,
      getStepValidationError,
      onStepValidationError,
    }: {
      title: string
      steps: Array<{ id: string; title: string; content: JSX.Element }>
      onFinish?: () => void
      getStepValidationError?: (stepId: string) => string | null
      onStepValidationError?: (stepId: string, message: string) => void
    }) => {
      const [activeIndex, setActiveIndex] = React.useState(0)
      const activeStep = steps[activeIndex]

      const handleNext = () => {
        const validationError = getStepValidationError?.(activeStep.id)
        if (validationError) {
          onStepValidationError?.(activeStep.id, validationError)
          return
        }

        if (activeIndex === steps.length - 1) {
          void onFinish?.()
          return
        }

        setActiveIndex((prev) => prev + 1)
      }

      return (
        <div>
          <h1>{title}</h1>
          <div>Aktiver Schritt: {activeStep.title}</div>
          <section key={activeStep.id}>{activeStep.content}</section>
          <button type="button" onClick={() => setActiveIndex((prev) => Math.max(0, prev - 1))}>
            Zurueck
          </button>
          <button type="button" onClick={handleNext}>
            {activeIndex === steps.length - 1 ? 'Abschliessen' : 'Weiter'}
          </button>
        </div>
      )
    },
  }
})

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    post: postMock,
    get: getMock,
  },
}))

vi.mock('@/hooks/use-toast', () => ({
  toast: toastMock,
}))

describe('BestellungAnlegenPage', () => {
  async function goToStep(stepTitle: string): Promise<void> {
    await waitFor(() => {
      expect(screen.getByText(`Aktiver Schritt: ${stepTitle}`)).toBeInTheDocument()
    })
  }

  beforeEach(() => {
    postMock.mockReset()
    getMock.mockReset()
    toastMock.mockReset()
    getMock.mockResolvedValue({ data: null })
  })

  it('uebernimmt den Procure-to-Pay-Handover in die Standardmaske', async () => {
    render(
      <MemoryRouter
        initialEntries={[
          '/einkauf/bestellungen/neu?workflowProcess=procure-to-pay&workflowInstanceId=wf-1&workflowCase=WF-2026-001&entryMode=Direktbestellung&partnerName=Agrarhandel%20Nord&subject=Saisonbedarf',
        ]}
      >
        <BestellungAnlegenPage />
      </MemoryRouter>,
    )

    expect(await screen.findByText('Workflow-Handover aus Procure-to-Pay')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByLabelText('Lieferant *')).toHaveValue('Agrarhandel Nord')
    })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Positionen')
    fireEvent.change(screen.getByPlaceholderText('Artikel'), { target: { value: 'Testprodukt' } })
    fireEvent.change(screen.getAllByRole('spinbutton')[1], { target: { value: '1' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Lieferung')
    const notesField = screen.getByLabelText('Notizen (optional)') as HTMLTextAreaElement
    expect(notesField.value).toContain('Workflow-Vorgang WF-2026-001')
    expect(notesField.value).toContain('Einstieg: Direktbestellung')
    expect(notesField.value).toContain('Saisonbedarf')
  })

  it('blockiert fachlich leere Direktbestellungen vor dem API-Call', async () => {
    render(
      <MemoryRouter initialEntries={['/einkauf/bestellungen/neu']}>
        <BestellungAnlegenPage />
      </MemoryRouter>,
    )

    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))

    await waitFor(() => {
      expect(postMock).not.toHaveBeenCalled()
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Validierung fehlgeschlagen',
          description: 'Lieferant ist ein Pflichtfeld.',
          variant: 'destructive',
        }),
      )
    })
  })

  it('sendet die Lieferadresse ueber shippingAddress an den Backend-Contract', async () => {
    postMock.mockResolvedValueOnce({})

    render(
      <MemoryRouter initialEntries={['/einkauf/bestellungen/neu?workflowProcess=procure-to-pay&subject=Rahmenabruf']}>
        <BestellungAnlegenPage />
      </MemoryRouter>,
    )

    fireEvent.change(screen.getByLabelText('Lieferant *'), { target: { value: 'Agrarhandel Nord' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Positionen')
    fireEvent.change(screen.getByPlaceholderText('Artikel'), { target: { value: 'Sojaschrot' } })
    fireEvent.change(screen.getAllByRole('spinbutton')[1], { target: { value: '42.5' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Lieferung')
    fireEvent.change(screen.getAllByLabelText('Lieferadresse')[0], { target: { value: 'Werk Nord, Tor 3' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Zusammenfassung')

    fireEvent.click(screen.getByRole('button', { name: 'Abschliessen' }))

    await waitFor(() => {
      expect(postMock).toHaveBeenCalledTimes(1)
    })

    expect(postMock).toHaveBeenCalledWith(
      '/api/v1/purchase-orders',
      expect.objectContaining({
        supplierId: 'Agrarhandel Nord',
        subject: 'Rahmenabruf',
        shippingAddress: 'Werk Nord, Tor 3',
        deliveryAddress: 'Werk Nord, Tor 3',
      }),
    )
  })

  it('laedt Bedarfsmeldungen ueber den realen Einkaufsanfrage-Contract vor', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        id: 'req-1',
        anfrageNummer: 'BANF-2026-001',
        anforderer: 'Disposition Nord',
        artikel: 'Sommergerste',
        menge: 24,
        faelligkeit: '2026-04-10',
        status: 'FREIGEGEBEN',
      },
    })

    render(
      <MemoryRouter initialEntries={['/einkauf/bestellungen/neu?requisitionId=req-1']}>
        <BestellungAnlegenPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(getMock).toHaveBeenCalledWith('/api/v1/einkauf/anfragen/req-1')
    })
    fireEvent.change(screen.getByLabelText('Lieferant *'), { target: { value: 'Agrarhandel Nord' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Positionen')
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Artikel')).toHaveValue('Sommergerste')
    })
    fireEvent.click(screen.getByRole('button', { name: 'Zurueck' }))
    await goToStep('Lieferant')
    expect(screen.getByDisplayValue('2026-04-10')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Positionen')
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Lieferung')
    const notesField = screen.getByLabelText('Notizen (optional)') as HTMLTextAreaElement
    expect(notesField.value).toContain('Bedarfsmeldung BANF-2026-001')
    expect(notesField.value).toContain('Anforderer: Disposition Nord')
  })

  it('laedt RFQ-Vorbelegung ueber denselben Einkaufsanfrage-Contract', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        id: 'rfq-1',
        anfrageNummer: 'RFQ-2026-008',
        artikel: 'Rapsschrot',
        menge: 12,
        faelligkeit: '2026-04-22',
        status: 'ANGEBOTSPHASE',
      },
    })

    render(
      <MemoryRouter initialEntries={['/einkauf/bestellungen/neu?rfqId=rfq-1']}>
        <BestellungAnlegenPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(getMock).toHaveBeenCalledWith('/api/v1/einkauf/anfragen/rfq-1')
    })
    fireEvent.change(screen.getByLabelText('Lieferant *'), { target: { value: 'Lieferant RFQ' } })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Positionen')
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Artikel')).toHaveValue('Rapsschrot')
    })
    fireEvent.click(screen.getByRole('button', { name: 'Zurueck' }))
    await goToStep('Lieferant')
    expect(screen.getByDisplayValue('2026-04-22')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Positionen')
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Lieferung')
    const notesField = screen.getByLabelText('Notizen (optional)') as HTMLTextAreaElement
    expect(notesField.value).toContain('RFQ-Bezug RFQ-2026-008')
    expect(notesField.value).toContain('RFQ-Status: ANGEBOTSPHASE')
  })

  it('laedt Vertragsabrufe ueber den Contract-Endpoint vor', async () => {
    getMock.mockResolvedValueOnce({
      data: {
        id: 'kon-1',
        contractNo: 'K-2026-004',
        counterpartyId: 'Lieferant-77',
        commodity: 'Mais',
        qty: { contracted: 18, unit: 'kg' },
        deliveryWindow: { to: '2026-05-01' },
      },
    })

    render(
      <MemoryRouter initialEntries={['/einkauf/bestellungen/neu?contractId=kon-1']}>
        <BestellungAnlegenPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(getMock).toHaveBeenCalledWith('/api/v1/contracts/kon-1')
    })
    await waitFor(() => {
      expect(screen.getByLabelText('Lieferant *')).toHaveValue('Lieferant-77')
    })
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Positionen')
    await waitFor(() => {
      expect(screen.getByPlaceholderText('Artikel')).toHaveValue('Mais')
    })
    fireEvent.click(screen.getByRole('button', { name: 'Zurueck' }))
    await goToStep('Lieferant')
    expect(screen.getByDisplayValue('2026-05-01')).toBeInTheDocument()
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Positionen')
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))
    await goToStep('Lieferung')
    const notesField = screen.getByLabelText('Notizen (optional)') as HTMLTextAreaElement
    expect(notesField.value).toContain('Vertragsbezug K-2026-004')
  })

  it('zeigt einen Fehler-Toast, wenn die Bedarfsmeldungs-Vorbelegung fehlschlaegt', async () => {
    getMock.mockRejectedValueOnce(new Error('Backend offline'))

    render(
      <MemoryRouter initialEntries={['/einkauf/bestellungen/neu?requisitionId=req-fehler']}>
        <BestellungAnlegenPage />
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Bedarfsmeldung konnte nicht geladen werden',
          description: 'Backend offline',
          variant: 'destructive',
        }),
      )
    })
  })

  it('blockiert den Wechsel zum Positionsschritt ohne Lieferant', async () => {
    render(
      <MemoryRouter initialEntries={['/einkauf/bestellungen/neu']}>
        <BestellungAnlegenPage />
      </MemoryRouter>,
    )

    await goToStep('Lieferant')
    fireEvent.click(screen.getByRole('button', { name: 'Weiter' }))

    await waitFor(() => {
      expect(toastMock).toHaveBeenCalledWith(
        expect.objectContaining({
          title: 'Validierung fehlgeschlagen',
          description: 'Lieferant ist ein Pflichtfeld.',
          variant: 'destructive',
        }),
      )
    })
    expect(screen.getByText('Aktiver Schritt: Lieferant')).toBeInTheDocument()
  })
})
