import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { StudioMigrationPlan } from '@/features/screen-studio/StudioMigrationPlan'

afterEach(cleanup)

const save = vi.hoisted(() => vi.fn())
vi.mock('@/lib/api/studio', () => ({ saveStudioMigrationPlan: save }))
vi.mock('@/lib/api-client', () => ({ getAxiosErrorMessage: (error: Error) => error.message }))
const result = { draft_id: 'draft', candidate_revision: 'revision', requires_definition_update: false, schema_changes: [] }
beforeEach(() => { vi.clearAllMocks(); save.mockResolvedValue(result) })

it('prepares only the saved revision and hides its result after revision changes', async () => {
  const prepared = vi.fn()
  const view = render(<StudioMigrationPlan draftId="draft" revision="revision" disabled={false} onPrepared={prepared} />)
  fireEvent.click(screen.getByRole('button'))
  await screen.findByRole('status')
  expect(save).toHaveBeenCalledWith('draft', 'revision')
  expect(prepared).toHaveBeenCalledWith(result)
  view.rerender(<StudioMigrationPlan draftId="draft" revision="changed" disabled={false} onPrepared={prepared} />)
  expect(screen.queryByRole('status')).not.toBeInTheDocument()
})

it('does not invoke the command while disabled or without a stored revision', () => {
  const view = render(<StudioMigrationPlan draftId="draft" revision="revision" disabled onPrepared={vi.fn()} />)
  fireEvent.click(screen.getByRole('button'))
  expect(save).not.toHaveBeenCalled()
  view.rerender(<StudioMigrationPlan disabled={false} onPrepared={vi.fn()} />)
  expect(screen.getByRole('button')).toBeDisabled()
})

it.each([
  [{ requires_definition_update: true }, /Bindungen müssen zuerst/],
  [{ schema_changes: [{ operation: 'create_table' }] }, /Bereitstellungsnachweis/],
] as const)('shows unresolved work rather than a release promise: %j', async (change, text) => {
  save.mockResolvedValue({ ...result, ...change })
  render(<StudioMigrationPlan draftId="draft" revision="revision" disabled={false} onPrepared={vi.fn()} />)
  fireEvent.click(screen.getByRole('button'))
  await waitFor(() => expect(screen.getByRole('status')).toHaveTextContent(text))
})

it('reports a rejected command without calling the success callback', async () => {
  save.mockRejectedValue(new Error('Plan abgelehnt'))
  const prepared = vi.fn()
  render(<StudioMigrationPlan draftId="draft" revision="revision" disabled={false} onPrepared={prepared} />)
  fireEvent.click(screen.getByRole('button'))
  expect(await screen.findByRole('alert')).toHaveTextContent('Plan abgelehnt')
  expect(prepared).not.toHaveBeenCalled()
})
