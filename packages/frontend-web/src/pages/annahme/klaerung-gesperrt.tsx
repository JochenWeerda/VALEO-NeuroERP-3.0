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

type KlaerungDecision = '' | 'sonderfreigabe' | 'gesperrt'

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
    const klaerungPayload = {
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
