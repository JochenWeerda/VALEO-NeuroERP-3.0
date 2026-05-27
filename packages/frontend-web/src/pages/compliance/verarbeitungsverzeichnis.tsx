/**
 * DSGVO Art. 30 — Verzeichnis von Verarbeitungstätigkeiten (RoPA)
 * Slice-008
 */
import { useState, useEffect, useCallback } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { toast } from 'sonner'
import { Plus, Download, Pencil, Trash2, ShieldCheck, Eye } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import {
  listActivities,
  createActivity,
  updateActivity,
  deleteActivity,
  downloadExportJson,
  type ProcessingActivity,
  type ProcessingActivityInput,
} from '@/lib/api/gdpr-art30'

const EMPTY_FORM: ProcessingActivityInput = {
  controller_name: '',
  controller_contact: '',
  purpose: '',
  subject_categories: [],
  data_categories: [],
  recipients: [],
  third_country_transfers: [],
  retention_period: '',
  toms: '',
  legal_basis: '',
  system_or_tool: '',
  status: 'AKTIV',
}

function parseLines(text: string): string[] {
  return text
    .split('\n')
    .map((l) => l.trim())
    .filter(Boolean)
}

function linesToText(arr: string[]): string {
  return arr.join('\n')
}

function statusBadgeVariant(status: string): 'default' | 'secondary' | 'outline' {
  if (status === 'AKTIV') return 'default'
  if (status === 'INAKTIV') return 'secondary'
  return 'outline'
}

interface FormFieldsProps {
  form: ProcessingActivityInput
  onChange: (updated: ProcessingActivityInput) => void
}

function FormFields({ form, onChange }: FormFieldsProps): JSX.Element {
  const set = <K extends keyof ProcessingActivityInput>(key: K, val: ProcessingActivityInput[K]) =>
    onChange({ ...form, [key]: val })

  return (
    <div className="grid gap-4 py-2 max-h-[65vh] overflow-y-auto pr-1">
      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label htmlFor="ropa-controller-name">Verantwortlicher (Art. 30 Abs. 1 lit. a) *</Label>
          <Input
            id="ropa-controller-name"
            value={form.controller_name}
            onChange={(e) => set('controller_name', e.target.value)}
            placeholder="VALEO Agrar Handel GmbH"
            data-testid="ropa-controller-name"
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="ropa-controller-contact">Kontakt / DSB</Label>
          <Input
            id="ropa-controller-contact"
            value={form.controller_contact}
            onChange={(e) => set('controller_contact', e.target.value)}
            placeholder="datenschutz@beispiel.de"
            data-testid="ropa-controller-contact"
          />
        </div>
      </div>

      <div className="space-y-1">
        <Label htmlFor="ropa-purpose">Zweck der Verarbeitung (Art. 30 Abs. 1 lit. b) *</Label>
        <Textarea
          id="ropa-purpose"
          value={form.purpose}
          onChange={(e) => set('purpose', e.target.value)}
          placeholder="z. B. Kundenstammdatenverwaltung zur Auftragsabwicklung"
          rows={2}
          data-testid="ropa-purpose"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label htmlFor="ropa-subjects">Kategorien betroffener Personen (lit. c)</Label>
          <Textarea
            id="ropa-subjects"
            value={linesToText(form.subject_categories)}
            onChange={(e) => set('subject_categories', parseLines(e.target.value))}
            placeholder={'Kunden\nMitarbeiter\nLieferanten'}
            rows={3}
            data-testid="ropa-subject-categories"
          />
          <p className="text-xs text-muted-foreground">Eine Kategorie pro Zeile</p>
        </div>
        <div className="space-y-1">
          <Label htmlFor="ropa-data-cats">Kategorien personenbezogener Daten (lit. d)</Label>
          <Textarea
            id="ropa-data-cats"
            value={linesToText(form.data_categories)}
            onChange={(e) => set('data_categories', parseLines(e.target.value))}
            placeholder={'Name\nAdresse\nE-Mail\nBankverbindung'}
            rows={3}
            data-testid="ropa-data-categories"
          />
          <p className="text-xs text-muted-foreground">Eine Kategorie pro Zeile</p>
        </div>
      </div>

      <div className="space-y-1">
        <Label htmlFor="ropa-recipients">Empfängerkategorien (Art. 30 Abs. 1 lit. e)</Label>
        <Textarea
          id="ropa-recipients"
          value={linesToText(form.recipients)}
          onChange={(e) => set('recipients', parseLines(e.target.value))}
          placeholder={'Steuerberater\nKreditinstitut\nBehörden'}
          rows={2}
          data-testid="ropa-recipients"
        />
        <p className="text-xs text-muted-foreground">Eine Kategorie pro Zeile</p>
      </div>

      <div className="space-y-1">
        <Label htmlFor="ropa-retention">Löschfristen (Art. 30 Abs. 1 lit. g)</Label>
        <Input
          id="ropa-retention"
          value={form.retention_period}
          onChange={(e) => set('retention_period', e.target.value)}
          placeholder="10 Jahre nach Vertragsende (§ 257 HGB)"
          data-testid="ropa-retention-period"
        />
      </div>

      <div className="space-y-1">
        <Label htmlFor="ropa-toms">Technisch-organisatorische Maßnahmen (Art. 32 / lit. h)</Label>
        <Textarea
          id="ropa-toms"
          value={form.toms}
          onChange={(e) => set('toms', e.target.value)}
          placeholder="Verschlüsselung, Zugriffskontrolle, Backup-Konzept, Pseudonymisierung…"
          rows={2}
          data-testid="ropa-toms"
        />
      </div>

      <div className="grid grid-cols-2 gap-3">
        <div className="space-y-1">
          <Label htmlFor="ropa-legal-basis">Rechtsgrundlage (Art. 6 DSGVO)</Label>
          <Input
            id="ropa-legal-basis"
            value={form.legal_basis}
            onChange={(e) => set('legal_basis', e.target.value)}
            placeholder="Art. 6 Abs. 1 lit. b (Vertragserfüllung)"
            data-testid="ropa-legal-basis"
          />
        </div>
        <div className="space-y-1">
          <Label htmlFor="ropa-system">System / Tool</Label>
          <Input
            id="ropa-system"
            value={form.system_or_tool}
            onChange={(e) => set('system_or_tool', e.target.value)}
            placeholder="VALEO NeuroERP 3.0"
            data-testid="ropa-system-or-tool"
          />
        </div>
      </div>

      <div className="space-y-1">
        <Label htmlFor="ropa-status">Status</Label>
        <select
          id="ropa-status"
          className="flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm"
          value={form.status}
          onChange={(e) => set('status', e.target.value as 'AKTIV' | 'INAKTIV' | 'ENTWURF')}
          data-testid="ropa-status"
        >
          <option value="AKTIV">AKTIV</option>
          <option value="ENTWURF">ENTWURF</option>
          <option value="INAKTIV">INAKTIV</option>
        </select>
      </div>
    </div>
  )
}

