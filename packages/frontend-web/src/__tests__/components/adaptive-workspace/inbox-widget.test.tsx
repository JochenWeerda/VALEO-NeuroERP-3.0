import { render, screen, waitFor } from '@testing-library/react'
import { AxiosError } from 'axios'
import userEvent from '@testing-library/user-event'
import { describe, expect, it, vi, beforeEach } from 'vitest'
import * as domMatchers from '@testing-library/jest-dom/matchers'

expect.extend(domMatchers)
import {
  InboxPrefillBanner,
  InboxWidget,
  INBOX_PREFILL_SCHEMA,
  INBOX_PREFILL_STORAGE_KEY,
} from '@/components/adaptive-workspace/inbox'
import type { InboxPrefillPayload, InboxQueueItem } from '@/components/adaptive-workspace/inbox'

const postMock = vi.hoisted(() => vi.fn())
const getMock = vi.hoisted(() => vi.fn())

vi.mock('@/lib/api-client', () => ({
  apiClient: { get: getMock, post: postMock },
  getAxiosErrorMessage: (error: unknown) =>
    error instanceof Error ? error.message : 'Unbekannter Fehler.',
}))

function samplePrefill(overrides: Partial<InboxPrefillPayload> = {}): InboxPrefillPayload {
  return {
    schema: INBOX_PREFILL_SCHEMA,
    documentId: 'INBOX-9',
    documentNumber: 'RE-9',
    partner: { id: 'L-22', number: 'L-22', name: 'Nordkorn AG', role: 'supplier' },
    amounts: { total: '99.00', tax: '15.81', currency: 'EUR' },
    source: { kind: 'dms_inbox', id: 'INBOX-9', dmsDocumentId: 9, classification: 'default-incoming-invoice' },
    confidence: 0.4,
    confidenceBand: 'low',
    policyId: 'incoming-supplier-invoice',
    documentType: 'supplier_invoice',
    targetRoute: '/einkauf/rechnung-eingang-erfassung',
    booking: false,
    matchValues: { invoiceNumber: 'RE-9', supplierName: 'Nordkorn AG', supplierId: 'L-22' },
    match: {
      kind: 'business_partner',
      status: 'matched',
      matched_by: 'partner_number',
      partner_id: 'bp-22',
      partner_number: 'L-22',
      name: 'Nordkorn AG',
    },
    duplicates: [{ doc_type: 'purchase_order', doc_number: 'RE-9' }],
    uncertainties: [{ code: 'dublette', detail: 'Belegnummer existiert bereits im Dokumentspeicher des Mandanten.' }],
    storageKey: INBOX_PREFILL_STORAGE_KEY,
    maskConsumesPrefill: true,
    ...overrides,
  }
}

function item(overrides: Partial<InboxQueueItem> = {}): InboxQueueItem {
  return {
    id: 'INBOX-9',
    status: 'pending',
    parsed_fields: { invoice_number: 'RE-9' },
    match_values: { supplierName: 'Nordkorn AG', invoiceNumber: 'RE-9' },
    confidence: 0.4,
    confidence_band: 'low',
    source: 'default-incoming-invoice',
    proposal: {
      policy_id: 'incoming-supplier-invoice',
      label: 'Rechnungseingang erfassen',
      document_type: 'supplier_invoice',
      direction: 'incoming',
      target_route: '/einkauf/rechnung-eingang-erfassung',
      reason: 'test',
    },
    match: {
      kind: 'business_partner',
      status: 'matched',
      matched_by: 'partner_number',
      partner_id: 'bp-22',
      partner_number: 'L-22',
      name: 'Nordkorn AG',
    },
    duplicates: [{ doc_type: 'purchase_order', doc_number: 'RE-9' }],
    uncertainties: [{ code: 'dublette', detail: 'Belegnummer existiert bereits im Dokumentspeicher des Mandanten.' }],
    blockers: [{ code: 'konfidenz', detail: 'Konfidenz zu niedrig fuer eine automatische Vorbelegung.' }],
    actions: [
      {
        key: 'open_mask',
        label: 'Beleg öffnen',
        kind: 'primary',
        href: '/einkauf/rechnung-eingang-erfassung?inbox=INBOX-9',
        enabled: true,
        booking: false,
      },
    ],
    command: {
      command: 'document.capture.open',
      executable: false,
      booking: false,
      reason: 'keine Buchung',
      policy_id: 'incoming-supplier-invoice',
      document_type: 'supplier_invoice',
      target_route: '/einkauf/rechnung-eingang-erfassung',
      prefill: samplePrefill(),
      confidence: 0.4,
      confidence_band: 'low',
      blockers: [],
      match: samplePrefill().match,
      duplicates: samplePrefill().duplicates,
      uncertainties: samplePrefill().uncertainties,
      can_open: true,
      source: { kind: 'dms_inbox', id: 'INBOX-9' },
      gaps: [
        'create_from_inbox_bucht_nicht',
        'kontrakt_abgleich_nur_bei_kontraktnummer_im_extrakt',
        'linked_document_id_nur_bei_eindeutigem_documents_treffer',
      ],
    },
    can_open: true,
    booking_allowed: false,
    ...overrides,
  }
}

