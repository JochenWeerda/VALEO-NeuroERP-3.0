/**
 * DSGVO Art. 33 — Datenpannen-Meldeprozess
 * 72h-Meldefrist an Aufsichtsbehörde mit Ampelindikator.
 * Slice-009.
 */
import { useState, useCallback } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { AlertTriangle, CheckCircle2, Clock, Plus, Pencil, ShieldAlert } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import {
  listBreaches,
  createBreach,
  updateBreach,
  notifyAuthority,
  getDeadline,
  type DataBreach,
  type DataBreachInput,
  type DeadlineInfo,
  type TrafficLight,
} from '@/lib/api/gdpr-art33'

const BREACH_TYPES = [
  { value: 'VERTRAULICHKEIT', label: 'Vertraulichkeit (unbefugter Zugriff)' },
  { value: 'INTEGRITAET', label: 'Integrität (unbefugte Änderung)' },
  { value: 'VERFUEGBARKEIT', label: 'Verfügbarkeit (Verlust / Zerstörung)' },
]

const STATUS_OPTIONS = ['ENTDECKT', 'IN_BEARBEITUNG', 'GEMELDET', 'ABGESCHLOSSEN']

const EMPTY_FORM: DataBreachInput = {
  breach_type: 'VERTRAULICHKEIT',
  description: '',
  data_categories: [],
  persons_count_approx: 0,
  records_count_approx: 0,
  dpo_name: '',
  dpo_contact: '',
  likely_consequences: '',
  measures_taken: '',
  discovered_at: new Date().toISOString(),
  status: 'ENTDECKT',
  internal_reference: '',
}

function parseLines(text: string): string[] {
  return text.split('\n').map((l) => l.trim()).filter(Boolean)
}

function TrafficLightBadge({ light, hoursRemaining, isNotified }: { light: TrafficLight; hoursRemaining: number; isNotified: boolean }): JSX.Element {
  if (isNotified) {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-800" data-testid="traffic-light-green">
        <CheckCircle2 className="h-3 w-3" /> Gemeldet
      </span>
    )
  }
  if (light === 'RED') {
    return (
      <span className="inline-flex items-center gap-1 rounded-full bg-red-100 px-2 py-0.5 text-xs font-medium text-red-800" data-testid="traffic-light-red">
        <AlertTriangle className="h-3 w-3" />
        {hoursRemaining === 0 ? 'Überfällig!' : `${hoursRemaining.toFixed(0)}h verbleibend`}
      </span>
    )
  }
  return (
    <span className="inline-flex items-center gap-1 rounded-full bg-amber-100 px-2 py-0.5 text-xs font-medium text-amber-800" data-testid="traffic-light-orange">
      <Clock className="h-3 w-3" /> {hoursRemaining.toFixed(0)}h verbleibend
    </span>
  )
}

function statusBadgeVariant(status: string): 'default' | 'secondary' | 'outline' | 'destructive' {
  switch (status) {
    case 'GEMELDET': return 'default'
    case 'ABGESCHLOSSEN': return 'secondary'
    case 'ENTDECKT': return 'destructive'
    default: return 'outline'
  }
}

interface BreachCardProps {
  breach: DataBreach
  onEdit: (b: DataBreach) => void
  onNotify: (b: DataBreach) => void
}

