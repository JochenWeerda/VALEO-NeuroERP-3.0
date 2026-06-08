/**
 * Service-Rueckmeldung — Report-Node im Service-to-Customer Flow
 * POST /api/v1/service/rueckmeldungen
 */

import { useState } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/react-router-compat'
import { useMutation } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useToast } from '@/hooks/use-toast'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'
import {
  WorkflowEntryBanner,
  readWorkflowEntryContext,
} from '@/components/workflow/WorkflowEntryBanner'
import { ArrowLeft, Loader2, Send } from 'lucide-react'

type RueckmeldungForm = {
  anfrage_id: string
  arbeitszeit_stunden: string
  material: string
  ergebnis: 'erledigt' | 'teilweise' | 'offen'
  bemerkung: string
}

type RueckmeldungRole = 'service' | 'techniker' | 'disposition' | 'abrechnung'

const rueckmeldungRoles = [
  {
    id: 'service',
    label: 'Service',
    description: 'Rueckmeldung pruefen und den Kundenfall sauber weiterfuehren.',
  },
  {
    id: 'techniker',
    label: 'Technik',
    description: 'Arbeitszeit, Material und Ergebnis direkt nach dem Einsatz dokumentieren.',
  },
  {
    id: 'disposition',
    label: 'Disposition',
    description: 'Offene oder teilweise erledigte Einsaetze fuer Folgeplanung erkennen.',
  },
  {
    id: 'abrechnung',
    label: 'Abrechnung',
    description: 'Arbeitszeit und Material als Grundlage fuer Folgebelege nachvollziehen.',
  },
] satisfies Array<{ id: RueckmeldungRole; label: string; description: string }>