describe('InboxWidget', () => {
  beforeEach(() => {
    getMock.mockReset()
    postMock.mockReset()
    sessionStorage.clear()
  })

  it('opens the existing beleg mask and does not call the fake DMS create', async () => {
    const onOpenMask = vi.fn()
    const user = userEvent.setup()
    render(
      <InboxWidget
        queue={[
          item({
            proposal: {
              ...item().proposal,
              document_kind: 'EINGANGSRECHNUNG',
            },
          }),
        ]}
        onOpenMask={onOpenMask}
      />,
    )

    expect(screen.getByTestId('adaptive-workspace-inbox')).toBeInTheDocument()
    expect(screen.getByTestId('inbox-row-INBOX-9')).toHaveTextContent('Rechnungseingang erfassen')
    expect(screen.getByText(/Nordkorn AG/)).toBeInTheDocument()
    expect(getMock).not.toHaveBeenCalled()

    expect(screen.getByRole('link', { name: 'Zur Belegmaske INBOX-9' })).toHaveAttribute(
      'href',
      '/belege/purchase_invoice/neu?inbox=INBOX-9',
    )
    await user.click(screen.getByRole('button', { name: 'Beleg öffnen' }))
    expect(onOpenMask).toHaveBeenCalledTimes(1)
    expect(onOpenMask.mock.calls[0]?.[0].proposal.target_route).toBe('/einkauf/rechnung-eingang-erfassung')
    expect(sessionStorage.getItem(INBOX_PREFILL_STORAGE_KEY)).toBeNull()
    expect(postMock).not.toHaveBeenCalledWith(
      expect.stringContaining('/api/v1/dms/inbox/'),
      expect.anything(),
    )
  })

  it('prepares a validated command without booking', async () => {
    const onPrepare = vi.fn()
    postMock.mockResolvedValue({
      data: {
        command: item().command,
      },
    })
    const user = userEvent.setup()
    render(<InboxWidget queue={[item()]} onPrepare={onPrepare} />)

    await user.click(screen.getByRole('button', { name: 'Vorschlag' }))
    expect(postMock).toHaveBeenCalledWith('/api/mcp/documents/inbox/INBOX-9/prepare', {})
    expect(onPrepare).toHaveBeenCalledTimes(1)
    expect(onPrepare.mock.calls[0]?.[1].booking).toBe(false)
    expect(onPrepare.mock.calls[0]?.[1].executable).toBe(false)
  })

  it('zeigt Kontrakt-Match und verifizierte Beleg-ID ohne Buchung', () => {
    render(
      <InboxWidget
        queue={[
          item({
            linked_document_id: 'erp-doc-77',
            contract_match: {
              kind: 'contract',
              status: 'matched',
              matched_by: 'contract_number',
              source: 'kon_contract',
              contract_id: 'kon-13842',
              contract_number: '13842',
            },
            match_values: {
              ...item().match_values,
              contractId: '13842',
            },
          }),
        ]}
      />,
    )
    expect(screen.getByTestId('inbox-contract-INBOX-9')).toHaveTextContent('Kontrakt 13842')
    expect(screen.getByTestId('inbox-contract-INBOX-9')).toHaveTextContent('kon_contract')
    expect(screen.getByTestId('inbox-hints-INBOX-9')).toHaveTextContent('Beleg-ID erp-doc-77')
    expect(screen.getByTestId('inbox-hints-INBOX-9')).toHaveTextContent('Kontrakt 13842')
  })

  it('loest approve nicht aus auch wenn die Queue Freigeben mit /approve liefert (409 booking_not_from_inbox)', async () => {
    const approveHref = '/api/mcp/documents/inbox/INBOX-9/approve'
    const onPrepare = vi.fn()
    postMock.mockResolvedValue({ data: { command: item().command } })
    const user = userEvent.setup()
    render(
      <InboxWidget
        queue={[
          item({
            actions: [
              ...item().actions,
              {
                key: 'approve',
                label: 'Freigeben',
                kind: 'secondary',
                href: approveHref,
                enabled: true,
                booking: false,
              },
            ],
            command: {
              ...item().command,
              blockers: [{ code: 'booking_not_from_inbox', detail: 'Approve bleibt 409.' }],
            },
          }),
        ]}
        onPrepare={onPrepare}
      />,
    )

    expect(screen.queryByRole('button', { name: 'Freigeben' })).not.toBeInTheDocument()
    expect(screen.queryByRole('link', { name: /Freigeben|approve/i })).not.toBeInTheDocument()
    await user.click(screen.getByRole('button', { name: 'Vorschlag' }))
    expect(postMock).toHaveBeenCalledTimes(1)
    expect(postMock).toHaveBeenCalledWith('/api/mcp/documents/inbox/INBOX-9/prepare', {})
    expect(postMock).not.toHaveBeenCalledWith(approveHref, expect.anything())
    expect(postMock.mock.calls.every((call) => !String(call[0]).includes('/approve'))).toBe(true)
    expect(onPrepare.mock.calls[0]?.[1].booking).toBe(false)
  })

  it('hides low-confidence rows when the launcher asks for a threshold', () => {
    render(<InboxWidget queue={[item()]} confidenceMin={0.8} />)
    expect(screen.getByText('Kein Eingang in der Queue.')).toBeInTheDocument()
  })

  it('shows match and duplicate uncertainties without booking', () => {
    render(<InboxWidget queue={[item()]} />)
    expect(screen.getByTestId('inbox-partner-INBOX-9')).toHaveTextContent('Nordkorn AG')
    expect(screen.getByTestId('inbox-partner-INBOX-9')).toHaveTextContent(/Stamm partner_number/)
    expect(screen.getByTestId('inbox-hints-INBOX-9')).toHaveTextContent('Dublette RE-9')
  })

  it('renders match, duplicates and uncertainties on the prefill banner', () => {
    render(<InboxPrefillBanner payload={samplePrefill()} />)
    expect(screen.getByTestId('inbox-prefill-match')).toHaveTextContent('L-22')
    expect(screen.getByTestId('inbox-prefill-match')).toHaveTextContent(/partner_number/)
    expect(screen.getByTestId('inbox-prefill-duplicates')).toHaveTextContent('RE-9')
    expect(screen.getByTestId('inbox-prefill-uncertainties')).toHaveTextContent(/Dokumentspeicher/)
  })

  it('zeigt blend_confidence als Konfidenz und classification_source als Quelle', () => {
    render(
      <InboxWidget
        queue={[
          item({
            confidence: 0.72,
            confidence_band: 'medium',
            source: 'parsed-or-ocr-hint',
          }),
        ]}
      />,
    )
    expect(screen.getByTestId('inbox-confidence-INBOX-9')).toHaveTextContent(/72\s*%/)
    expect(screen.getByTestId('inbox-confidence-INBOX-9')).toHaveTextContent(/mittel/)
    expect(screen.getByTestId('inbox-source-INBOX-9')).toHaveTextContent('parsed-or-ocr-hint')
    expect(screen.getByTestId('inbox-partner-INBOX-9')).not.toHaveTextContent(/%/)
  })

  it('zeigt classification_source und blend_confidence im Prefill-Banner', () => {
    render(
      <InboxPrefillBanner
        payload={samplePrefill({
          confidence: 0.55,
          confidenceBand: 'low',
          source: {
            kind: 'dms_inbox',
            id: 'INBOX-9',
            dmsDocumentId: 9,
            classification: 'parsed-or-ocr-hint',
          },
        })}
      />,
    )
    expect(screen.getByTestId('inbox-prefill-confidence')).toHaveTextContent(/55\s*%/)
    expect(screen.getByTestId('inbox-prefill-confidence')).toHaveTextContent(/niedrig/)
    expect(screen.getByTestId('inbox-prefill-classification')).toHaveTextContent('parsed-or-ocr-hint')
    expect(screen.queryByTestId('inbox-prefill-match')).toBeInTheDocument()
    expect(screen.getByTestId('inbox-prefill-match')).not.toHaveTextContent(/%/)
  })

  it('laesst Prefill-Klassifikation weg wenn classification_source fehlt', () => {
    render(
      <InboxPrefillBanner
        payload={samplePrefill({
          source: { kind: 'dms_inbox', id: 'INBOX-9', dmsDocumentId: 9 },
        })}
      />,
    )
    expect(screen.queryByTestId('inbox-prefill-classification')).not.toBeInTheDocument()
    expect(screen.getByTestId('inbox-prefill-confidence')).toBeInTheDocument()
  })

  it('does not show document_kind when the backend omitted the field', () => {
    render(<InboxWidget queue={[item()]} />)
    expect(screen.queryByTestId('inbox-kind-INBOX-9')).not.toBeInTheDocument()
    expect(screen.getByRole('button', { name: 'Beleg öffnen' })).toBeDisabled()
    expect(screen.getByTestId('inbox-open-reason-INBOX-9')).toHaveTextContent(/nicht erkannt/)
    expect(screen.queryByRole('link', { name: 'Zur Belegmaske INBOX-9' })).not.toBeInTheDocument()
  })

  it('shows Zur Übersicht for Lieferschein list without Prefill', async () => {
    const user = userEvent.setup()
    const onOpenMask = vi.fn()
    sessionStorage.setItem(INBOX_PREFILL_STORAGE_KEY, '{"schema":"stale"}')
    render(
      <InboxWidget
        queue={[
          item({
            proposal: {
              ...item().proposal,
              document_kind: 'LIEFERSCHEIN',
              target_route: '/einkauf/rechnung-eingang-erfassung',
            },
          }),
        ]}
        onOpenMask={onOpenMask}
      />,
    )
    expect(screen.getByTestId('inbox-primary-open-INBOX-9')).toHaveTextContent('Zur Übersicht')
    expect(screen.getByRole('link', { name: 'Zur Übersicht INBOX-9' })).toHaveAttribute(
      'href',
      '/einkauf/lieferschein-erfassung?inbox=INBOX-9',
    )
    expect(screen.getByTestId('inbox-document-open-INBOX-9')).toBeDisabled()
    await user.click(screen.getByTestId('inbox-primary-open-INBOX-9'))
    expect(onOpenMask).toHaveBeenCalledTimes(1)
    expect(sessionStorage.getItem(INBOX_PREFILL_STORAGE_KEY)).toBeNull()
  })

  it('shows Zur Übersicht for credit/scale lists and disables Beleg öffnen without ID', async () => {
    const user = userEvent.setup()
    const onOpenMask = vi.fn()
    render(
      <InboxWidget
        queue={[
          item({
            id: 'INBOX-credit',
            proposal: {
              ...item().proposal,
              document_kind: 'GUTSCHRIFT',
              direction: 'outgoing',
            },
          }),
          item({
            id: 'INBOX-scale',
            proposal: { ...item().proposal, document_kind: 'WIEGESCHEIN' },
          }),
          item({
            id: 'INBOX-scale-id',
            linked_document_id: 'WS-OK-1',
            proposal: { ...item().proposal, document_kind: 'WIEGESCHEIN' },
          }),
          item({
            id: 'INBOX-credit-nodir',
            proposal: {
              ...item().proposal,
              document_kind: 'GUTSCHRIFT',
              direction: null,
            },
          }),
        ]}
        onOpenMask={onOpenMask}
      />,
    )
    expect(screen.getByTestId('inbox-primary-open-INBOX-credit')).toHaveTextContent('Zur Übersicht')
    expect(screen.getByTestId('inbox-primary-open-INBOX-scale')).toHaveTextContent('Zur Übersicht')
    expect(screen.getByRole('link', { name: 'Zur Übersicht INBOX-credit' })).toHaveAttribute(
      'href',
      '/sales/credit-notes?inbox=INBOX-credit',
    )
    expect(screen.getByRole('link', { name: 'Zur Übersicht INBOX-scale' })).toHaveAttribute(
      'href',
      '/weighing?inbox=INBOX-scale',
    )
    expect(screen.getByTestId('inbox-document-open-INBOX-credit')).toBeDisabled()
    expect(screen.getByTestId('inbox-document-open-INBOX-scale')).toBeDisabled()
    expect(screen.getByTestId('inbox-document-open-reason-INBOX-scale')).toHaveTextContent(/Beleg-ID/)
    expect(screen.getByTestId('inbox-document-open-INBOX-scale-id')).toBeEnabled()
    expect(screen.getByRole('link', { name: 'Zum Beleg INBOX-scale-id' })).toHaveAttribute(
      'href',
      '/waage/wiegeschein/WS-OK-1',
    )
    expect(screen.getByTestId('inbox-primary-open-INBOX-credit-nodir')).toBeDisabled()
    expect(screen.getByTestId('inbox-primary-open-INBOX-credit-nodir')).toHaveTextContent('Beleg öffnen')
    expect(screen.queryByTestId('inbox-document-open-INBOX-credit-nodir')).not.toBeInTheDocument()
    expect(screen.getByTestId('inbox-open-reason-INBOX-credit-nodir')).toHaveTextContent(/Richtung/)
    expect(screen.queryByRole('link', { name: 'Zur Übersicht INBOX-credit-nodir' })).not.toBeInTheDocument()
    await user.click(screen.getByTestId('inbox-primary-open-INBOX-credit'))
    expect(onOpenMask).toHaveBeenCalledTimes(1)
    expect(sessionStorage.getItem(INBOX_PREFILL_STORAGE_KEY)).toBeNull()
  })

  it('shows document_kind when the backend set the field', () => {
    render(
      <InboxWidget
        queue={[
          item({
            id: 'INBOX-kind',
            proposal: {
              policy_id: 'incoming-supplier-invoice',
              label: 'Rechnungseingang erfassen',
              document_type: 'supplier_invoice',
              document_kind: 'EINGANGSRECHNUNG',
              direction: 'incoming',
              target_route: '/einkauf/rechnung-eingang-erfassung',
              reason: 'test',
            },
          }),
        ]}
      />,
    )
    expect(screen.getByTestId('inbox-kind-INBOX-kind')).toHaveTextContent('Rechnung')
  })

  it('disables open when can_open is false', () => {
    render(
      <InboxWidget
        queue={[
          item({
            can_open: false,
            actions: [
              {
                key: 'open_mask',
                label: 'Beleg öffnen',
                kind: 'primary',
                href: null,
                enabled: false,
                booking: false,
              },
            ],
            uncertainties: [{ code: 'keine_berechtigung_maske', detail: 'Keine Berechtigung: Belegart purchase_invoice bearbeiten.' }],
          }),
        ]}
      />,
    )
    expect(screen.getByRole('button', { name: 'Beleg öffnen' })).toBeDisabled()
    expect(screen.queryByRole('link', { name: 'Zur Belegmaske INBOX-9' })).not.toBeInTheDocument()
    expect(screen.getByTestId('inbox-hints-INBOX-9')).toHaveTextContent(/Berechtigung/)
  })

  it('legt Lieferant nach Bestaetigung ueber POST /api/v1/einkauf/lieferanten an (nicht Approve)', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    postMock.mockResolvedValue({ data: { id: 'lf-42', lieferantennummer: 'L-NEU-9', firmenname: 'Neue Muehle GmbH' } })
    const user = userEvent.setup()
    render(
      <InboxWidget
        queue={[
          item({
            id: 'INBOX-LS',
            match: undefined,
            match_values: { supplierName: 'Neue Muehle GmbH', supplierNumber: 'L-NEU-9' },
            uncertainties: [
              { code: 'partner_nicht_gefunden', detail: 'Kein Lieferant-Match.' },
            ],
            master_data_proposals: {
              booking: false,
              executable: false,
              line_item_count: 0,
              supplier: {
                kind: 'supplier_create',
                status: 'propose',
                booking: false,
                executable: false,
                domain_api: 'POST /api/v1/einkauf/lieferanten',
                target_route: '/einkauf/lieferanten',
                reason: 'test',
                payload: {
                  firmenname: 'Neue Muehle GmbH',
                  lieferantennummer: 'L-NEU-9',
                  strasse: 'Hofweg 1',
                  plz: '26789',
                  ort: 'Leer',
                  land: 'Deutschland',
                },
              },
              articles: [
                {
                  kind: 'article_create',
                  status: 'blocked',
                  booking: false,
                  executable: false,
                  code: 'keine_positionszeilen_im_extrakt',
                  detail: 'keine Positionen',
                },
              ],
            },
          }),
        ]}
      />,
    )

    expect(screen.getByTestId('inbox-hints-INBOX-LS')).toHaveTextContent(/Lieferant-Vorschlag: Neue Muehle GmbH/)
    const createBtn = screen.getByTestId('inbox-supplier-create-INBOX-LS')
    expect(createBtn).toHaveTextContent('Lieferant anlegen')
    await user.click(createBtn)
    expect(confirmSpy).toHaveBeenCalled()
    expect(postMock).toHaveBeenCalledWith('/api/v1/einkauf/lieferanten', {
      firmenname: 'Neue Muehle GmbH',
      lieferantennummer: 'L-NEU-9',
      land: 'Deutschland',
      strasse: 'Hofweg 1',
      plz: '26789',
      ort: 'Leer',
    })
    expect(postMock.mock.calls.every((call) => !String(call[0]).includes('/approve'))).toBe(true)
    confirmSpy.mockRestore()
  })

  it('legt Lieferant nicht an wenn Bestaetigung abgelehnt wird', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(false)
    const user = userEvent.setup()
    render(
      <InboxWidget
        queue={[
          item({
            id: 'INBOX-LS-CANCEL',
            master_data_proposals: {
              booking: false,
              executable: false,
              line_item_count: 0,
              supplier: {
                kind: 'supplier_create',
                status: 'propose',
                booking: false,
                executable: false,
                domain_api: 'POST /api/v1/einkauf/lieferanten',
                target_route: '/einkauf/lieferanten',
                reason: 'test',
                payload: { firmenname: 'X', lieferantennummer: 'L-1' },
              },
              articles: [],
            },
          }),
        ]}
      />,
    )
    await user.click(screen.getByTestId('inbox-supplier-create-INBOX-LS-CANCEL'))
    expect(postMock).not.toHaveBeenCalled()
    confirmSpy.mockRestore()
  })

  it('DEMO-GAP: Confirm schreibt POST Lieferant; 409 bleibt Erfolg ohne Approve', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    postMock.mockRejectedValue({
      response: { status: 409, data: { detail: 'bereits vorhanden' } },
    })
    const user = userEvent.setup()
    render(
      <InboxWidget
        queue={[
          item({
            id: 'INBOX-DEMO-LF-GAP',
            match: undefined,
            match_values: {
              supplierName: 'Nordkorn Handelsgesellschaft Demo OHG',
              supplierId: 'DEMO-LF-GAP',
            },
            uncertainties: [
              { code: 'partner_nicht_gefunden', detail: 'Kein Lieferant-Match.' },
            ],
            master_data_proposals: {
              booking: false,
              executable: false,
              line_item_count: 1,
              supplier: {
                kind: 'supplier_create',
                status: 'propose',
                booking: false,
                executable: false,
                domain_api: 'POST /api/v1/einkauf/lieferanten',
                target_route: '/einkauf/lieferanten',
                reason: 'test',
                payload: {
                  firmenname: 'Nordkorn Handelsgesellschaft Demo OHG',
                  lieferantennummer: 'DEMO-LF-GAP',
                  land: 'Deutschland',
                },
              },
              articles: [
                {
                  kind: 'article_match',
                  status: 'matched',
                  booking: false,
                  executable: false,
                  line_index: 0,
                  match: {
                    kind: 'article',
                    status: 'matched',
                    matched_by: 'article_number',
                    article_number: 'DEMO-NWF-WHEAT',
                    name: 'Demo-Schrot Weizen',
                  },
                },
              ],
            },
          }),
        ]}
      />,
    )
    await user.click(screen.getByTestId('inbox-supplier-create-INBOX-DEMO-LF-GAP'))
    expect(confirmSpy).toHaveBeenCalled()
    expect(postMock).toHaveBeenCalledWith('/api/v1/einkauf/lieferanten', {
      firmenname: 'Nordkorn Handelsgesellschaft Demo OHG',
      lieferantennummer: 'DEMO-LF-GAP',
      land: 'Deutschland',
    })
    expect(postMock.mock.calls.every((call) => !String(call[0]).includes('/approve'))).toBe(true)
    confirmSpy.mockRestore()
  })

  it('DEMO-NWF: Beleg oeffnen navigiert per Inbox-ID ohne gespeicherte Geschaeftsdaten', async () => {
    const onOpenMask = vi.fn()
    const user = userEvent.setup()
    const demoPrefill = samplePrefill({
      documentId: 'INBOX-DEMO-LF-NWF',
      documentNumber: 'DEMO-NWF-RE-001',
      partner: {
        id: 'DEMO-LF-NWF',
        number: 'DEMO-LF-NWF',
        name: 'Nordwestdeutsche Futtermittel GmbH & Co. KG',
        role: 'supplier',
      },
      matchValues: {
        invoiceNumber: 'DEMO-NWF-RE-001',
        supplierName: 'Nordwestdeutsche Futtermittel GmbH & Co. KG',
        supplierId: 'DEMO-LF-NWF',
      },
      source: { kind: 'dms_inbox', id: 'INBOX-DEMO-LF-NWF', dmsDocumentId: 92001 },
    })
    render(
      <InboxWidget
        queue={[
          item({
            id: 'INBOX-DEMO-LF-NWF',
            proposal: {
              ...item().proposal,
              document_kind: 'EINGANGSRECHNUNG',
              target_route: '/einkauf/rechnung-eingang-erfassung',
            },
            actions: [
              {
                key: 'open_mask',
                label: 'Beleg öffnen',
                kind: 'primary',
                href: '/einkauf/rechnung-eingang-erfassung?inbox=INBOX-DEMO-LF-NWF',
                enabled: true,
                booking: false,
              },
            ],
            command: {
              ...item().command,
              prefill: demoPrefill,
              source: { kind: 'dms_inbox', id: 'INBOX-DEMO-LF-NWF' },
            },
          }),
        ]}
        onOpenMask={onOpenMask}
      />,
    )
    expect(screen.getByTestId('inbox-primary-open-INBOX-DEMO-LF-NWF')).toHaveTextContent('Beleg öffnen')
    expect(screen.getByRole('link', { name: 'Zur Belegmaske INBOX-DEMO-LF-NWF' })).toHaveAttribute(
      'href',
      '/belege/purchase_invoice/neu?inbox=INBOX-DEMO-LF-NWF',
    )
    await user.click(screen.getByRole('button', { name: 'Beleg öffnen' }))
    expect(onOpenMask).toHaveBeenCalledTimes(1)
    expect(sessionStorage.getItem(INBOX_PREFILL_STORAGE_KEY)).toBeNull()
    expect(postMock).not.toHaveBeenCalled()
  })

  it('legt Artikel an und ruft danach fetch-image (article_id Pflicht)', async () => {
    const confirmSpy = vi.spyOn(window, 'confirm').mockReturnValue(true)
    postMock
      .mockResolvedValueOnce({ data: { id: 'art-42' } })
      .mockResolvedValueOnce({ data: { image_url: 'https://example.test/w.jpg' } })
    const user = userEvent.setup()
    render(
      <InboxWidget
        queue={[
          item({
            id: 'INBOX-ART',
            master_data_proposals: {
              booking: false,
              executable: false,
              line_item_count: 1,
              articles: [
                {
                  kind: 'article_create',
                  status: 'propose',
                  booking: false,
                  executable: false,
                  domain_api: 'POST /api/v1/articles/',
                  target_route: '/artikel/neu',
                  payload: {
                    name: 'Winterweizen A',
                    article_number: 'WW-1',
                    ean_code: '4006381333931',
                    unit_hint: 't',
                  },
                  image_research: {
                    status: 'propose',
                    executed: false,
                    booking: false,
                    service: 'app.services.article_image_enrichment.resolve_image_for_article',
                    api: 'POST /api/v1/articles/enrich-images',
                    reason: 'test',
                  },
                },
              ],
            },
          }),
        ]}
      />,
    )

    expect(screen.getByTestId('inbox-hints-INBOX-ART')).toHaveTextContent(/Artikel-Vorschlag: Winterweizen A/)
    await user.click(screen.getByTestId('inbox-article-create-INBOX-ART'))
    expect(confirmSpy).toHaveBeenCalled()
    await waitFor(() => {
      expect(postMock).toHaveBeenCalledWith('/api/v1/articles/', {
        article_number: 'WW-1',
        name: 'Winterweizen A',
        unit: 't',
        category: 'Sonstige',
        sales_price: 0,
        ean_code: '4006381333931',
        barcode: '4006381333931',
      })
    })
    await waitFor(() => {
      expect(postMock).toHaveBeenCalledWith('/api/v1/articles/art-42/fetch-image')
    })
    expect(postMock.mock.calls.every((call) => !String(call[0]).includes('/approve'))).toBe(true)
    confirmSpy.mockRestore()
  })

  it('meldet die geladene Queue und blendet 401 aus', async () => {
    const onQueue = vi.fn()
    const loaded = render(<InboxWidget queue={[item()]} onQueue={onQueue} />)
    await waitFor(() => {
      expect(onQueue.mock.calls.at(-1)?.[0]).toMatchObject({ status: 'ready' })
    })
    expect(onQueue.mock.calls.at(-1)?.[0].items.map((entry: { id: string }) => entry.id)).toEqual(['INBOX-9'])
    expect(getMock).not.toHaveBeenCalled()
    loaded.unmount()

    onQueue.mockClear()
    getMock.mockRejectedValue(
      new AxiosError('Unauthorized', 'ERR_BAD_REQUEST', undefined, undefined, {
        status: 401,
        statusText: 'Unauthorized',
        data: {},
        headers: {},
        config: { headers: {} as never },
      }),
    )
    render(<InboxWidget onQueue={onQueue} />)
    await waitFor(() => {
      expect(onQueue.mock.calls.some((call) => call[0]?.status === 'hidden')).toBe(true)
    })
    expect(onQueue.mock.calls.some((call) => call[0]?.status === 'ready')).toBe(false)
  })
})
