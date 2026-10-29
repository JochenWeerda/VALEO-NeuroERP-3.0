import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import APInvoiceApprovalPanel from '@/features/workflow/APInvoiceApprovalPanel'

const mocks = vi.hoisted(() => ({
  data: {} as Record<string, unknown>,
  request: vi.fn(),
  decide: vi.fn(),
}))

vi.mock('@/lib/api/ap-approval-workflow', () => ({
  useAPApprovalStatus: () => ({ data: mocks.data, isLoading: false }),
  useRequestAPApproval: () => ({ mutateAsync: mocks.request, isPending: false }),
  useActOnAPApproval: () => ({ mutateAsync: mocks.decide, isPending: false }),
}))
vi.mock('@/policy/decision-view', () => ({ buildDecisionView: () => null }))
vi.mock('@/features/workflow/useApprovalDensityProfile', () => ({ useApprovalDensityProfile: () => ({}) }))
vi.mock('@/components/workflow/ProcessStatusPanel', () => ({ ProcessStatusPanel: () => null }))

afterEach(cleanup)
beforeEach(() => {
  vi.clearAllMocks()
  mocks.request.mockResolvedValue({})
  mocks.decide.mockResolvedValue({})
  mocks.data = { status: 'pending', approval_request_id: 'synthetic-request-1', can_decide: true,
    current_approvals: 0, required_approvals: 1, can_post: false }
})

function panel() {
  return render(<APInvoiceApprovalPanel invoiceId="SYNTH-AP" canRequestApproval canPost
    onPosted={vi.fn()} onStatusChanged={vi.fn()} />)
}

it('submits exactly the server request reference without a caller-selected reviewer', async () => {
  panel()
  fireEvent.click(screen.getByRole('button', { name: 'Freigeben' }))
  await waitFor(() => expect(mocks.decide).toHaveBeenCalledWith({ invoice_id: 'SYNTH-AP',
    approval_request_id: 'synthetic-request-1', action: 'approve', comment: undefined }))
})

it('does not offer a decision when server-side eligibility is false', () => {
  mocks.data.can_decide = false
  panel()
  expect(screen.queryByRole('button', { name: 'Freigeben' })).toBeNull()
  expect(screen.queryByRole('button', { name: 'Ablehnen' })).toBeNull()
})

it('cannot submit when the server request reference is missing', () => {
  mocks.data.approval_request_id = null
  panel()
  fireEvent.click(screen.getByRole('button', { name: 'Freigeben' }))
  expect(mocks.decide).not.toHaveBeenCalled()
})

it('requests review without inventing a requester identity', async () => {
  mocks.data = { status: 'not_requested', can_decide: false, can_post: false }
  panel()
  fireEvent.click(screen.getByRole('button', { name: 'Freigabe anfordern' }))
  await waitFor(() => expect(mocks.request).toHaveBeenCalledWith({ invoice_id: 'SYNTH-AP', comment: undefined }))
})
