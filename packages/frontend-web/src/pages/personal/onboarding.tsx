import { useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  useCreateOnboardingRun,
  useOnboardingChecklists,
  useOnboardingRuns,
  type OnboardingRun,
  type OnboardingStatus,
} from '@/lib/api/personal'
import { useToast } from '@/components/ui/toast-provider'

const statusLabels: Record<OnboardingStatus, string> = {
  not_started: 'Nicht gestartet',
  in_progress: 'In Bearbeitung',
  completed: 'Abgeschlossen',
  cancelled: 'Abgebrochen',
}

export default function PersonalOnboardingPage(): JSX.Element {
  const { push } = useToast()
  const { data: runs, isLoading } = useOnboardingRuns()
  const { data: checklists, isLoading: loadingChecklists } = useOnboardingChecklists()
  const createMutation = useCreateOnboardingRun()

  const [employeeRef, setEmployeeRef] = useState('')
  const [checklistId, setChecklistId] = useState('')
  const [dueDate, setDueDate] = useState('')
  const [assignedBy, setAssignedBy] = useState('')

  const list = useMemo(() => runs ?? [], [runs])

  const save = (): void => {
    if (!employeeRef.trim() || !checklistId) {
      push('Bitte Mitarbeiter-Referenz und Checkliste angeben.')
      return
    }
    createMutation.mutate(
      {
        checklistId,
        employeeRef: employeeRef.trim(),
        assignedBy: assignedBy.trim() || undefined,
        dueDate: dueDate || undefined,
        status: 'not_started',
        progressPercent: 0,
      },
      {
        onSuccess: () => {
          push('Onboarding-Run angelegt.')
          setEmployeeRef('')
          setChecklistId('')
          setDueDate('')
          setAssignedBy('')
        },
        onError: (error) => {
          push(error instanceof Error ? error.message : 'Speichern fehlgeschlagen.')
        },
      },
    )
  }

  const columns = [
    { key: 'employeeRef' as const, label: 'Mitarbeiter' },
    {
      key: 'checklistTitle' as const,
      label: 'Checkliste',
      render: (item: OnboardingRun) => item.checklistTitle || item.checklistCode || item.checklistId,
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (item: OnboardingRun) => <Badge variant="outline">{statusLabels[item.status]}</Badge>,
    },
    {
      key: 'progressPercent' as const,
      label: 'Fortschritt',
      render: (item: OnboardingRun) => `${item.progressPercent}%`,
    },
    {
      key: 'dueDate' as const,
      label: 'Faellig',
      render: (item: OnboardingRun) =>
        item.dueDate ? new Date(item.dueDate).toLocaleDateString('de-DE') : <span className="text-muted-foreground">-</span>,
    },
    {
      key: 'assignedBy' as const,
      label: 'Zugewiesen von',
      render: (item: OnboardingRun) => item.assignedBy || <span className="text-muted-foreground">-</span>,
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div>
        <h1 className="text-3xl font-bold">Onboarding</h1>
        <p className="text-muted-foreground">Checklisten und Einarbeitungslaeufe</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Run anlegen</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="employee-ref">Mitarbeiter-Referenz</Label>
              <Input id="employee-ref" value={employeeRef} onChange={(e) => setEmployeeRef(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="checklist-id">Checkliste</Label>
              <select
                id="checklist-id"
                className="w-full rounded-md border border-input bg-background px-3 py-2"
                value={checklistId}
                onChange={(e) => setChecklistId(e.target.value)}
                disabled={loadingChecklists}
              >
                <option value="">Bitte waehlen</option>
                {(checklists ?? []).map((entry) => (
                  <option key={entry.id} value={entry.id}>
                    {entry.checklist_code} - {entry.title}
                  </option>
                ))}
              </select>
            </div>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="grid gap-2">
              <Label htmlFor="assigned-by">Zugewiesen von</Label>
              <Input id="assigned-by" value={assignedBy} onChange={(e) => setAssignedBy(e.target.value)} />
            </div>
            <div className="grid gap-2">
              <Label htmlFor="due-date">Faellig bis</Label>
              <Input id="due-date" type="date" value={dueDate} onChange={(e) => setDueDate(e.target.value)} />
            </div>
          </div>

          <Button onClick={save} disabled={createMutation.isPending || loadingChecklists}>
            {createMutation.isPending ? 'Speichert...' : 'Speichern'}
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Runs</CardTitle>
        </CardHeader>
        <CardContent className="pt-6">
          {isLoading ? <div className="text-sm text-muted-foreground">Laedt...</div> : <DataTable data={list} columns={columns} />}
        </CardContent>
      </Card>
    </div>
  )
}