export default function Verarbeitungsverzeichnis(): JSX.Element {
  const qc = useQueryClient()
  const [dialogOpen, setDialogOpen] = useState(false)
  const [editTarget, setEditTarget] = useState<ProcessingActivity | null>(null)
  const [form, setForm] = useState<ProcessingActivityInput>(EMPTY_FORM)
  const [downloadPending, setDownloadPending] = useState(false)

  const { data: activities = [], isLoading, isError } = useQuery({
    queryKey: ['gdpr', 'art30', 'activities'],
    queryFn: () => listActivities(),
  })

  const createMutation = useMutation({
    mutationFn: (payload: ProcessingActivityInput) => createActivity(payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['gdpr', 'art30', 'activities'] })
      toast.success('Verarbeitungstätigkeit gespeichert')
      setDialogOpen(false)
    },
    onError: (e: Error) => {
      toast.error(`Fehler beim Speichern: ${e.message}`)
    },
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }: { id: string; payload: ProcessingActivityInput }) =>
      updateActivity(id, payload),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['gdpr', 'art30', 'activities'] })
      toast.success('Verarbeitungstätigkeit aktualisiert')
      setDialogOpen(false)
    },
    onError: (e: Error) => {
      toast.error(`Fehler beim Aktualisieren: ${e.message}`)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: (id: string) => deleteActivity(id),
    onSuccess: () => {
      void qc.invalidateQueries({ queryKey: ['gdpr', 'art30', 'activities'] })
      toast.success('Verarbeitungstätigkeit gelöscht')
    },
    onError: (e: Error) => {
      toast.error(`Fehler beim Löschen: ${e.message}`)
    },
  })

  const openCreate = useCallback(() => {
    setEditTarget(null)
    setForm(EMPTY_FORM)
    setDialogOpen(true)
  }, [])

  const openEdit = useCallback((activity: ProcessingActivity) => {
    setEditTarget(activity)
    setForm({
      controller_name: activity.controller_name,
      controller_contact: activity.controller_contact,
      purpose: activity.purpose,
      subject_categories: activity.subject_categories,
      data_categories: activity.data_categories,
      recipients: activity.recipients,
      third_country_transfers: activity.third_country_transfers,
      retention_period: activity.retention_period,
      toms: activity.toms,
      legal_basis: activity.legal_basis,
      system_or_tool: activity.system_or_tool,
      status: activity.status,
    })
    setDialogOpen(true)
  }, [])

  const handleSave = useCallback(() => {
    if (!form.controller_name.trim() || !form.purpose.trim()) {
      toast.error('Verantwortlicher und Zweck sind Pflichtfelder')
      return
    }
    if (editTarget) {
      updateMutation.mutate({ id: editTarget.id, payload: form })
    } else {
      createMutation.mutate(form)
    }
  }, [form, editTarget, createMutation, updateMutation])

  const handleExport = useCallback(async () => {
    setDownloadPending(true)
    try {
      await downloadExportJson()
      toast.success('Export heruntergeladen')
    } catch (e) {
      toast.error('Export fehlgeschlagen')
    } finally {
      setDownloadPending(false)
    }
  }, [])

  const isSaving = createMutation.isPending || updateMutation.isPending

  return (
    <div className="p-6 space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <ShieldCheck className="h-6 w-6 text-primary" />
          <div>
            <h1 className="text-xl font-semibold">Verarbeitungsverzeichnis (Art. 30 DSGVO)</h1>
            <p className="text-sm text-muted-foreground">
              Records of Processing Activities — Pflichtverzeichnis nach Art. 30 Abs. 1 DSGVO
            </p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => void handleExport()}
            disabled={downloadPending}
            data-testid="ropa-export-btn"
          >
            <Download className="mr-2 h-4 w-4" />
            {downloadPending ? 'Exportiere…' : 'JSON-Export'}
          </Button>
          <Button size="sm" onClick={openCreate} data-testid="ropa-add-btn">
            <Plus className="mr-2 h-4 w-4" />
            Neue Tätigkeit
          </Button>
        </div>
      </div>

      {isError && (
        <Card>
          <CardContent className="pt-6 text-destructive">
            Fehler beim Laden der Verarbeitungstätigkeiten.
          </CardContent>
        </Card>
      )}

      {isLoading && (
        <div className="text-sm text-muted-foreground animate-pulse">Lade Verarbeitungsverzeichnis…</div>
      )}

      {!isLoading && !isError && activities.length === 0 && (
        <Card>
          <CardContent className="pt-6 text-center text-muted-foreground">
            <ShieldCheck className="mx-auto mb-3 h-10 w-10 opacity-30" />
            <p className="text-sm">Noch keine Verarbeitungstätigkeiten erfasst.</p>
            <Button variant="outline" size="sm" className="mt-4" onClick={openCreate}>
              Erste Tätigkeit anlegen
            </Button>
          </CardContent>
        </Card>
      )}

      {!isLoading && activities.length > 0 && (
        <div className="space-y-3">
          {activities.map((act) => (
            <Card key={act.id} data-testid={`ropa-row-${act.id}`}>
              <CardHeader className="pb-2">
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <CardTitle className="text-base truncate">{act.purpose}</CardTitle>
                    <p className="text-xs text-muted-foreground mt-0.5">
                      {act.controller_name}
                      {act.legal_basis ? ` · ${act.legal_basis}` : ''}
                    </p>
                  </div>
                  <div className="flex items-center gap-2 shrink-0">
                    <Badge variant={statusBadgeVariant(act.status)}>{act.status}</Badge>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label="Bearbeiten"
                      onClick={() => openEdit(act)}
                      data-testid={`ropa-edit-${act.id}`}
                    >
                      <Pencil className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      aria-label="Löschen"
                      disabled={deleteMutation.isPending}
                      onClick={() => deleteMutation.mutate(act.id)}
                      data-testid={`ropa-delete-${act.id}`}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              </CardHeader>
              <CardContent className="pt-0">
                <div className="grid grid-cols-2 gap-x-6 gap-y-1 text-sm">
                  {act.data_categories.length > 0 && (
                    <div>
                      <span className="text-muted-foreground text-xs">Datenkategorien: </span>
                      {act.data_categories.slice(0, 3).join(', ')}
                      {act.data_categories.length > 3 && ` +${act.data_categories.length - 3}`}
                    </div>
                  )}
                  {act.retention_period && (
                    <div>
                      <span className="text-muted-foreground text-xs">Löschfrist: </span>
                      {act.retention_period}
                    </div>
                  )}
                  {act.system_or_tool && (
                    <div>
                      <span className="text-muted-foreground text-xs">System: </span>
                      {act.system_or_tool}
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <Dialog open={dialogOpen} onOpenChange={setDialogOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader>
            <DialogTitle>
              {editTarget ? 'Verarbeitungstätigkeit bearbeiten' : 'Neue Verarbeitungstätigkeit (Art. 30 DSGVO)'}
            </DialogTitle>
          </DialogHeader>
          <FormFields form={form} onChange={setForm} />
          <div className="flex justify-end gap-2 pt-2">
            <Button variant="outline" onClick={() => setDialogOpen(false)} disabled={isSaving}>
              Abbrechen
            </Button>
            <Button
              onClick={handleSave}
              disabled={isSaving}
              data-testid="ropa-save-btn"
            >
              {isSaving ? 'Speichere…' : editTarget ? 'Aktualisieren' : 'Anlegen'}
            </Button>
          </div>
        </DialogContent>
      </Dialog>
    </div>
  )
}
