import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { FeedingActualPage } from '@/features/feed-advice/FeedingActualPage'

const mocks = vi.hoisted(() => ({ exportCsv: vi.fn(), findings: vi.fn(), measures: vi.fn(), create: vi.fn(), policies: vi.fn(), createPolicy: vi.fn(), click: vi.fn() }))

vi.mock('@/lib/api/feeding-actual', () => ({
  exportActualFeedingsCsv: mocks.exportCsv,
  fetchDeviationFindings: mocks.findings,
  fetchActualMeasures: mocks.measures,
  createActualMeasure: mocks.create,
  fetchDeviationPolicies: mocks.policies,
  createDeviationPolicy: mocks.createPolicy,
}))
vi.mock('@/components/mask-builder/UniversalNativeCockpitPage', () => ({
  UniversalNativeCockpitPage: ({ screenId, onAction }: {
    screenId: string
    onAction: (key: string) => void
  }) => <div data-testid="native-actuals">{screenId}
    <button onClick={() => onAction('export_csv')}>CSV exportieren</button>
    <button onClick={() => onAction('create_measure')}>Massnahme aus Abweichung</button>
    <button onClick={() => onAction('configure_threshold')}>Schwellen konfigurieren</button>
  </div>,
}))

describe('FeedingActualPage', () => {
  beforeEach(() => {
    mocks.exportCsv.mockReset()
    mocks.findings.mockReset()
    mocks.measures.mockReset()
    mocks.create.mockReset()
    mocks.policies.mockReset()
    mocks.createPolicy.mockReset()
    mocks.click.mockReset()
    Object.defineProperty(URL, 'createObjectURL', { configurable: true, value: vi.fn(() => 'blob:actuals') })
    Object.defineProperty(URL, 'revokeObjectURL', { configurable: true, value: vi.fn() })
    vi.spyOn(HTMLAnchorElement.prototype, 'click').mockImplementation(mocks.click)
  })

  it('renders through the native Meridian screen and exports the grant-filtered CSV', async () => {
    mocks.exportCsv.mockResolvedValue(new Blob(['actual_record_id']))
    render(<FeedingActualPage />)
    expect(screen.getByTestId('native-actuals')).toHaveTextContent('agrar/feeding-actuals')
    fireEvent.click(screen.getByRole('button', { name: 'CSV exportieren' }))
    await waitFor(() => expect(mocks.exportCsv).toHaveBeenCalledOnce())
    expect(mocks.click).toHaveBeenCalledOnce()
    expect(screen.getByRole('status')).toHaveTextContent('berechtigten Ist-Fuetterungen')
  })

  it('creates a measure only after explicit owner due-date and reason confirmation', async () => {
    mocks.findings.mockResolvedValue([{
      actual_component_id: 'component-1', actual_record_id: 'record-1', plan_version_id: 'plan-2',
      group_id: 'group-1', feed_id: 'mais', feed_name: 'Maissilage', severity: 'critical',
      delta_pct: 15, feed_class: 'forage', policy_version: 2, message: '15 % Abweichung',
    }])
    mocks.measures.mockResolvedValue([])
    mocks.create.mockResolvedValue({ id: 'measure-1', status: 'open' })
    render(<FeedingActualPage />)
    fireEvent.click(screen.getByRole('button', { name: 'Massnahme aus Abweichung' }))
    expect(await screen.findByRole('dialog')).toHaveTextContent('Maissilage')
    fireEvent.change(screen.getByLabelText('Massnahme'), { target: { value: 'Mischwagenwaage pruefen' } })
    fireEvent.change(screen.getByLabelText('Verantwortlich'), { target: { value: 'stall-team' } })
    fireEvent.change(screen.getByLabelText('Begruendung'), { target: { value: 'Kritische Abweichung nachverfolgen' } })
    fireEvent.click(screen.getByRole('button', { name: 'Massnahme anlegen' }))
    await waitFor(() => expect(mocks.create).toHaveBeenCalledWith(expect.objectContaining({
      actual_component_id: 'component-1', owner_subject: 'stall-team',
    })))
    expect(await screen.findByRole('status')).toHaveTextContent('revisionssicher angelegt')
  })

  it('creates an explicit versioned class threshold instead of a hidden universal default', async () => {
    mocks.policies.mockResolvedValue([])
    mocks.createPolicy.mockResolvedValue({ feed_class: 'forage', version: 1 })
    render(<FeedingActualPage />)
    fireEvent.click(screen.getByRole('button', { name: 'Schwellen konfigurieren' }))
    expect(await screen.findByRole('dialog')).toHaveTextContent('keinen stillen Universalwert')
    fireEvent.change(screen.getByLabelText('Aenderungsgrund'), { target: { value: 'Betriebliche Grundfuttertoleranz' } })
    fireEvent.click(screen.getByRole('button', { name: 'Neue Regelversion anlegen' }))
    await waitFor(() => expect(mocks.createPolicy).toHaveBeenCalledWith(expect.objectContaining({
      feed_class: 'forage', warning_pct: 5, critical_pct: 10,
    })))
    expect(await screen.findByRole('status')).toHaveTextContent('Regelversion 1')
  })
})
