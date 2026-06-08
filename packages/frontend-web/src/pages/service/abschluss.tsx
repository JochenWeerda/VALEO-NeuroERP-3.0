/**
 * Service-Abschluss — Closure-Node im Service-to-Customer Flow
 * POST /api/v1/service/abschluss
 */

import { useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/react-router-compat'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import {
  WorkflowEntryBanner,
  readWorkflowEntryContext,
} from '@/components/workflow/WorkflowEntryBanner'
import { ArrowLeft, CheckCircle, Loader2, Star } from 'lucide-react'

type AbschlussForm = {
  anfrage_id: string
  kundenzufriedenheit: number
  abschlusskommentar: string
}

// ── Component ────────────────────────────────────────────────────────────────

export default function AbschlussPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { toast } = useToast()
  const workflowContext = readWorkflowEntryContext(searchParams)

  const anfrageId = searchParams.get('anfrage_id') ?? ''

  const [form, setForm] = useState<AbschlussForm>({
    anfrage_id: anfrageId,
    kundenzufriedenheit: 0,
    abschlusskommentar: '',
  })

  const submitMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        ...form,
        workflow_instance_id: workflowContext?.instanceId ?? undefined,
      }
      return (await apiClient.post('/api/v1/service/abschluss', payload)).data
    },
    onSuccess: () => {
      toast({ title: 'Abschluss erfasst', description: 'Der Service-Fall wurde abgeschlossen.' })
      navigate('/service/anfragen')
    },
    onError: () => {
      toast({
        title: 'Fehler',
        description: 'Abschluss konnte nicht gespeichert werden.',
        variant: 'destructive',
      })
    },
  })

  const canSubmit = form.kundenzufriedenheit >= 1 && form.kundenzufriedenheit <= 5

  return (
    <div className="space-y-6 p-6">
      {/* Workflow Banner */}
      {workflowContext && (
        <WorkflowEntryBanner
          context={workflowContext}
          title="Workflow-Handover: Abschluss"
          description="Kundenzufriedenheit und Abschlusskommentar werden hier dokumentiert, um den Service-Fall zu schliessen."
        />
      )}

      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/service/anfragen')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Service-Abschluss</h1>
          <p className="text-muted-foreground">
            Kundenzufriedenheit und Abschluss dokumentieren
            {anfrageId && <span> (Anfrage: {anfrageId.slice(0, 8)})</span>}
          </p>
        </div>
      </div>

      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle>Abschluss</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Star Rating */}
          <div className="space-y-2">
            <Label>
              Kundenzufriedenheit <span className="text-red-500">*</span>
            </Label>
            <div className="flex gap-1">
              {[1, 2, 3, 4, 5].map((rating) => (
                <button
                  key={rating}
                  type="button"
                  onClick={() => setForm((prev) => ({ ...prev, kundenzufriedenheit: rating }))}
                  className="rounded p-1 transition-colors hover:bg-muted"
                  aria-label={`${rating} Stern${rating > 1 ? 'e' : ''}`}
                >
                  <Star
                    className={`h-8 w-8 ${
                      rating <= form.kundenzufriedenheit
                        ? 'fill-yellow-400 text-yellow-400'
                        : 'text-muted-foreground'
                    }`}
                  />
                </button>
              ))}
              <span className="ml-2 self-center text-sm text-muted-foreground">
                {form.kundenzufriedenheit > 0
                  ? `${form.kundenzufriedenheit} von 5`
                  : 'Bitte bewerten'}
              </span>
            </div>
          </div>

          {/* Comment */}
          <div className="space-y-2">
            <Label htmlFor="abschlusskommentar">Abschlusskommentar</Label>
            <Textarea
              id="abschlusskommentar"
              rows={5}
              placeholder="Zusammenfassung des Service-Falls, Empfehlungen, offene Punkte..."
              value={form.abschlusskommentar}
              onChange={(e) =>
                setForm((prev) => ({ ...prev, abschlusskommentar: e.target.value }))
              }
            />
          </div>

          <div className="flex justify-end gap-2">
            <Button variant="outline" onClick={() => navigate('/service/anfragen')}>
              Abbrechen
            </Button>
            <Button
              onClick={() => submitMutation.mutate()}
              disabled={!canSubmit || submitMutation.isPending}
              className="gap-2"
            >
              {submitMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <CheckCircle className="h-4 w-4" />
              )}
              Abschluss speichern
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