function BreachCard({ breach, onEdit, onNotify }: BreachCardProps): JSX.Element {
  const { data: deadline } = useQuery({
    queryKey: ['gdpr', 'art33', 'deadline', breach.id],
    queryFn: () => getDeadline(breach.id),
    refetchInterval: 60_000,
  })

  return (
    <Card data-testid={`breach-row-${breach.id}`}>
      <CardHeader className="pb-2">
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1 min-w-0">
            <CardTitle className="text-base truncate">{breach.description}</CardTitle>
            <p className="text-xs text-muted-foreground mt-0.5">
              {breach.breach_type} · Entdeckt: {new Date(breach.discovered_at).toLocaleString('de-DE')}
              {breach.internal_reference ? ` · ${breach.internal_reference}` : ''}
            </p>
          </div>
          <div className="flex items-center gap-2 shrink-0">
            <Badge variant={statusBadgeVariant(breach.status)}>{breach.status}</Badge>
            {deadline && (
              <TrafficLightBadge
                light={deadline.traffic_light}
                hoursRemaining={deadline.hours_remaining}
                isNotified={deadline.is_notified}
              />
            )}
          </div>
        </div>
      </CardHeader>
      <CardContent className="pt-0">
        <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm">
          <div>
            <span className="text-muted-foreground text-xs">Betroffene Personen ca.: </span>
            {breach.persons_count_approx.toLocaleString('de-DE')}
          </div>
          {breach.dpo_contact && (
            <div>
              <span className="text-muted-foreground text-xs">DSB: </span>
              {breach.dpo_name || breach.dpo_contact}
            </div>
          )}
          {breach.data_categories.length > 0 && (
            <div className="col-span-2">
              <span className="text-muted-foreground text-xs">Datenkategorien: </span>
              {breach.data_categories.slice(0, 4).join(', ')}
              {breach.data_categories.length > 4 && ` +${breach.data_categories.length - 4}`}
            </div>
          )}
        </div>
        <div className="mt-3 flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => onEdit(breach)}
            data-testid={`breach-edit-${breach.id}`}
          >
            <Pencil className="mr-1 h-3 w-3" /> Bearbeiten
          </Button>
          {breach.status !== 'GEMELDET' && breach.status !== 'ABGESCHLOSSEN' && (
            <Button
              variant="default"
              size="sm"
              onClick={() => onNotify(breach)}
              data-testid={`breach-notify-${breach.id}`}
            >
              <CheckCircle2 className="mr-1 h-3 w-3" /> Behörde gemeldet
            </Button>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

interface FormFieldsProps {
  form: DataBreachInput
  onChange: (f: DataBreachInput) => void
}

function FormFields({ form, onChange }: FormFieldsProps): JSX.Element {
  const set = <K extends keyof DataBreachInput>(key: K, val: DataBreachInput[K]) =>
    onChange({ ...form, [key]: val })

  return (
    <div className="grid gap-4 py-2 max-h-[60vh] overflow-y-auto pr-1">
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label>Art der Verletzung (Art. 33 Abs. 3 lit. a) *</Label>
          <select
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
            value={form.breach_type}
            onChange={(e) => set('breach_type', e.target.value as DataBreachInput['breach_type'])}
            data-testid="breach-type"
          >
            {BREACH_TYPES.map((t) => (
              <option key={t.value} value={t.value}>{t.label}</option>
            ))}
          </select>
        </div>
        <div className="space-y-1">
          <Label>Status</Label>
          <select
            className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
            value={form.status}
            onChange={(e) => set('status', e.target.value as DataBreachInput['status'])}
            data-testid="breach-status"
          >
            {STATUS_OPTIONS.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      <div className="space-y-1">
        <Label>Beschreibung der Datenpanne *</Label>
        <Textarea
          value={form.description}
          onChange={(e) => set('description', e.target.value)}
          placeholder="Was ist passiert? Wie wurde es entdeckt?"
          rows={3}
          data-testid="breach-description"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label>Betroffene Personen (ca.)</Label>
          <Input
            type="number"
            value={form.persons_count_approx}
            min={0}
            onChange={(e) => set('persons_count_approx', parseInt(e.target.value) || 0)}
            data-testid="breach-persons-count"
          />
        </div>
        <div className="space-y-1">
          <Label>Betroffene Datensätze (ca.)</Label>
          <Input
            type="number"
            value={form.records_count_approx}
            min={0}
            onChange={(e) => set('records_count_approx', parseInt(e.target.value) || 0)}
          />
        </div>
      </div>

      <div className="space-y-1">
        <Label>Betroffene Datenkategorien</Label>
        <Textarea
          value={form.data_categories.join('\n')}
          onChange={(e) => set('data_categories', parseLines(e.target.value))}
          placeholder={'Name\nE-Mail\nBankverbindung'}
          rows={3}
          data-testid="breach-data-categories"
        />
        <p className="text-xs text-muted-foreground">Eine Kategorie pro Zeile</p>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label>DSB Name (Art. 33 Abs. 3 lit. b)</Label>
          <Input
            value={form.dpo_name}
            onChange={(e) => set('dpo_name', e.target.value)}
            placeholder="Max Mustermann"
            data-testid="breach-dpo-name"
          />
        </div>
        <div className="space-y-1">
          <Label>DSB Kontakt</Label>
          <Input
            value={form.dpo_contact}
            onChange={(e) => set('dpo_contact', e.target.value)}
            placeholder="dsb@beispiel.de"
            data-testid="breach-dpo-contact"
          />
        </div>
      </div>

      <div className="space-y-1">
        <Label>Wahrscheinliche Folgen (Art. 33 Abs. 3 lit. c)</Label>
        <Textarea
          value={form.likely_consequences}
          onChange={(e) => set('likely_consequences', e.target.value)}
          placeholder="Identitätsdiebstahl, Phishing, Reputationsschaden…"
          rows={2}
          data-testid="breach-likely-consequences"
        />
      </div>

      <div className="space-y-1">
        <Label>Ergriffene Maßnahmen (Art. 33 Abs. 3 lit. d)</Label>
        <Textarea
          value={form.measures_taken}
          onChange={(e) => set('measures_taken', e.target.value)}
          placeholder="Zugangsdaten zurückgesetzt, Sicherheitslücke geschlossen…"
          rows={2}
          data-testid="breach-measures-taken"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label>Entdeckungszeitpunkt (Fristbeginn)</Label>
          <Input
            type="datetime-local"
            value={form.discovered_at.slice(0, 16)}
            onChange={(e) => set('discovered_at', new Date(e.target.value).toISOString())}
            data-testid="breach-discovered-at"
          />
        </div>
        <div className="space-y-1">
          <Label>Interne Referenz</Label>
          <Input
            value={form.internal_reference}
            onChange={(e) => set('internal_reference', e.target.value)}
            placeholder="INC-2026-001"
          />
        </div>
      </div>
    </div>
  )
}

interface NotifyDialogProps {
  breach: DataBreach | null
  open: boolean
  onClose: () => void
  onConfirm: (notifiedBy: string, ref: string) => void
  isPending: boolean
}

function NotifyDialog({ breach, open, onClose, onConfirm, isPending }: NotifyDialogProps): JSX.Element {
  const [notifiedBy, setNotifiedBy] = useState('')
  const [authorityRef, setAuthorityRef] = useState('')
  return (
    <Dialog open={open} onOpenChange={(o) => { if (!o) onClose() }}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle>Behördenmeldung bestätigen (Art. 33 DSGVO)</DialogTitle>
        </DialogHeader>
        <p className="text-sm text-muted-foreground">
          Datenpanne <strong>{breach?.description?.slice(0, 60)}</strong> als bei der Aufsichtsbehörde gemeldet markieren.
        </p>
        <div className="space-y-3 pt-2">
          <div className="space-y-1">
            <Label>Gemeldet von *</Label>
            <Input
              value={notifiedBy}
              onChange={(e) => setNotifiedBy(e.target.value)}
              placeholder="Max Mustermann, DSB"
              data-testid="notify-by"
            />
          </div>
          <div className="space-y-1">
            <Label>Aktenzeichen Behörde (optional)</Label>
            <Input
              value={authorityRef}
              onChange={(e) => setAuthorityRef(e.target.value)}
              placeholder="BayLDA-2026-001"
              data-testid="notify-authority-ref"
            />
          </div>
        </div>
        <div className="flex justify-end gap-2 pt-2">
          <Button variant="outline" onClick={onClose} disabled={isPending}>Abbrechen</Button>
          <Button
            onClick={() => onConfirm(notifiedBy, authorityRef)}
            disabled={isPending || !notifiedBy.trim()}
            data-testid="notify-confirm-btn"
          >
            {isPending ? 'Speichere…' : 'Meldung bestätigen'}
          </Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}

export default function Datenpannen(): JSX.Element {
  const qc = useQueryClient()
  const [formOpen, setFormOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<DataBreach | null>(null)
  const [form, setForm] = useState<DataBreachInput>(EMPTY_FORM)
  const [notifyTarget, setNotifyTarget] = useState<DataBreach | null>(null)

  const { data: breaches = [], isLoading, isError } = useQuery({
    queryKey: ['gdpr', 'art33', 'breaches'],
    queryFn: () => listBreaches(),
    refetchInterval: 60_000,
  })

  const createMutation = useMutation({
    mutationFn: (p: DataBreachInput) => createBreach(p),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['gdpr', 'art33', 'breaches'] })
      toast.success('Datenpanne erfasst — 72h-Frist läuft!')
      setFormOpen(false)
    },
    onError: (e: Error) => toast.error(`Fehler: ${e.message}`),
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: DataBreachInput }) => updateBreach(id, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['gdpr', 'art33', 'breaches'] })
      toast.success('Datenpanne aktualisiert')
      setFormOpen(false)
    },
    onError: (e: Error) => toast.error(`Fehler: ${e.message}`),
  })

  const notifyMutation = useMutation({
    mutationFn: ({ id, notifiedBy, ref }: { id: string; notifiedBy: string; ref: string }) =>
      notifyAuthority(id, { notified_by: notifiedBy, authority_reference: ref }),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['gdpr', 'art33', 'breaches'] })
      void qc.invalidateQueries({ queryKey: ['gdpr', 'art33', 'deadline'] })
      toast.success('Behördenmeldung erfasst ✓')
      setNotifyTarget(null)
    },
    onError: (e: Error) => toast.error(`Fehler: ${e.message}`),
  })

  const openCreate = useCallback(() => {
    setEditTarget(null)
    setForm({ ...EMPTY_FORM, discovered_at: new Date().toISOString() })
    setFormOpen(true)
  }, [])

  const openEdit = useCallback((b: DataBreach) => {
    setEditTarget(b)
    setForm({
      breach_type: b.breach_type,
      description: b.description,
      data_categories: b.data_categories,
      persons_count_approx: b.persons_count_approx,
      records_count_approx: b.records_count_approx,
      dpo_name: b.dpo_name,
      dpo_contact: b.dpo_contact,
      likely_consequences: b.likely_consequences,
      measures_taken: b.measures_taken,
      discovered_at: b.discovered_at,
      status: b.status,
      internal_reference: b.internal_reference,
    })
    setFormOpen(true)
  }, [])

  const handleSave = useCallback(() => {
    if (!form.description.trim()) {
      toast.error('Beschreibung ist ein Pflichtfeld')
      return
    }
    if (editTarget) {
      updateMutation.mutate({ id: editTarget.id, payload: form })
    } else {
      createMutation.mutate(form)
    }
  }, [form, editTarget, createMutation, updateMutation])

  const isSaving = createMutation.isPending || updateMutation.isPending

  const overdueCount = breaches.filter(
    (b) => b.status !== 'GEMELDET' && b.status !== 'ABGESCHLOSSEN' && b.notified_at === null
  ).length

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ShieldAlert className="h-6 w-6 text-destructive" />
          <div>
            <h1 className="text-xl font-semibold">Datenpannen-Meldeprozess (Art. 33 DSGVO)</h1>
            <p className="text-sm text-muted-foreground">
              72h-Meldefrist an Aufsichtsbehörde · Ampelindikator zeigt verbleibende Zeit
            </p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          {overdueCount > 0 && (
            <span className="rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-800">
              {overdueCount} offen / überfällig
            </span>
          )}
          <Button size="sm" onClick={openCreate} data-testid="breach-add-btn">
            <Plus className="mr-2 h-4 w-4" /> Datenpanne erfassen
          </Button>
        </div>
      </div>

      {isError && (
        <Card>
          <CardContent className="pt-6 text-destructive">Fehler beim Laden der Datenpannen.</CardContent>
        </Card>
      )}

      {isLoading && (
        <div className="text-sm text-muted-foreground animate-pulse">Lade Datenpannen…</div>
      )}

      {!isLoading && !isError && breaches.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-center text-muted-foreground">
            <ShieldAlert className="mx-auto mb-3 h-10 w-10 opacity-30" />
            <p className="text-sm">Keine Datenpannen erfasst — das ist gut!</p>
            <Button variant="outline" size="sm" className="mt-4" onClick={openCreate}>
              Datenpanne erfassen
            </Button>
          </CardContent>
        </Card>
      )}

      {!isLoading && breaches.length > 0 && (
        <div className="space-y-3">
          {breaches.map((b) => (
            <BreachCard
              key={b.id}
              breach={b}
              onEdit={openEdit}
              onNotify={(breach) => setNotifyTarget(breach)}
            />
          ))}
        </div>
      )}

      <Dialog open={formOpen} onOpenChange={setFormOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editTarget ? 'Datenpanne bearbeiten' : 'Neue Datenpanne erfassen (Art. 33 DSGVO)'}
            </DialogTitle>
          </DialogHeader>
          <FormFields form={form} onChange={setForm} />
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setFormOpen(false)} disabled={isSaving}>Abbrechen</Button>
            <Button onClick={handleSave} disabled={isSaving} data-testid="breach-save-btn">
              {isSaving ? 'Speichere…' : editTarget ? 'Aktualisieren' : 'Erfassen'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>

      <NotifyDialog
        breach={notifyTarget}
        open={notifyTarget !== null}
        onClose={() => setNotifyTarget(null)}
        onConfirm={(notifiedBy, ref) => {
          if (notifyTarget) notifyMutation.mutate({ id: notifyTarget.id, notifiedBy, ref })
        }}
        isPending={notifyMutation.isPending}
      />
    </div>
  )
}
