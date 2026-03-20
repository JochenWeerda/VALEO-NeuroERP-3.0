import { describe, expect, it } from 'vitest'
import { render, screen } from '@testing-library/react'
import { IdempotencyMonitoringPanel } from '@/components/agent/IdempotencyMonitoringPanel'

describe('IdempotencyMonitoringPanel', () => {
  it('zeigt den Monitoring-Überblick fuer Idempotenz', () => {
    render(
      <IdempotencyMonitoringPanel
        overview={{
          schema_version: 1,
          confidence_score: 82,
          catalog: {
            total_commands: 12,
            idempotent_commands: 8,
            human_confirmation_commands: 3,
            agent_ready_commands: 6,
            idempotent_coverage_pct: 67,
          },
          store: {
            total_records: 24,
            tenant_count: 2,
            execution_count: 24,
            command_count: 7,
            aggregate_count: 4,
            commands: ['ApproveAPInvoice', 'FinalizeAgrarSettlement'],
            aggregates: ['ap_invoice', 'agrar_settlement'],
          },
          recommended_action: 'Idempotente Commands sind live und replay-sicher.',
          lookup_paths: [
            '/api/v1/process/actions/execute',
            '/api/v1/process/actions/idempotency/{tenant_id}/{idempotency_key}',
          ],
        }}
      />,
    )

    expect(screen.getByText('Idempotency Monitoring')).toBeInTheDocument()
    expect(screen.getByText('82%')).toBeInTheDocument()
    expect(screen.getByText('12')).toBeInTheDocument()
    expect(screen.getByText('8')).toBeInTheDocument()
    expect(screen.getByText('24')).toBeInTheDocument()
    expect(screen.getByText('ApproveAPInvoice')).toBeInTheDocument()
    expect(screen.getByText('/api/v1/process/actions/execute')).toBeInTheDocument()
  })
})
