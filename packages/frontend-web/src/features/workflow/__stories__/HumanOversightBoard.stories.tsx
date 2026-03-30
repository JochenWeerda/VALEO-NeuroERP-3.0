import type { Meta, StoryObj } from '@storybook/react'
import { HumanOversightBoard } from '../HumanOversightBoard'

const meta = {
  title: 'Workflow/HumanOversightBoard',
  component: HumanOversightBoard,
  args: {
    isRefreshing: false,
    rejectionInput: {
      'run-001': 'Budgetfreigabe fehlt',
    },
    runs: [
      {
        run_id: 'run-001',
        capability_key: 'bestellvorschlag_assistant',
        status: 'pending_approval',
        started_at: '2026-03-30T08:30:00Z',
        result: {
          current_stage_key: 'approval',
          gate_decisions: [{ gate_type: 'approval_gate', status: 'deferred' }],
          proposal: { items: 3, total_estimated_cost: 18200 },
        },
      },
      {
        run_id: 'run-002',
        capability_key: 'operations_exception_assistant',
        status: 'pending_approval',
        started_at: '2026-03-30T09:05:00Z',
        result: {
          current_stage_key: 'approval',
          gate_decisions: [{ gate_type: 'approval_gate', status: 'deferred' }],
          exception_code: 'inventory_hold',
        },
      },
      {
        run_id: 'run-003',
        capability_key: 'finance_skonto_assistant',
        status: 'completed',
        started_at: '2026-03-30T07:45:00Z',
        result: {
          current_stage_key: 'closure',
          recommendations: [{ invoice_id: 'AP-77', discount: 140.5 }],
        },
      },
    ],
    onRejectionInputChange: () => undefined,
    onRefresh: () => undefined,
    onApprove: () => undefined,
    onReject: () => undefined,
  },
} satisfies Meta<typeof HumanOversightBoard>

export default meta

type Story = StoryObj<typeof meta>

export const Default: Story = {}
