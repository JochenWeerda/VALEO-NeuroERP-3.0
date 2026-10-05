import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FeedingAnalysisDetail } from '@/features/feed-advice/FeedingAnalysisDetail'
import { FeedingAnalysisWorklist } from '@/features/feed-advice/FeedingAnalysisWorklist'

const mocks = vi.hoisted(() => ({ create: vi.fn(), validate: vi.fn(), transition: vi.fn(), refetch: vi.fn() }))
vi.mock('@tanstack/react-query', () => ({ useQuery: () => ({ data: [{ id: 'feed-1', name: 'Maissilage', artikel_nummer: 'F-1' }] }) }))
vi.mock('@/lib/api/masks', () => ({ useScreenDefinition: () => ({ data: { adapter: { temporary: false } }, isLoading: false, error: null }) }))
vi.mock('@/lib/api/feeding-feed-catalog', () => ({ listFeedingFeeds: vi.fn() }))
vi.mock('@/lib/api/feeding-feed-analyses', () => ({
  createFeedingAnalysis: mocks.create, validateFeedingAnalysis: mocks.validate, transitionFeedingAnalysis: mocks.transition,
}))
vi.mock('@/components/mask-builder', () => ({
  useUniversalMaskRuntime: ({ screenId }: { screenId: string }) => ({
    plan: { actions: [] }, entityData: screenId === 'futtermittel/analyse'
      ? { id: 'analysis-1', status: 'validated', revision: 2, findings: [] } : {},
    entityError: null, tableRows: {}, tableQueryStates: {}, tableTotals: {}, setTableQuery: vi.fn(),
    updateUserOverlay: vi.fn(), resetUserOverlay: vi.fn(), lookupBindings: {}, refetch: mocks.refetch,
  }),
  UniversalMaskRenderer: ({ onAction }: { onAction: (key: string) => void }) => <div>
    <button onClick={() => onAction('import_analysis')}>Analyse erfassen</button>
    <button onClick={() => onAction('validate')}>Plausibilitaet pruefen</button>
    <button onClick={() => onAction('release')}>Analyse freigeben</button>
  </div>,
}))

describe('Feeding analysis Meridian journeys', () => {
  it('creates a mapped feed analysis from the worklist overlay', async () => {
    mocks.create.mockResolvedValue({ id: 'analysis-42' })
    render(<FeedingAnalysisWorklist />)
    fireEvent.click(screen.getByRole('button', { name: 'Analyse erfassen' }))
    fireEvent.change(screen.getByLabelText('Futtermittel'), { target: { value: 'feed-1' } })
    fireEvent.change(screen.getByLabelText('Probenbezeichnung'), { target: { value: 'Maissilage Nord' } })
    fireEvent.change(screen.getByLabelText('Trockensubstanz % OS'), { target: { value: '35' } })
    fireEvent.click(screen.getByRole('button', { name: 'Analyse anlegen' }))
    await waitFor(() => expect(mocks.create).toHaveBeenCalledWith(expect.objectContaining({
      feed_id: 'feed-1', bezeichnung: 'Maissilage Nord',
      values: [expect.objectContaining({ nutrient_code: 'dry_matter', value_status: 'measured' })],
    })))
  })

  it('validates and releases with optimistic revision plus audit reason', async () => {
    mocks.validate.mockResolvedValue({}); mocks.transition.mockResolvedValue({})
    render(<FeedingAnalysisDetail analysisId="analysis-1" />)
    fireEvent.click(screen.getByRole('button', { name: 'Plausibilitaet pruefen' }))
    await waitFor(() => expect(mocks.validate).toHaveBeenCalledWith('analysis-1', 2))
    fireEvent.click(screen.getByRole('button', { name: 'Analyse freigeben' }))
    fireEvent.change(screen.getByLabelText('Auditgrund'), { target: { value: 'Laborbefund fachlich geprüft' } })
    fireEvent.click(screen.getByRole('button', { name: 'Verbindlich freigeben' }))
    await waitFor(() => expect(mocks.transition).toHaveBeenCalledWith(
      'analysis-1', 'released', 2, 'Laborbefund fachlich geprüft',
    ))
  })
})
