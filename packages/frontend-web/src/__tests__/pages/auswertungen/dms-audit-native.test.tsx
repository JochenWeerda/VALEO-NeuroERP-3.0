import { render, screen } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import DmsVolltextPage from '@/pages/auswertungen/dms-volltext'
import AenderungshistoriePage from '@/pages/auswertungen/aenderungshistorie'
import DuengemittelmengenPage from '@/pages/auswertungen/duengemittelmengen'
import SanktionspruefungPersonalPage from '@/pages/auswertungen/sanktionspruefung-personal'
import SanktionspruefungKundenPage from '@/pages/auswertungen/sanktionspruefung-kunden'
import AuftragsKontrollePage from '@/pages/auswertungen/auftrags-kontrolle'
import LieferscheinKontrollePage from '@/pages/auswertungen/lieferschein-kontrolle'
import EbLieferscheinKontrollePage from '@/pages/abrechnung/eb-lieferschein-kontrolle'
import BonusBerechnungPage from '@/pages/auswertungen/bonus-berechnung'
import ChargenBearbeitenPage from '@/pages/produktion/chargen-bearbeiten'

vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ screenId, testId }: { screenId: string; testId: string }) => (
    <div data-testid={testId} data-screen-id={screenId} />
  ),
}))

describe('L3 deep native masks', () => {
  function renderWithQueryClient(node: JSX.Element): void {
    render(<QueryClientProvider client={new QueryClient()}>{node}</QueryClientProvider>)
  }
  it('binds DMS fulltext to the central runtime', () => {
    render(<DmsVolltextPage />)
    expect(screen.getByTestId('dms-volltext')).toHaveAttribute('data-screen-id', 'auswertungen/dms-volltext')
  })

  it('binds cross-domain history to the central runtime', () => {
    render(<AenderungshistoriePage />)
    expect(screen.getByTestId('aenderungshistorie')).toHaveAttribute('data-screen-id', 'auswertungen/aenderungshistorie')
  })

  it.each([
    { page: <DuengemittelmengenPage />, testId: 'duengemittelmengen', screenId: 'auswertungen/duengemittelmengen' },
    { page: <SanktionspruefungPersonalPage />, testId: 'personal-sanctions-check', screenId: 'auswertungen/sanktionspruefung-personal' },
    { page: <SanktionspruefungKundenPage />, testId: 'customers-sanctions-check', screenId: 'auswertungen/sanktionspruefung-kunden' },
    { page: <AuftragsKontrollePage />, testId: 'auswertungen-auftrags-kontrolle', screenId: 'auswertungen/auftrags-kontrolle' },
    { page: <LieferscheinKontrollePage />, testId: 'auswertungen-lieferschein-kontrolle', screenId: 'auswertungen/lieferschein-kontrolle' },
    { page: <EbLieferscheinKontrollePage />, testId: 'abrechnung-eb-lieferschein-kontrolle', screenId: 'abrechnung/eb-lieferschein-kontrolle' },
    { page: <BonusBerechnungPage />, testId: 'bonus-berechnung', screenId: 'auswertungen/bonus-berechnung' },
    { page: <ChargenBearbeitenPage />, testId: 'chargen-bearbeiten', screenId: 'produktion/chargen-bearbeiten' },
  ])('binds $screenId to the central runtime', ({ page, testId, screenId }) => {
    renderWithQueryClient(page)
    expect(screen.getByTestId(testId)).toHaveAttribute('data-screen-id', screenId)
  })
})