export default function RueckmeldungPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const { toast } = useToast()
  const workflowContext = readWorkflowEntryContext(searchParams)
  const [roleFocus, setRoleFocus] = useState<RueckmeldungRole>('service')

  const anfrageId = searchParams.get('anfrage_id') ?? ''

  const [form, setForm] = useState<RueckmeldungForm>({
    anfrage_id: anfrageId,
    arbeitszeit_stunden: '',
    material: '',
    ergebnis: 'erledigt',
    bemerkung: '',
  })

  const updateField = <K extends keyof RueckmeldungForm>(field: K, value: RueckmeldungForm[K]) => {
    setForm((prev) => ({ ...prev, [field]: value }))
  }

  const submitMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        ...form,
        arbeitszeit_stunden: parseFloat(form.arbeitszeit_stunden) || 0,
        workflow_instance_id: workflowContext?.instanceId ?? undefined,
      }
      return (await apiClient.post('/api/v1/service/rueckmeldungen', payload)).data
    },
    onSuccess: () => {
      toast({ title: 'Rueckmeldung erfasst', description: 'Die Rueckmeldung wurde gespeichert.' })
      if (anfrageId) {
        navigate(`/service/anfrage/${anfrageId}`)
      } else {
        navigate('/service/anfragen')
      }
    },
    onError: () => {
      toast({
        title: 'Fehler',
        description: 'Rueckmeldung konnte nicht gespeichert werden.',
        variant: 'destructive',
      })
    },
  })

  const arbeitszeit = Number.parseFloat(form.arbeitszeit_stunden)
  const hasArbeitszeit = Number.isFinite(arbeitszeit) && arbeitszeit > 0
  const hasAnfrage = form.anfrage_id.trim().length > 0
  const needsFolgehinweis = form.ergebnis !== 'erledigt'
  const hasFolgehinweis = !needsFolgehinweis || form.bemerkung.trim().length > 0
  const canSendRueckmeldung = hasAnfrage && hasArbeitszeit && hasFolgehinweis
  const rueckmeldungAction = !hasAnfrage
    ? 'Zuerst die zugehoerige Service-Anfrage auswaehlen oder aus der Anfrage heraus starten.'
    : !hasArbeitszeit
      ? 'Arbeitszeit in Stunden erfassen, damit Einsatz und Abrechnung nachvollziehbar sind.'
      : !hasFolgehinweis
        ? 'Bei offenem oder teilweise erledigtem Ergebnis eine konkrete Folgeaktion in der Bemerkung notieren.'
        : 'Rueckmeldung speichern und den Servicefall danach im Ticket weiterpruefen.'

  return (
    <div className="space-y-6 p-6">
      {/* Workflow Banner */}
      {workflowContext && (
        <WorkflowEntryBanner
          context={workflowContext}
          title="Workflow-Handover: Rueckmeldung"
          description="Einsatzdaten und Ergebnis der Service-Anfrage werden hier dokumentiert."
        />
      )}

      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate('/service/anfragen')}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Service-Rueckmeldung</h1>
          <p className="text-muted-foreground">
            Einsatzdaten und Ergebnis erfassen
            {anfrageId && <span> (Anfrage: {anfrageId.slice(0, 8)})</span>}
          </p>
        </div>
      </div>

      <RoleFocusBar
        roles={rueckmeldungRoles}
        value={roleFocus}
        onChange={setRoleFocus}
        title="Arbeitsrolle fuer diese Rueckmeldung"
      />

      <ManagementDecisionPanel
        decision={{
          allowed: canSendRueckmeldung,
          allowedLabel: 'Rueckmeldung bereit',
          blockedLabel: 'Angaben fehlen',
          summary: canSendRueckmeldung
            ? 'Die Rueckmeldung enthaelt Anfrage, Arbeitszeit und Ergebnis. Sie kann als Nachweis fuer Serviceabschluss, Folgeplanung oder Abrechnung gespeichert werden.'
            : 'Fuer eine belastbare Rueckmeldung fehlen noch Pflichtangaben. Ohne Anfrage, Arbeitszeit oder Folgehinweis bleibt unklar, was erledigt wurde und was als naechstes passieren muss.',
          blockerCount: [hasAnfrage, hasArbeitszeit, hasFolgehinweis].filter((value) => !value).length,
          nextFocus: rueckmeldungAction,
          template: {
            label: 'Service-Rueckmeldeprotokoll',
            href: '/docs/service/service-rueckmeldung.md',
          },
        }}
      />

      <div className="grid gap-4 xl:grid-cols-[1.15fr_1fr_1fr]">
        <OperationalTaskPlan
          title="Rueckmeldeplan"
          items={[
            {
              label: 'Anfrage zuordnen',
              done: hasAnfrage,
              hint: hasAnfrage ? `Anfrage ${form.anfrage_id.slice(0, 8)} ist gesetzt.` : 'Rueckmeldung braucht eine eindeutige Service-Anfrage.',
            },
            {
              label: 'Arbeitszeit erfassen',
              done: hasArbeitszeit,
              hint: hasArbeitszeit ? `${form.arbeitszeit_stunden} Stunde(n) erfasst.` : 'Arbeitszeit als Zahl groesser 0 eintragen.',
            },
            {
              label: 'Ergebnis festlegen',
              done: Boolean(form.ergebnis),
              hint: 'Ergebnis steuert, ob Abschluss oder Folgeeinsatz noetig ist.',
            },
            {
              label: 'Folgeaktion dokumentieren',
              done: hasFolgehinweis,
              hint: needsFolgehinweis ? 'Bei offenem Ergebnis muss die naechste Aktion im Hinweis stehen.' : 'Bei erledigtem Ergebnis ist ein Hinweis optional.',
            },
          ]}
        />
        <NextActionPanel action={rueckmeldungAction} tone={canSendRueckmeldung ? 'emerald' : 'amber'} />
        <div className="space-y-3">
          <EvidenceTemplateLink
            link={{
              label: 'Einsatznachweis Service',
              href: '/docs/service/einsatznachweis.md',
            }}
          />
          <CrudCapabilityChecklist
            capabilities={[
              { key: 'create', label: 'Rueckmeldung anlegen', available: true, hint: 'POST speichert die Rueckmeldung als neuen Nachweis.' },
              { key: 'read', label: 'Anfragebezug lesen', available: hasAnfrage, hint: 'Anfrage-ID kommt aus dem Ticket oder kann hier geprueft werden.' },
              { key: 'update', label: 'Einsatzdaten aendern', available: true, hint: 'Arbeitszeit, Material, Ergebnis und Hinweis werden gefuehrt erfasst.' },
              { key: 'evidence', label: 'Nachweis', available: canSendRueckmeldung, hint: 'Vollstaendige Rueckmeldung dient als Einsatz- und Abrechnungsnachweis.' },
            ]}
          />
        </div>
      </div>

      {/* Form */}
      <Card>
        <CardHeader>
          <CardTitle>Rueckmeldung</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid gap-4 md:grid-cols-2">
            <div className="space-y-2">
              <Label htmlFor="arbeitszeit">Arbeitszeit (Stunden)</Label>
              <Input
                id="arbeitszeit"
                type="number"
                step="0.5"
                min="0"
                placeholder="z.B. 2.5"
                value={form.arbeitszeit_stunden}
                onChange={(e) => updateField('arbeitszeit_stunden', e.target.value)}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="ergebnis">Ergebnis</Label>
              <select
                id="ergebnis"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm"
                value={form.ergebnis}
                onChange={(e) =>
                  updateField('ergebnis', e.target.value as RueckmeldungForm['ergebnis'])
                }
              >
                <option value="erledigt">Erledigt</option>
                <option value="teilweise">Teilweise erledigt</option>
                <option value="offen">Offen / Folgeeinsatz noetig</option>
              </select>
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="material">Eingesetztes Material</Label>
              <Input
                id="material"
                placeholder="z.B. Ersatzteile, Verbrauchsmaterial..."
                value={form.material}
                onChange={(e) => updateField('material', e.target.value)}
              />
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="bemerkung">Bemerkung</Label>
              <Textarea
                id="bemerkung"
                rows={4}
                placeholder="Zusaetzliche Hinweise, Befunde, Empfehlungen..."
                value={form.bemerkung}
                onChange={(e) => updateField('bemerkung', e.target.value)}
              />
            </div>
          </div>

          <div className="mt-6 flex justify-end gap-2">
            <Button variant="outline" onClick={() => navigate('/service/anfragen')}>
              Abbrechen
            </Button>
            <Button
              onClick={() => submitMutation.mutate()}
              disabled={submitMutation.isPending || !canSendRueckmeldung}
              className="gap-2"
            >
              {submitMutation.isPending ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <Send className="h-4 w-4" />
              )}
              Rueckmeldung senden
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
