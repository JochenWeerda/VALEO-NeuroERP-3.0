import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { AgentProcessPanel, AgentUxPanel } from '@/components/agent'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { useApproveWorkflow, useListRuns } from '@/lib/api/workflows'
import { HumanOversightBoard } from '@/features/workflow/HumanOversightBoard'

export default function SupervisorPage(): JSX.Element {
  const navigate = useNavigate()
  const runsQuery = useListRuns()
  const approveMutation = useApproveWorkflow()
  const runs = runsQuery.data ?? []
  const [rejectionInput, setRejectionInput] = useState<Record<string, string>>({})

  const shortcuts = buildCoreMaskShortcuts({
    onRefresh: () => {
      void runsQuery.refetch()
    },
    onCancel: () => navigate('/'),
  })
  useKeyboardShortcuts(shortcuts)

  return (
    <div className="flex flex-col">
      <div className="space-y-6 p-6">
        <div>
          <h1 className="text-3xl font-bold">Prozess-Supervisor</h1>
          <p className="text-muted-foreground">
            Human Oversight, Freigaben und Agent-Runs in einer gemeinsamen Arbeitsoberflaeche.
          </p>
        </div>

        <AgentProcessPanel domain="" className="max-w-2xl" />

        <HumanOversightBoard
          runs={runs}
          isRefreshing={runsQuery.isFetching || approveMutation.isPending}
          rejectionInput={rejectionInput}
          onRejectionInputChange={(runId, value) => {
            setRejectionInput((prev) => ({ ...prev, [runId]: value }))
          }}
          onRefresh={() => {
            void runsQuery.refetch()
          }}
          onApprove={(runId) => {
            void approveMutation.mutateAsync({ workflowId: runId, approved: true }).then(() => runsQuery.refetch())
          }}
          onReject={(runId) => {
            void approveMutation
              .mutateAsync({
                workflowId: runId,
                approved: false,
                rejection_reason: rejectionInput[runId] ?? '',
              })
              .then(() => {
                setRejectionInput((prev) => ({ ...prev, [runId]: '' }))
                return runsQuery.refetch()
              })
          }}
        />

        {runs.length > 0 ? (
          <AgentUxPanel
            title="Agent Confidence"
            summary="Vertrauensscore aus laufenden Runs, Idempotenz-Abdeckung und Capability-Bereitschaft."
            confidence={
              runs.length > 0
                ? Math.round((runs.filter((run) => run.status === 'completed').length / runs.length) * 100)
                : 0
            }
            confidenceLabel="Erfolgsrate"
            sources={[
              {
                label: 'Capability-Registry',
                href: '/api/v1/agents/neuroassist/capabilities',
                description: 'Registrierte Agent-Capabilities und Bereitschaftsstatus',
              },
              {
                label: 'Workflow-Runs API',
                href: '/api/v1/agents/neuroassist/runs',
                description: 'Alle gestarteten Agent-Runs dieses Tenants',
              },
              {
                label: 'Idempotency-Store',
                href: '/api/v1/process/actions/idempotency/overview',
                description: 'Replay-Schutz und Command-Abdeckung',
              },
            ]}
            action={{
              label: 'Command Monitor oeffnen',
              href: '/admin/command-monitor',
              description: 'Idempotenz-Ueberwachung und Replay-Nachweis fuer alle Business Commands',
            }}
          />
        ) : null}
      </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
