import { useState } from 'react'
import { AlertCircle, ArrowLeft } from 'lucide-react'
import { UniversalMaskRenderer, useUniversalMaskRuntime } from '@/components/mask-builder'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { useScreenDefinition } from '@/lib/api/masks'
import { updateFeedingGroup, type FeedingGroupDetail as GroupDetail, type GroupProfile, type GroupRiskLevel, type PregnancyStatus } from '@/lib/api/feeding-groups'
import { getAxiosErrorMessage } from '@/lib/api-client'

const PROFILES: GroupProfile[] = ['custom', 'fresh_cow', 'high_yield_cow', 'mid_lactation_cow', 'late_lactation_cow', 'dry_far_off', 'dry_close_up', 'heifer', 'calf', 'beef_cattle']
const RISKS: GroupRiskLevel[] = ['low', 'medium', 'high', 'critical']
const PREGNANCY: PregnancyStatus[] = ['unknown', 'open', 'pregnant']

export function FeedingGroupDetail({ groupId }: { groupId: string }): JSX.Element {
  const schemaQuery = useScreenDefinition('agrar/feeding-group')
  const runtime = useUniversalMaskRuntime({
    screenId: 'agrar/feeding-group', entityId: groupId, schema: schemaQuery.data,
    permissions: ['futtermittel.rations.update'], enabled: Boolean(schemaQuery.data && groupId),
  })
  const detail = runtime.entityData as unknown as Partial<GroupDetail>
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [animalCount, setAnimalCount] = useState('0')
  const [profile, setProfile] = useState<GroupProfile>('custom')
  const [pregnancy, setPregnancy] = useState<PregnancyStatus>('unknown')
  const [gestationDay, setGestationDay] = useState('')
  const [risk, setRisk] = useState<GroupRiskLevel>('low')
  const [validUntil, setValidUntil] = useState('')
  const [reason, setReason] = useState('')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)

  function beginEdit(): void {
    setName(detail.name ?? '')
    setAnimalCount(String(detail.animal_count ?? 0))
    setProfile(detail.profile_code ?? 'custom')
    setPregnancy(detail.pregnancy_status ?? 'unknown')
    setGestationDay(detail.gestation_day == null ? '' : String(detail.gestation_day))
    setRisk(detail.risk_level ?? 'low')
    setValidUntil(detail.valid_until ?? '')
    setReason('')
    setOpen(true)
  }

  async function save(): Promise<void> {
    if (!detail.revision || !name.trim() || reason.trim().length < 3) return
    setSaving(true)
    setFeedback(null)
    try {
      await updateFeedingGroup(groupId, {
        expected_revision: detail.revision, reason: reason.trim(), name: name.trim(),
        animal_count: Number(animalCount), profile_code: profile, pregnancy_status: pregnancy,
        gestation_day: pregnancy === 'pregnant' && gestationDay ? Number(gestationDay) : null,
        risk_level: risk, valid_until: validUntil || null,
      })
      setOpen(false)
      setFeedback('Tiergruppe wurde als neue Revision gespeichert.')
      await runtime.refetch()
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  if (schemaQuery.isLoading || !runtime.plan) return <p className="px-4 py-6 text-sm text-muted-foreground">Tiergruppe wird geladen…</p>
  if (schemaQuery.error || runtime.entityError) return <p className="flex gap-2 px-4 py-6 text-sm text-destructive" role="alert"><AlertCircle className="h-4 w-4" />Tiergruppe konnte nicht geladen werden.</p>

  return <div data-testid="feeding-group-detail">
    <a href="/portal/rationsoptimierung?view=rations" className="mb-3 inline-flex min-h-touch items-center gap-2 rounded-md px-3 text-sm font-medium text-muted-foreground hover:bg-muted hover:text-foreground"><ArrowLeft className="h-4 w-4" /> Zur Rationsliste</a>
    {feedback ? <p className="mb-3 rounded-md border bg-muted px-3 py-2 text-sm" role="status">{feedback}</p> : null}
    <UniversalMaskRenderer plan={runtime.plan} data={runtime.entityData} tables={runtime.tableRows} tableQueryStates={runtime.tableQueryStates} tableTotals={runtime.tableTotals} onTableQueryChange={runtime.setTableQuery} onOverlayChange={runtime.updateUserOverlay} onOverlayReset={runtime.resetUserOverlay} lookupBindings={runtime.lookupBindings} entityId={groupId} onAction={(key) => { if (key === 'edit_group') beginEdit() }} />
    <Dialog open={open} onOpenChange={setOpen}><DialogContent><DialogHeader><DialogTitle>Tiergruppe bearbeiten</DialogTitle><DialogDescription>Die Aenderung erzeugt eine neue, auditierbare Parameterrevision.</DialogDescription></DialogHeader>
      <div className="grid gap-3 py-2 sm:grid-cols-2">
        <div className="grid gap-1"><Label htmlFor="group-name">Name</Label><Input id="group-name" value={name} onChange={(e) => setName(e.target.value)} /></div>
        <div className="grid gap-1"><Label htmlFor="group-count">Tierzahl</Label><Input id="group-count" type="number" min="0" value={animalCount} onChange={(e) => setAnimalCount(e.target.value)} /></div>
        <div className="grid gap-1"><Label htmlFor="group-profile">Profil</Label><select id="group-profile" className="h-10 rounded-md border bg-background px-3 text-sm" value={profile} onChange={(e) => setProfile(e.target.value as GroupProfile)}>{PROFILES.map((value) => <option key={value}>{value}</option>)}</select></div>
        <div className="grid gap-1"><Label htmlFor="group-risk">Risiko</Label><select id="group-risk" className="h-10 rounded-md border bg-background px-3 text-sm" value={risk} onChange={(e) => setRisk(e.target.value as GroupRiskLevel)}>{RISKS.map((value) => <option key={value}>{value}</option>)}</select></div>
        <div className="grid gap-1"><Label htmlFor="group-pregnancy">Traechtigkeit</Label><select id="group-pregnancy" className="h-10 rounded-md border bg-background px-3 text-sm" value={pregnancy} onChange={(e) => setPregnancy(e.target.value as PregnancyStatus)}>{PREGNANCY.map((value) => <option key={value}>{value}</option>)}</select></div>
        <div className="grid gap-1"><Label htmlFor="group-gestation">Traechtigkeitstag</Label><Input id="group-gestation" type="number" min="0" max="305" disabled={pregnancy !== 'pregnant'} value={gestationDay} onChange={(e) => setGestationDay(e.target.value)} /></div>
        <div className="grid gap-1"><Label htmlFor="group-valid-until">Gueltig bis</Label><Input id="group-valid-until" type="date" value={validUntil} onChange={(e) => setValidUntil(e.target.value)} /></div>
        <div className="grid gap-1 sm:col-span-2"><Label htmlFor="group-reason">Aenderungsgrund</Label><Textarea id="group-reason" value={reason} onChange={(e) => setReason(e.target.value)} /></div>
      </div>
      <DialogFooter><Button variant="outline" onClick={() => setOpen(false)}>Abbrechen</Button><Button disabled={saving || !name.trim() || reason.trim().length < 3} onClick={() => { void save() }}>{saving ? 'Speichert…' : 'Neue Revision speichern'}</Button></DialogFooter>
    </DialogContent></Dialog>
  </div>
}
