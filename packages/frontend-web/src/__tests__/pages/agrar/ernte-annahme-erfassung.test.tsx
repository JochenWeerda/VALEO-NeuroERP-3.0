import { render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, beforeEach, vi } from 'vitest'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
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
})
