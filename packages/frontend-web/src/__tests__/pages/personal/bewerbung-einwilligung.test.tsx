import { act, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import type { ReactNode } from 'react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import type { RenderPlan } from '@/components/mask-builder/render-plan/types'
import type { UniversalFormState } from '@/components/mask-builder/runtime/useUniversalFormState'
import PersonalBewerbungEinwilligungPage from '@/pages/personal/bewerbung-einwilligung'
import PersonalEinwilligungserklaerungenPage from '@/pages/personal/einwilligungserklaerungen'
import PersonalBewerbungenPage from '@/pages/personal/bewerbungen'

const mocks = vi.hoisted(() => ({
  navigate: vi.fn(),
  params: { id: 'bew-1' } as { id?: string },
  toastSuccess: vi.fn(),
  toastError: vi.fn(),
  getBewerbungKopf: vi.fn(),
  getEinwilligung: vi.fn(),
  listErklaerungen: vi.fn(),
  erteileEinwilligung: vi.fn(),
  widerrufeEinwilligung: vi.fn(),
  legeErklaerungAn: vi.fn(),
  apiGet: vi.fn(),
  form: null as UniversalFormState | null,
  plan: null as RenderPlan | null,
  onAction: null as ((key: string, payload: Record<string, unknown>) => unknown) | null,
}))

vi.mock('@/app/routing/typed-router', () => ({
  useNavigate: () => mocks.navigate,
  useParams: () => mocks.params,
}))
vi.mock('sonner', () => ({ toast: { success: mocks.toastSuccess, error: mocks.toastError } }))
vi.mock('@/hooks/useTouchDevice', () => ({ useTouchDevice: () => false }))
vi.mock('@/lib/api-client', () => ({
  apiClient: { get: mocks.apiGet, post: vi.fn(), delete: vi.fn() },
  getAxiosErrorMessage: (error: unknown) => (error instanceof Error ? error.message : String(error)),
}))
vi.mock('@/lib/api/bewerbung-einwilligung', async (importOriginal) => ({
  ...(await importOriginal<typeof import('@/lib/api/bewerbung-einwilligung')>()),
  getBewerbungKopf: mocks.getBewerbungKopf,
  getEinwilligung: mocks.getEinwilligung,
  listErklaerungen: mocks.listErklaerungen,
  erteileEinwilligung: mocks.erteileEinwilligung,
  widerrufeEinwilligung: mocks.widerrufeEinwilligung,
  legeErklaerungAn: mocks.legeErklaerungAn,
}))
// Der Renderer zeichnet, was die Screen Definition hergibt: Aktionen und
// Eingabefelder aus dem kompilierten Plan. Fehlt ein Feld in der SD, fehlt es hier.
vi.mock('@/components/mask-builder/UniversalMaskRenderer', () => ({
  UniversalMaskRenderer: ({ plan, formState, onAction }: {
    plan: RenderPlan
    formState: UniversalFormState
    onAction: (key: string, payload: Record<string, unknown>) => void
  }) => {
    mocks.form = formState
    mocks.plan = plan
    mocks.onAction = onAction
    return (
      <div>
        {plan.actions.map((action) => (
          <button key={action.key} disabled={action.disabled} onClick={() => onAction(action.key, formState.values)}>
            {action.label}
          </button>
        ))}
        {Object.values(plan.fieldsByKey).filter((field) => !field.readOnly).map((field) => (
          <input
            key={field.key}
            aria-label={field.label}
            value={String(formState.values[field.key] ?? '')}
            onChange={(event) => formState.setValue(field.key, event.target.value)}
          />
        ))}
        <output data-testid="wortlaut">{String(formState.values.wortlaut ?? '')}</output>
      </div>
    )
  },
}))

const FASSUNGEN = [
  { id: 'e2', fassung: 2, wortlaut: 'Zweiter Wortlaut', erstellt_am: '2026-10-02T09:00:00Z' },
  { id: 'e1', fassung: 1, wortlaut: 'Erster Wortlaut', erstellt_am: '2026-09-01T09:00:00Z' },
]
const OHNE = { bewerbung_id: 'bew-1', gueltig_bis: null, erteilt_am: null, laeuft: false, vorgaenge: [] }
const LAUFEND = {
  bewerbung_id: 'bew-1', gueltig_bis: '2027-10-01', erteilt_am: '2026-10-07T08:00:00Z', laeuft: true,
  vorgaenge: [{ id: 'v1', vorgang: 'ERTEILT', erfolgt_am: '2026-10-07T08:00:00Z', gueltig_bis: '2027-10-01', kanal: 'PAPIER', fassung: 2 }],
}

function mitAbfragen(kind: ReactNode) {
  const client = new QueryClient({ defaultOptions: { queries: { retry: false } } })
  return <QueryClientProvider client={client}>{kind}</QueryClientProvider>
}

function eingeben(label: string, wert: string) {
  fireEvent.change(screen.getByLabelText(label), { target: { value: wert } })
}

beforeEach(() => {
  vi.clearAllMocks()
  mocks.params = { id: 'bew-1' }
  mocks.getBewerbungKopf.mockResolvedValue({ id: 'bew-1', applicant_name: 'Erika Muster', position_title: 'Disponentin' })
  mocks.getEinwilligung.mockResolvedValue(OHNE)
  mocks.listErklaerungen.mockResolvedValue(FASSUNGEN)
})

describe('Einwilligung zur Aufbewahrung', () => {
  it('bietet die Fassungen der API als Auswahl und zeigt deren Wortlaut', async () => {
    render(mitAbfragen(<PersonalBewerbungEinwilligungPage />))
    await waitFor(() => expect(mocks.plan?.fieldsByKey.fassung.options).toHaveLength(2))
    expect(mocks.plan?.fieldsByKey.fassung.options?.[0]).toEqual({ value: '2', label: 'Fassung 2 vom 02.10.2026' })
    // Keine Vorauswahl: Welche Fassung unterschrieben wurde, sagt der Mensch.
    expect(mocks.form?.values.fassung).toBe('')
    eingeben('Fassung der Erklärung', '1')
    await waitFor(() => expect(screen.getByTestId('wortlaut')).toHaveTextContent('Erster Wortlaut'))
    expect(mocks.plan?.fieldsByKey.wortlaut.readOnly).toBe(true)
  })

  it('erteilt gegen die gewaehlte Fassung und schuetzt vor dem Doppelklick', async () => {
    let fertig: (value: unknown) => void = () => undefined
    mocks.erteileEinwilligung.mockReturnValue(new Promise((resolve) => { fertig = resolve }))
    render(mitAbfragen(<PersonalBewerbungEinwilligungPage />))
    await screen.findByLabelText('Fassung der Erklärung')
    eingeben('Fassung der Erklärung', '2')
    eingeben('Gültig bis', '2027-10-01')
    eingeben('Eingegangen über', 'PAPIER')
    const knopf = screen.getByRole('button', { name: 'Einwilligung erteilen' })
    await waitFor(() => expect(knopf).toBeEnabled())
    fireEvent.click(knopf)
    fireEvent.click(knopf)
    await waitFor(() => expect(knopf).toBeDisabled())
    expect(mocks.erteileEinwilligung).toHaveBeenCalledTimes(1)
    expect(mocks.erteileEinwilligung).toHaveBeenCalledWith('bew-1', {
      fassung: 2, gueltig_bis: '2027-10-01', kanal: 'PAPIER', erfasst_durch: null,
    })
    await act(async () => { fertig({ fassung: 2, gueltig_bis: '2027-10-01' }) })
    await waitFor(() => expect(mocks.toastSuccess).toHaveBeenCalledWith('Einwilligung erteilt', expect.anything()))
    await waitFor(() => expect(knopf).toBeEnabled())
    // Sichtpruefung 07.10.2026: Das Leeren nach dem Erfolg meldete "Pflichtfeld".
    expect(mocks.form?.values.fassung).toBe('')
    expect(mocks.form?.visibleFieldErrors).toEqual({})
  })

  it('erteilt nichts, solange Fassung, Ende oder Kanal fehlen', async () => {
    render(mitAbfragen(<PersonalBewerbungEinwilligungPage />))
    await screen.findByLabelText('Fassung der Erklärung')
    eingeben('Fassung der Erklärung', '2')
    const knopf = screen.getByRole('button', { name: 'Einwilligung erteilen' })
    await waitFor(() => expect(knopf).toBeEnabled())
    fireEvent.click(knopf)
    await waitFor(() => expect(mocks.toastError).toHaveBeenCalledWith('Einwilligung unvollständig', expect.anything()))
    expect(mocks.erteileEinwilligung).not.toHaveBeenCalled()
    // Jetzt zeigt die Maske, was fehlt.
    expect(Object.keys(mocks.form?.visibleFieldErrors ?? {}).sort()).toEqual(['gueltig_bis', 'kanal'])
  })

  it('zeigt den Grund, wenn das Erteilen scheitert', async () => {
    mocks.erteileEinwilligung.mockRejectedValue(new Error('Hoechstens 1095 Tage ab heute.'))
    render(mitAbfragen(<PersonalBewerbungEinwilligungPage />))
    await screen.findByLabelText('Fassung der Erklärung')
    eingeben('Fassung der Erklärung', '2')
    eingeben('Gültig bis', '2031-01-01')
    eingeben('Eingegangen über', 'WEB')
    const knopf = screen.getByRole('button', { name: 'Einwilligung erteilen' })
    await waitFor(() => expect(knopf).toBeEnabled())
    fireEvent.click(knopf)
    await waitFor(() => expect(mocks.toastError).toHaveBeenCalledWith(
      'Einwilligung nicht erteilt', { description: 'Hoechstens 1095 Tage ab heute.' },
    ))
    await waitFor(() => expect(knopf).toBeEnabled())
  })

  it('ohne Fassung laesst sich nicht erteilen', async () => {
    mocks.listErklaerungen.mockResolvedValue([])
    render(mitAbfragen(<PersonalBewerbungEinwilligungPage />))
    await screen.findByLabelText('Fassung der Erklärung')
    await waitFor(() => expect(screen.getByRole('button', { name: 'Einwilligung erteilen' })).toBeDisabled())
  })

  it('ohne Einwilligung gibt es nichts zu widerrufen', async () => {
    render(mitAbfragen(<PersonalBewerbungEinwilligungPage />))
    await screen.findByLabelText('Fassung der Erklärung')
    expect(screen.getByRole('button', { name: 'Einwilligung widerrufen' })).toBeDisabled()
  })

  it('widerruft nach Bestaetigung — ohne Rumpf, ohne Grund', async () => {
    mocks.getEinwilligung.mockResolvedValue(LAUFEND)
    mocks.widerrufeEinwilligung.mockResolvedValue({ id: 'v2', vorgang: 'WIDERRUFEN' })
    render(mitAbfragen(<PersonalBewerbungEinwilligungPage />))
    const knopf = await screen.findByRole('button', { name: 'Einwilligung widerrufen' })
    await waitFor(() => expect(knopf).toBeEnabled())
    fireEvent.click(knopf)
    // Die Bestaetigung fragt nichts ab — kein Feld, kein Grund.
    const dialog = await screen.findByRole('alertdialog')
    expect(dialog.querySelectorAll('input, textarea, select')).toHaveLength(0)
    expect(mocks.widerrufeEinwilligung).not.toHaveBeenCalled()
    fireEvent.click(screen.getByRole('button', { name: 'Widerrufen' }))
    await waitFor(() => expect(mocks.widerrufeEinwilligung).toHaveBeenCalledTimes(1))
    expect(mocks.widerrufeEinwilligung.mock.calls[0]).toEqual(['bew-1'])
    await waitFor(() => expect(mocks.toastSuccess).toHaveBeenCalledWith('Einwilligung widerrufen', expect.anything()))
  })

  it('der Abbruch der Bestaetigung widerruft nicht', async () => {
    mocks.getEinwilligung.mockResolvedValue(LAUFEND)
    render(mitAbfragen(<PersonalBewerbungEinwilligungPage />))
    const knopf = await screen.findByRole('button', { name: 'Einwilligung widerrufen' })
    await waitFor(() => expect(knopf).toBeEnabled())
    fireEvent.click(knopf)
    fireEvent.click(await screen.findByRole('button', { name: 'Abbrechen' }))
    await waitFor(() => expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument())
    expect(mocks.widerrufeEinwilligung).not.toHaveBeenCalled()
  })

  it('ohne gewaehlte Bewerbung sagt die Seite das', () => {
    mocks.params = {}
    render(mitAbfragen(<PersonalBewerbungEinwilligungPage />))
    expect(screen.getByRole('status')).toHaveTextContent('Keine Bewerbung gewählt')
    expect(mocks.getEinwilligung).not.toHaveBeenCalled()
  })
})

describe('Fassungen der Einwilligungserklaerung', () => {
  it('legt nach Bestaetigung an und meldet die vergebene Nummer', async () => {
    mocks.legeErklaerungAn.mockResolvedValue({ id: 'e3', fassung: 3, wortlaut: 'Neuer Text' })
    render(mitAbfragen(<PersonalEinwilligungserklaerungenPage />))
    await screen.findByLabelText('Wortlaut')
    eingeben('Wortlaut', '  Neuer Text  ')
    fireEvent.click(screen.getByRole('button', { name: 'Fassung anlegen' }))
    expect(mocks.legeErklaerungAn).not.toHaveBeenCalled()
    await screen.findByRole('alertdialog')
    fireEvent.click(screen.getByRole('button', { name: 'Anlegen' }))
    await waitFor(() => expect(mocks.legeErklaerungAn).toHaveBeenCalledWith('Neuer Text', null))
    await waitFor(() => expect(mocks.toastSuccess).toHaveBeenCalledWith('Fassung 3 angelegt', expect.anything()))
  })

  it('derselbe Wortlaut nennt die vorhandene Fassung', async () => {
    mocks.legeErklaerungAn.mockRejectedValue({ response: { status: 409, data: { detail: { fassung: 2 } } } })
    render(mitAbfragen(<PersonalEinwilligungserklaerungenPage />))
    await screen.findByLabelText('Wortlaut')
    eingeben('Wortlaut', 'Zweiter Wortlaut')
    fireEvent.click(screen.getByRole('button', { name: 'Fassung anlegen' }))
    fireEvent.click(await screen.findByRole('button', { name: 'Anlegen' }))
    await waitFor(() => expect(mocks.toastError).toHaveBeenCalledWith(
      'Diesen Wortlaut gibt es schon', { description: 'Er ist Fassung 2.' },
    ))
  })

  it('ohne Wortlaut wird nicht gefragt und nicht angelegt', async () => {
    render(mitAbfragen(<PersonalEinwilligungserklaerungenPage />))
    await screen.findByLabelText('Wortlaut')
    fireEvent.click(screen.getByRole('button', { name: 'Fassung anlegen' }))
    await waitFor(() => expect(mocks.toastError).toHaveBeenCalledWith('Fassung unvollständig', expect.anything()))
    expect(screen.queryByRole('alertdialog')).not.toBeInTheDocument()
    expect(mocks.legeErklaerungAn).not.toHaveBeenCalled()
  })

  it('bietet weder Bearbeiten noch Loeschen einer Fassung', async () => {
    render(mitAbfragen(<PersonalEinwilligungserklaerungenPage />))
    await screen.findByLabelText('Wortlaut')
    expect(mocks.plan?.actions.map((action) => action.key).sort()).toEqual(['anlegen', 'neu'])
    expect(mocks.plan?.tablesByKey.fassungen.rowActions ?? []).toEqual([])
  })
})

describe('Bewerbungen-Arbeitsliste', () => {
  it('fuehrt von der Zeile zur Einwilligung und zu den Fassungen', async () => {
    mocks.apiGet.mockResolvedValue({ data: [] })
    render(mitAbfragen(<PersonalBewerbungenPage />))
    const zuDenFassungen = await screen.findByRole('button', { name: 'Einwilligungserklärungen' })
    fireEvent.click(zuDenFassungen)
    expect(mocks.navigate).toHaveBeenCalledWith('/personal/einwilligungserklaerungen')
    const zeile = mocks.plan?.tablesByKey.bewerbungen.rowActions?.find((action) => action.key === 'einwilligung')
    expect(zeile?.label).toBe('Einwilligung')
    await act(async () => { await mocks.onAction?.('einwilligung', { id: 'bew 9' }) })
    expect(mocks.navigate).toHaveBeenCalledWith('/personal/bewerbung/bew%209/einwilligung')
  })
})
