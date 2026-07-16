import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import { FeedingBusinessDetail } from '@/features/feed-advice/FeedingBusinessDetail'

const mocks = vi.hoisted(() => ({
  create: vi.fn(), apply: vi.fn(), refetch: vi.fn(),
  rations: [{ id: 'ration-target', name: 'Frischmelker', group_id: 'group-1', group_name: 'Hochleistung', version_id: 'version-1', version_no: 1, status: 'draft', readiness_status: 'ready', readiness_blockers: 0, readiness_warnings: 0 }],
  templates: [{ id: 'template-1', business_id: 'business-1', group_id: 'group-1', name: 'Sommer', source_ration_version_id: 'version-1', source_ration_name: 'Frischmelker', source_version_no: 1, snapshot_checksum: 'abc', created_at: '2026-07-16T10:00:00Z' }],
}))

vi.mock('@/lib/api/masks', () => ({
  useScreenDefinition: () => ({ data: { adapter: { temporary: false } }, error: null }),
}))

vi.mock('@/lib/api/feeding-ration-templates', () => ({
  fetchBusinessRations: () => Promise.resolve(mocks.rations),
  fetchRationTemplates: () => Promise.resolve(mocks.templates),
  createRationTemplate: mocks.create,
  applyRationTemplate: mocks.apply,
}))

vi.mock('@/components/mask-builder', () => ({
  useUniversalMaskRuntime: () => ({
    plan: { actions: [] }, entityData: { id: 'business-1', name: 'Milchhof' }, entityError: null,
    tableRows: {}, tableQueryStates: {}, tableTotals: {}, lookupBindings: {}, setTableQuery: vi.fn(),
    userOverlay: {}, updateUserOverlay: vi.fn(), resetUserOverlay: vi.fn(), refetch: mocks.refetch,
  }),
  UniversalMaskRenderer: ({ onAction }: { onAction: (key: string) => void }) => <div>
    <button onClick={() => onAction('create_template')}>Vorlage anlegen</button>
    <button onClick={() => onAction('apply_template')}>Vorlage anwenden</button>
  </div>,
}))

describe('FeedingBusinessDetail', () => {
  it('creates an immutable template from the latest selected version', async () => {
    mocks.create.mockResolvedValue(mocks.templates[0])
    render(<FeedingBusinessDetail businessId="business-1" />)
    fireEvent.click(screen.getByRole('button', { name: 'Vorlage anlegen' }))
    await waitFor(() => expect(screen.getByLabelText('Quellration')).toHaveValue('version-1'))
    fireEvent.change(screen.getByLabelText('Vorlagenname'), { target: { value: 'Sommer 2026' } })
    fireEvent.click(screen.getByRole('button', { name: 'Ausfuehren' }))
    await waitFor(() => expect(mocks.create).toHaveBeenCalledWith(expect.objectContaining({
      name: 'Sommer 2026', source_ration_version_id: 'version-1',
    })))
  })

  it('applies a template with optimistic version and audit reason', async () => {
    mocks.apply.mockResolvedValue({ id: 'version-2', version_no: 2 })
    render(<FeedingBusinessDetail businessId="business-1" />)
    await waitFor(() => expect(screen.getByRole('button', { name: 'Vorlage anwenden' })).toBeInTheDocument())
    fireEvent.click(screen.getByRole('button', { name: 'Vorlage anwenden' }))
    fireEvent.change(screen.getByLabelText('Kopiergrund'), { target: { value: 'Neue Analyse eingetroffen' } })
    fireEvent.click(screen.getByRole('button', { name: 'Ausfuehren' }))
    await waitFor(() => expect(mocks.apply).toHaveBeenCalledWith('template-1', {
      target_ration_id: 'ration-target', expected_latest_version_no: 1, reason: 'Neue Analyse eingetroffen',
    }))
  })
})
