import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, beforeEach, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from '@/app/routing/react-router-compat'
import ErnteAnnahmeErfassungPage from '@/pages/agrar/ernte-annahme-erfassung'

const pushMock = vi.hoisted(() => vi.fn())
const axiosGetMock = vi.hoisted(() => vi.fn())
const axiosPostMock = vi.hoisted(() => vi.fn())
const axiosPutMock = vi.hoisted(() => vi.fn())
const axiosDeleteMock = vi.hoisted(() => vi.fn())
const authUser = vi.hoisted(() => ({ name: 'Max Mustermann', sub: 'mmustermann' }))

vi.mock('@/components/ui/toast-provider', () => ({
  useToast: () => ({ push: pushMock }),
}))

vi.mock('@/hooks/useAuth', () => ({
  useAuth: () => ({
    user: authUser,
  }),
}))

vi.mock('@/features/ki-usability', () => ({
  useGlobalShortcutsWithVoice: () => undefined,
}))

vi.mock('@/components/navigation/ModuleToolbar', () => ({
  ModuleToolbar: ({ title }: { title: string }) => <div>{title}</div>,
}))

vi.mock('@/components/shortcuts/ShortcutHelpPanel', () => ({
  ShortcutHintButton: ({ children }: { children: JSX.Element }) => children,
}))

vi.mock('@/lib/axios', () => ({
  apiClient: {
    get: axiosGetMock,
    post: axiosPostMock,
    put: axiosPutMock,
    delete: axiosDeleteMock,
  },
}))

describe('ErnteAnnahmeErfassungPage', () => {
  beforeEach(() => {
    pushMock.mockReset()
    axiosGetMock.mockReset()
    axiosPostMock.mockReset()
    axiosPutMock.mockReset()
    axiosDeleteMock.mockReset()
    axiosGetMock.mockImplementation(async (url: string) => {
      if (url === '/api/v1/articles') {
        return {
          data: {
            items: [
              {
                id: 'art-raps',
                name: 'Raps',
                article_number: 'ART-RAPS',
                vat_rate: 7,
              },
              {
                id: 'art-weizen',
                name: 'Weizen',
                article_number: 'ART-WEIZEN',
                vat_rate: 7,
              },
            ],
          },
        }
      }
      return { data: [] }
    })
  })

  it('uebernimmt den Harvest-to-Settlement-Handover stabil in die Ernte-Annahme-Maske', async () => {
    render(
      <MemoryRouter
        initialEntries={[
          '/agrar/ernte-annahme-erfassung?workflowProcess=harvest-to-settlement&workflowInstanceId=wf-ern-1&workflowCase=ERN-2026-001&entryMode=Annahme&partnerName=Hof%20Meyer&subject=Weizen%20Herbst',
        ]}
      >
        <Routes>
          <Route path="/agrar/ernte-annahme-erfassung" element={<ErnteAnnahmeErfassungPage />} />
        </Routes>
      </MemoryRouter>,
    )

    expect(await screen.findByText('Workflow-Handover aus Harvest-to-Settlement')).toBeInTheDocument()
    await waitFor(() => {
      expect(screen.getByDisplayValue(/Workflow-Vorgang ERN-2026-001/)).toBeInTheDocument()
    })
    expect(screen.getByDisplayValue(/Einstieg: Annahme/)).toBeInTheDocument()
    expect(screen.getByDisplayValue(/Anlieferer: Hof Meyer/)).toBeInTheDocument()
    expect(screen.getByDisplayValue(/Weizen Herbst/)).toBeInTheDocument()
  })

  it('uebernimmt die Vorbelegung aus dem Qualitaets-Check restart-sicher ueber Query-Parameter', async () => {
    render(
      <MemoryRouter
        initialEntries={[
          '/agrar/ernte-annahme-erfassung?workflowProcess=harvest-to-settlement&workflowLabel=quality-protocol%3Aqp-1&entryMode=Qualitaetspruefung&partnerName=Hof%20Meyer&subject=Weizen%20%2F%20freigegeben&lieferscheinNr=LS-42&vehiclePlate=AB-CD%201234&articleId=art-weizen&articleName=Weizen&qpResult=freigegeben&qualityProtocolId=qp-1',
        ]}
      >
        <Routes>
          <Route path="/agrar/ernte-annahme-erfassung" element={<ErnteAnnahmeErfassungPage />} />
        </Routes>
      </MemoryRouter>,
    )

    await waitFor(() => {
      expect(screen.getByDisplayValue('AB-CD 1234')).toBeInTheDocument()
    })
    expect(screen.getByDisplayValue('Weizen')).toBeInTheDocument()
    expect(screen.getByDisplayValue(/Lieferschein: LS-42/)).toBeInTheDocument()
    expect(screen.getByDisplayValue(/Qualitaetspruefung: freigegeben/)).toBeInTheDocument()
    expect(screen.getByDisplayValue(/Qualitaetsprotokoll: qp-1/)).toBeInTheDocument()
    expect(screen.getByDisplayValue('art-weizen')).toBeInTheDocument()
  })

  it('zieht fuer Queue-Handover die kanonische article_id aus der Artikel-API nach', async () => {
    render(
      <MemoryRouter
        initialEntries={[
          '/agrar/ernte-annahme-erfassung?workflowProcess=harvest-to-settlement&workflowLabel=queue-entry%3Aqueue-2&entryMode=Warteschlange&partnerName=Hof%20Meyer&subject=Raps%20%2F%20Queue&articleId=art-raps&lieferscheinNr=LS-99&vehiclePlate=EF-GH%205678&articleName=Raps&queueEntryId=queue-2',
        ]}
      >
        <Routes>
          <Route path="/agrar/ernte-annahme-erfassung" element={<ErnteAnnahmeErfassungPage />} />
        </Routes>
      </MemoryRouter>,
    )

    expect(screen.getByDisplayValue('art-raps')).toBeInTheDocument()
    expect(screen.getByDisplayValue('Raps')).toBeInTheDocument()
    expect(screen.getByDisplayValue(/Warteschlange: queue-2/)).toBeInTheDocument()
  })
})
