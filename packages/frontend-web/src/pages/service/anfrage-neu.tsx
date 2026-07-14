/**
 * Neue Service-Anfrage erstellen
 * POST /api/v1/service/anfragen
 */

import { useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import {
  WorkflowEntryBanner,
  readWorkflowEntryContext,
} from '@/components/workflow/WorkflowEntryBanner'
import { ArrowLeft, Loader2, Plus } from 'lucide-react'

type AnfrageForm = {
  kunde: string
  betreff: string
  beschreibung: string
  prioritaet: 'hoch' | 'normal' | 'niedrig'
}

export default function AnfrageNeuPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { toast } = useToast()
  const workflowContext = readWorkflowEntryContext(searchParams)

  const [form, setForm] = useState<AnfrageForm>({
    kunde: workflowContext?.partnerName ?? '',
    betreff: workflowContext?.subject ?? '',
    beschreibung: '',
    prioritaet: 'normal',
  })

  const updateField = <K extends keyof AnfrageForm>(field: K, value: AnfrageForm[K]) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const createMutation = useMutation({
    mutationFn: async () =>
      (await apiClient.post('/api/v1/service/anfragen', form)).data,
    onSuccess: () => {
      toast({ title: 'Anfrage erstellt', description: 'Die Service-Anfrage wurde angelegt.' })
      navigate('/service/anfragen')
    },
    onError: () => {
      toast({ title: 'Fehler', description: 'Anfrage konnte nicht erstellt werden.', variant: 'destructive' })
    },
  })

  const canSubmit = form.kunde.trim() !== '' && form.betreff.trim() !== ''

  return (
    <div className="space-y-6 p-6">
      {/* Workflow Banner */}
      {workflowContext && (
        <WorkflowEntryBanner
          context={workflowContext}
          title="Workflow-Handover aus Service-to-Customer"
          description="Neue Anfrage wird aus dem Flow-Spine-Vorgang heraus erstellt."
        />
      )}

      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/service/anfragen')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Neue Service-Anfrage</h1>
          <p className="text-muted-foreground">Kundenservice-Ticket anlegen</p>
        </div>
      </div>

      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle>Anfragedaten</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="kunde">
                Kunde <span className="text-status-error">*</span>
              </Label>
              <Input
                id="kunde"
                placeholder="Kundenname"
                value={form.kunde}
                onChange={(e) => updateField('kunde', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="prioritaet">Prioritaet</Label>
              <select
                id="prioritaet"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={form.prioritaet}
                onChange={(e) => updateField('prioritaet', e.target.value as AnfrageForm['prioritaet'])}
              >
                <option value="hoch">Hoch</option>
                <option value="normal">Normal</option>
                <option value="niedrig">Niedrig</option>
              </select>
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="betreff">
                Betreff <span className="text-status-error">*</span>
              </Label>
              <Input
                id="betreff"
                placeholder="Kurzbeschreibung der Anfrage"
                value={form.betreff}
                onChange={(e) => updateField('betreff', e.target.value)}
              />
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="beschreibung">Beschreibung</Label>
              <Textarea
                id="beschreibung"
                rows={4}
                placeholder="Detaillierte Beschreibung..."
                value={form.beschreibung}
                onChange={(e) => updateField('beschreibung', e.target.value)}
              />
            </div>
          </div>

          <div className="mt-6 flex justify-end gap-2">
            <Button variant="outline" onClick={() => navigate('/service/anfragen')}>
              Abbrechen
            </Button>
            <Button
              onClick={() => createMutation.mutate()}
              disabled={!canSubmit || createMutation.isPending}
              className="gap-2"
            >
              {createMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Plus className="h-4 w-4" />
              )}
              Anfrage erstellen
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
