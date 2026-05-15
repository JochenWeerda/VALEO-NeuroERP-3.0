import { useEffect, useMemo, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import { ModuleToolbar } from '@/components/navigation/ModuleToolbar'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'
import { useToast } from '@/hooks/use-toast'
import { usePatchWarteschlangeStatus, useWarteschlangeEintrag } from '@/lib/api/inventory'
import {
  CrudCapabilityChecklist,
  EvidenceTemplateLink,
  ManagementDecisionPanel,
  NextActionPanel,
  OperationalTaskPlan,
  RoleFocusBar,
} from '@/components/workflow'

type KlaerungDecision = '' | 'sonderfreigabe' | 'gesperrt'
type QualityHoldRole = 'annahme' | 'qs' | 'produktion' | 'leitung'

const qualityHoldRoles = [
  { id: 'annahme', label: 'Annahme', description: 'Haelt die gesperrte Ware zurueck und sorgt dafuer, dass kein Folgeprozess ungeklaert startet.' },
  { id: 'qs', label: 'QS', description: 'Bewertet Pruefergebnis, Begruendung und Sonderfreigabe oder Sperre.' },
  { id: 'produktion', label: 'Produktion', description: 'Sieht, ob die Ware weiterverarbeitet werden darf oder blockiert bleibt.' },
  { id: 'leitung', label: 'Leitung', description: 'Trifft oder prueft die fachliche Freigabe bei Risiko und Abweichung.' },
] satisfies Array<{ id: QualityHoldRole; label: string; description: string }>

function buildHarvestAcceptanceHandoverQuery(input: {
  partnerName: string
  articleId?: string | null
  artikel: string
  lieferscheinNr: string
  vehiclePlate: string
  qualityProtocolId?: string | null
  klaerung: Exclude<KlaerungDecision, ''>
}): string {
  const query = new URLSearchParams()
  query.set('workflowProcess', 'harvest-to-settlement')
  query.set('workflowLabel', `klaerung:${input.vehiclePlate || 'queue'}`)
  query.set('entryMode', 'Klaerung gesperrt')
  if (input.partnerName) query.set('partnerName', input.partnerName)
  if (input.artikel) query.set('subject', `${input.artikel} / Sonderfreigabe`)
  if (input.lieferscheinNr) query.set('lieferscheinNr', input.lieferscheinNr)
  if (input.vehiclePlate) query.set('vehiclePlate', input.vehiclePlate)
  if (input.articleId) query.set('articleId', input.articleId)
  if (input.artikel) query.set('articleName', input.artikel)
  if (input.qualityProtocolId) query.set('qualityProtocolId', input.qualityProtocolId)
  query.set('qpResult', 'gesperrt')
  query.set('klarstellung', input.klaerung)
  return query.toString()
}

export default function KlaerungGesperrtPage(): JSX.Element {
  const navigate = useNavigate()
  const location = useLocation()
  const { toast } = useToast()
  const searchParams = useMemo(() => new URLSearchParams(location.search), [location.search])
  const queueEntryId = searchParams.get('queueEntryId') ?? ''
  const qualityProtocolIdFromQuery = searchParams.get('qualityProtocolId')

  const { data: entry, isLoading } = useWarteschlangeEintrag(queueEntryId || undefined)
  const patchStatus = usePatchWarteschlangeStatus()
  const [roleFocus, setRoleFocus] = useState<QualityHoldRole>('annahme')
  const [decision, setDecision] = useState<KlaerungDecision>(
    (entry?.klaerung?.decision as KlaerungDecision | undefined) ?? '',
  )
  const [reason, setReason] = useState(entry?.klaerung?.reason ?? '')

  const qualityProtocolId = qualityProtocolIdFromQuery ?? entry?.klaerung?.quality_protocol_id ?? null

  useEffect(() => {
    if (!entry?.id) return
    if (entry.klaerung?.decision) {
      setDecision(entry.klaerung.decision as KlaerungDecision)
    }
    if (entry.klaerung?.reason) {
      setReason(entry.klaerung.reason)
    }
  }, [entry?.id, entry?.klaerung?.decision, entry?.klaerung?.reason])

  const hasReason = reason.trim().length > 0
  const canCloseClarification = Boolean(decision && hasReason)
  const blockerCount = (decision ? 0 : 1) + (hasReason ? 0 : 1)
  const nextClarificationAction = !decision
    ? 'Entscheidung waehlen: Sonderfreigabe oder endgueltige Sperre.'
    : !hasReason
      ? 'Kurze Begruendung erfassen, damit die Entscheidung nachvollziehbar ist.'
      : decision === 'sonderfreigabe'
        ? 'Klaerung speichern und Ware in die Annahme-Erfassung uebergeben.'
        : 'Klaerung speichern; Ware bleibt gesperrt und wird nicht weiterverarbeitet.'

  const handleSave = (): void => {
    if (!queueEntryId) {
      toast({ title: 'Queue-Eintrag fehlt', variant: 'destructive' })
      return
    }
    if (!decision) {
      toast({ title: 'Entscheidung fehlt', description: 'Bitte eine Klaerungsentscheidung waehlen.', variant: 'destructive' })
      return
    }
    if (!reason.trim()) {
      toast({ title: 'Begruendung fehlt', description: 'Bitte eine kurze Begruendung erfassen.', variant: 'destructive' })
      return
    }
    const klaerungPayload: NonNullable<NonNullable<typeof entry>['klaerung']> = {
      status: decision === 'sonderfreigabe' ? 'freigegeben' : 'gesperrt',
      decision,
      reason: reason.trim(),
      decided_at: new Date().toISOString(),
      quality_protocol_id: qualityProtocolId ?? undefined,
    }
    patchStatus.mutate(
      {
        id: queueEntryId,
        status: decision === 'sonderfreigabe' ? 'abgeschlossen' : 'gesperrt',
        klaerung: klaerungPayload,
      },
      {
        onSuccess: () => {
          if (decision === 'sonderfreigabe' && entry) {
            const handoverQuery = buildHarvestAcceptanceHandoverQuery({
              partnerName: entry.lieferant ?? '',
              articleId: entry.article_id ?? null,
              artikel: entry.artikel ?? '',
              lieferscheinNr: entry.lieferschein_nr ?? '',
              vehiclePlate: entry.kennzeichen ?? '',
              qualityProtocolId,
              klaerung: decision,
            })
            navigate({
              pathname: '/agrar/ernte-annahme-erfassung',
              search: `?${handoverQuery}`,
            })
            return
          }
          toast({ title: 'Klaerung gespeichert', description: 'Eintrag bleibt gesperrt.' })
          navigate('/annahme/warteschlange')
        },
        onError: () => {
          toast({ title: 'Fehler beim Speichern', variant: 'destructive' })
        },
      },
    )
  }

  if (isLoading) {
    return (
      <PageSurface data-page-surface="annahme-klaerung-loading" contentClassName="space-y-4">
        <Skeleton className="h-8 w-56" />
        <Skeleton className="h-36 w-full" />
        <Skeleton className="h-24 w-full" />
      </PageSurface>
    )
  }

  return (
    <PageSurface data-page-surface="annahme-klaerung-gesperrt" contentClassName="space-y-6">
      <ModuleToolbar
        backTarget="/annahme/warteschlange"
        closeTarget="/annahme/warteschlange"
        title="Klaerung gesperrte Ware"
        actions={
          <Button onClick={handleSave} className="min-h-touch">
            Klaerung speichern
          </Button>
        }
      />

      <RoleFocusBar roles={qualityHoldRoles} value={roleFocus} onChange={setRoleFocus} title="Wer klaert die gesperrte Ware?" />

      <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_360px]">
        <ManagementDecisionPanel
          decision={{
            allowed: canCloseClarification,
            allowedLabel: decision === 'sonderfreigabe' ? 'Sonderfreigabe dokumentiert' : 'Sperre dokumentiert',
            blockedLabel: 'Klaerung offen',
            summary: canCloseClarification
              ? 'Entscheidung und Begruendung sind vorhanden. Die gesperrte Ware kann kontrolliert freigegeben oder als gesperrt dokumentiert werden.'
              : 'Gesperrte Ware darf erst weiterlaufen, wenn Entscheidung und Begruendung dokumentiert sind.',
            blockerCount,
            nextFocus: nextClarificationAction,
            template: { label: 'QS-Sperr- und Sonderfreigabeprotokoll', href: '/docs/qualitaet/qs-sperrfreigabe.md' },
          }}
        />
        <div className="space-y-4">
          <NextActionPanel action={nextClarificationAction} tone={canCloseClarification ? 'emerald' : 'red'} />
          <EvidenceTemplateLink link={{ label: 'Abweichung und Freigabe dokumentieren', href: '/docs/qualitaet/abweichungsnachweis.md' }} />
        </div>
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <OperationalTaskPlan
          title="Pruefplan fuer gesperrte Ware"
          items={[
            { label: 'Ware identifizieren', done: Boolean(entry), hint: entry ? `${entry.kennzeichen ?? 'ohne Kennzeichen'} / ${entry.artikel ?? 'Artikel offen'}` : 'Queue-Eintrag laden.' },
            { label: 'Pruefprotokoll zuordnen', done: Boolean(qualityProtocolId), hint: qualityProtocolId ? `Protokoll ${qualityProtocolId}` : 'Qualitaetsprotokoll fehlt oder wurde nicht uebergeben.' },
            { label: 'Entscheidung treffen', done: Boolean(decision), hint: decision ? 'Entscheidung gewaehlt.' : 'Sonderfreigabe oder Sperre waehlen.' },
            { label: 'Begruendung erfassen', done: hasReason, hint: hasReason ? 'Begruendung ist vorhanden.' : 'Ohne Begruendung keine nachvollziehbare Freigabe.' },
          ]}
        />
        <CrudCapabilityChecklist
          capabilities={[
            { key: 'read', label: 'Sperrfall lesen', available: true, hint: 'Queue, Lieferant, Artikel und Lieferschein sind sichtbar.' },
            { key: 'update', label: 'Klaerung speichern', available: true, hint: 'Entscheidung und Begruendung werden am Eintrag gespeichert.' },
            { key: 'approve', label: 'Sonderfreigabe', available: decision === 'sonderfreigabe', hint: 'Freigabe fuehrt kontrolliert in die Annahme-Erfassung.' },
            { key: 'reject', label: 'Sperre bestaetigen', available: decision === 'gesperrt', hint: 'Ware bleibt gesperrt und wird nicht weiterverarbeitet.' },
            { key: 'evidence', label: 'Nachweis', available: true, hint: 'Vorlage fuer Abweichung und Freigabe ist verlinkt.' },
            { key: 'audit', label: 'Zeitpunkt', available: true, hint: 'Beim Speichern wird der Entscheidungszeitpunkt gesetzt.' },
          ]}
        />
      </div>

      <PageSection
        title="Queue-Kontext"
        description="Gesperrte Ware darf erst nach dokumentierter Klaerung weiterverarbeitet werden."
      >
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Anlieferung</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              <Badge variant="destructive">Gesperrt</Badge>
              <span className="text-sm text-muted-foreground">Queue-ID: {queueEntryId || '—'}</span>
            </div>
            <div className="text-sm">
              <div><span className="text-muted-foreground">Kennzeichen:</span> {entry?.kennzeichen ?? '—'}</div>
              <div><span className="text-muted-foreground">Lieferant:</span> {entry?.lieferant ?? '—'}</div>
              <div><span className="text-muted-foreground">Artikel:</span> {entry?.artikel ?? '—'}</div>
              <div><span className="text-muted-foreground">Lieferschein:</span> {entry?.lieferschein_nr ?? '—'}</div>
            </div>
          </CardContent>
        </Card>
      </PageSection>

      <PageSection title="Klaerungsentscheidung" description="Sonderfreigabe nur mit Begruendung.">
        <Card>
          <CardContent className="space-y-4 pt-6">
            <div className="space-y-2">
              <Label htmlFor="decision">Entscheidung</Label>
              <NativeSelect
                id="decision"
                value={decision}
                onValueChange={(value) => setDecision(value as KlaerungDecision)}
                placeholder="Bitte waehlen"
                options={[
                  { value: 'sonderfreigabe', label: 'Sonderfreigabe' },
                  { value: 'gesperrt', label: 'Endgueltig gesperrt' },
                ]}
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="reason">Begruendung</Label>
              <Textarea
                id="reason"
                value={reason}
                onChange={(event) => setReason(event.target.value)}
                placeholder="Warum ist die Sonderfreigabe bzw. Sperre fachlich begruendet?"
                rows={4}
              />
            </div>
          </CardContent>
        </Card>
      </PageSection>
    </PageSurface>
  )
}
