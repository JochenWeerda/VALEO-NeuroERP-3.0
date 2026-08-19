/**
 * Kundenportal - Ackerschlagkartei / Feldbuch
 *
 * CRUD (auch für AI-Agenten via OpenAPI operation_id / portalFeldbuchAgentApi):
 *   GET/POST/PUT/DELETE /portal/feldbuch/schlaege[/{id}]
 *   GET/POST/PUT/DELETE /portal/feldbuch/massnahmen[/{id}]
 */

import { useCallback, useEffect, useRef, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import {
  exportFeldbuchCsv,
  importFeldbuchCsv,
  useCreatePortalMassnahme,
  useCreatePortalSchlag,
  useDeletePortalMassnahme,
  useDeletePortalSchlag,
  usePortalArbeitskontext,
  usePortalFeldbuchMassnahmen,
  usePortalFeldbuchSchlaege,
  usePortalFeldbuchStats,
  usePortalJahreswechsel,
  usePortalSammelDuengung,
  usePortalSchlaginfo,
  useUpdatePortalMassnahme,
  useUpdatePortalSchlag,
  type PortalMassnahme,
  type PortalSchlag,
} from '@/lib/api/portal'
import { toast } from 'sonner'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { NativeSelect } from '@/components/ui/native-select'
import { Skeleton } from '@/components/ui/skeleton'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { ErrorState } from '@/components/ErrorState'
import { NextActionPanel } from '@/components/workflow'
import {
  Bug,
  Calendar,
  CheckCircle2,
  Download,
  Droplets,
  FileDown,
  FileSpreadsheet,
  FileUp,
  Globe,
  Info,
  Leaf,
  MapPin,
  Pencil,
  Plus,
  Search,
  Sprout,
  Trash2,
  Upload,
  AlertTriangle,
} from 'lucide-react'

// ── Typ-Konfiguration ──────────────────────────────────────────────────────

const typConfig: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  duengung: { label: 'Düngung', icon: <Droplets className="h-3 w-3" />, color: 'bg-blue-100 text-blue-800' },
  psm: { label: 'Pflanzenschutz', icon: <Bug className="h-3 w-3" />, color: 'bg-amber-100 text-amber-800' },
  aussaat: { label: 'Aussaat', icon: <Sprout className="h-3 w-3" />, color: 'bg-emerald-100 text-emerald-800' },
  ernte: { label: 'Ernte', icon: <Leaf className="h-3 w-3" />, color: 'bg-yellow-100 text-yellow-800' },
  bodenbearbeitung: { label: 'Bodenbearbeitung', icon: <MapPin className="h-3 w-3" />, color: 'bg-gray-100 text-gray-800' },
  beregnung: { label: 'Beregnung', icon: <Droplets className="h-3 w-3" />, color: 'bg-cyan-100 text-cyan-800' },
  aum: { label: 'AUM / Umwelt', icon: <Globe className="h-3 w-3" />, color: 'bg-lime-100 text-lime-800' },
  sonstiges: { label: 'Sonstiges', icon: <Calendar className="h-3 w-3" />, color: 'bg-slate-100 text-slate-800' },
}

function TypBadge({ typ }: { typ: string }) {
  const cfg = typConfig[typ] ?? typConfig.sonstiges
  return (
    <Badge className={`${cfg.color} gap-1 font-normal`}>
      {cfg.icon}
      {cfg.label}
    </Badge>
  )
}

function QuelleBadge({ quelle }: { quelle: string }) {
  if (quelle === 'erp_service' || quelle === 'erp_lieferschein') {
    return (
      <Badge className="bg-purple-100 text-purple-800 gap-1 font-normal">
        <Globe className="h-3 w-3" />
        VALEO Dienst
      </Badge>
    )
  }
  return null
}

// ── Schlag anlegen / bearbeiten ────────────────────────────────────────────

function SchlagFormDialog({
  open,
  onOpenChange,
  wirtschaftsjahr,
  initial,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  wirtschaftsjahr: number
  initial?: PortalSchlag | null
}) {
  const createSchlag = useCreatePortalSchlag()
  const updateSchlag = useUpdatePortalSchlag()
  const editing = Boolean(initial?.id)
  const pending = createSchlag.isPending || updateSchlag.isPending
  const [form, setForm] = useState({ name: '', flaeche: '', kultur: '', gemeinde: '', flik: '', status: 'aktiv' })

  useEffect(() => {
    if (!open) return
    if (initial) {
      setForm({
        name: initial.name ?? '',
        flaeche: String(initial.flaeche ?? ''),
        kultur: initial.kultur ?? '',
        gemeinde: initial.gemeinde ?? '',
        flik: initial.flik ?? '',
        status: initial.status ?? 'aktiv',
      })
    } else {
      setForm({ name: '', flaeche: '', kultur: '', gemeinde: '', flik: '', status: 'aktiv' })
    }
  }, [open, initial])

  const handleSubmit = async () => {
    if (!form.name || !form.flaeche || pending) return
    const payload = {
      name: form.name,
      flaeche: parseFloat(form.flaeche),
      kultur: form.kultur,
      gemeinde: form.gemeinde,
      flik: form.flik || undefined,
      status: form.status,
      wirtschaftsjahr,
    }
    try {
      if (editing && initial) {
        await updateSchlag.mutateAsync({ id: initial.id, data: payload })
        toast.success('Schlag aktualisiert')
      } else {
        await createSchlag.mutateAsync(payload)
        toast.success('Schlag angelegt')
      }
      onOpenChange(false)
    } catch (err) {
      toast.error(getAxiosErrorMessage(err) || 'Schlag konnte nicht gespeichert werden')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            {editing ? 'Schlag bearbeiten' : 'Schlag anlegen'}
          </DialogTitle>
          <DialogDescription>
            {editing ? 'Stammdaten des Schlags ändern' : 'Neuen Feldschlag in Ihrer Ackerschlagkartei erfassen'}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="space-y-1">
            <Label htmlFor="schlag-name">Name *</Label>
            <Input id="schlag-name" data-testid="schlag-name" value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} placeholder="z.B. Südfeld" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="schlag-flaeche">Fläche (ha) *</Label>
              <Input id="schlag-flaeche" data-testid="schlag-flaeche" type="number" step="0.01" value={form.flaeche} onChange={e => setForm(p => ({ ...p, flaeche: e.target.value }))} placeholder="12.5" />
            </div>
            <div className="space-y-1">
              <Label htmlFor="schlag-kultur">Kultur</Label>
              <Input id="schlag-kultur" data-testid="schlag-kultur" value={form.kultur} onChange={e => setForm(p => ({ ...p, kultur: e.target.value }))} placeholder="Winterweizen" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="schlag-gemeinde">Gemeinde</Label>
              <Input id="schlag-gemeinde" data-testid="schlag-gemeinde" value={form.gemeinde} onChange={e => setForm(p => ({ ...p, gemeinde: e.target.value }))} placeholder="Musterdorf" />
            </div>
            <div className="space-y-1">
              <Label htmlFor="schlag-flik">FLIK</Label>
              <Input id="schlag-flik" data-testid="schlag-flik" value={form.flik} onChange={e => setForm(p => ({ ...p, flik: e.target.value }))} placeholder="DE-09-12345-0001" />
            </div>
          </div>
          {editing && (
            <div className="space-y-1">
              <Label>Status</Label>
              <NativeSelect
                value={form.status}
                onValueChange={v => setForm(p => ({ ...p, status: v }))}
                options={[
                  { value: 'aktiv', label: 'aktiv' },
                  { value: 'stillgelegt', label: 'stillgelegt' },
                  { value: 'brache', label: 'brache' },
                ]}
              />
            </div>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Abbrechen</Button>
          <Button onClick={() => void handleSubmit()} disabled={!form.name || !form.flaeche || pending}>
            {pending ? 'Speichern…' : editing ? 'Änderungen speichern' : 'Schlag anlegen'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Maßnahme erfassen Dialog ───────────────────────────────────────────────

function MassnahmeDialog({
  open,
  onOpenChange,
  schlaege,
  initial,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  schlaege: PortalSchlag[]
  initial?: PortalMassnahme | null
}) {
  const createMassnahme = useCreatePortalMassnahme()
  const updateMassnahme = useUpdatePortalMassnahme()
  const editing = Boolean(initial?.id)
  const pending = createMassnahme.isPending || updateMassnahme.isPending
  const emptyForm = {
    schlagId: '',
    datum: new Date().toISOString().split('T')[0],
    typ: 'psm',
    bezeichnung: '',
    mittel: '',
    menge: '',
    einheit: 'l/ha',
    flaeche: '',
    anwender: '',
    bemerkung: '',
    sorte: '',
    aumCode: '',
    sachkundeNummer: '',
    sachkundeGueltigBis: '',
    begruendung: '',
  }
  const [form, setForm] = useState(emptyForm)

  useEffect(() => {
    if (!open) return
    if (initial) {
      setForm({
        schlagId: initial.schlagId ?? '',
        datum: initial.datum?.slice(0, 10) || new Date().toISOString().split('T')[0],
        typ: initial.typ || 'psm',
        bezeichnung: initial.bezeichnung ?? '',
        mittel: initial.mittel ?? '',
        menge: initial.menge != null ? String(initial.menge) : '',
        einheit: initial.einheit || 'l/ha',
        flaeche: initial.flaeche != null ? String(initial.flaeche) : '',
        anwender: initial.anwender ?? '',
        bemerkung: initial.bemerkung ?? '',
        sorte: '',
        aumCode: '',
        sachkundeNummer: initial.sachkundeNummer ?? '',
        sachkundeGueltigBis: initial.sachkundeGueltigBis?.slice(0, 10) ?? '',
        begruendung: initial.begruendung ?? '',
      })
    } else {
      setForm(emptyForm)
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps -- reset only when dialog opens / target changes
  }, [open, initial?.id])

  const handleSubmit = async () => {
    if (!form.datum || !form.typ || pending) return
    const payload: Record<string, unknown> = {
      schlag_id: form.schlagId || undefined,
      datum: form.datum,
      typ: form.typ,
      bezeichnung: form.bezeichnung || undefined,
      mittel: form.mittel || undefined,
      menge: form.menge ? parseFloat(form.menge) : undefined,
      einheit: form.einheit || undefined,
      flaeche: form.flaeche ? parseFloat(form.flaeche) : undefined,
      anwender: form.anwender || undefined,
      bemerkung: form.bemerkung || undefined,
      sorte: form.typ === 'aussaat' ? form.sorte || form.mittel : undefined,
      wassermenge_mm: form.typ === 'beregnung' && form.menge ? parseFloat(form.menge) : undefined,
      aum_code: form.typ === 'aum' ? form.aumCode : undefined,
      begruendung: form.typ === 'psm' ? form.begruendung || undefined : undefined,
      sachkunde_nummer: form.typ === 'psm' ? form.sachkundeNummer || undefined : undefined,
      sachkunde_gueltig_bis: form.typ === 'psm' && form.sachkundeGueltigBis
        ? form.sachkundeGueltigBis
        : undefined,
    }
    try {
      if (editing && initial) {
        await updateMassnahme.mutateAsync({ id: initial.id, data: payload })
        toast.success('Maßnahme aktualisiert')
      } else {
        await createMassnahme.mutateAsync({
          ...payload,
          client_ref: typeof crypto !== 'undefined' && 'randomUUID' in crypto
            ? crypto.randomUUID()
            : undefined,
        })
        toast.success('Maßnahme erfasst')
      }
      onOpenChange(false)
    } catch (err) {
      toast.error(getAxiosErrorMessage(err) || 'Maßnahme konnte nicht gespeichert werden')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            {editing ? 'Maßnahme bearbeiten' : 'Maßnahme erfassen'}
          </DialogTitle>
          <DialogDescription>
            {editing
              ? 'Eigene Portal-Maßnahme ändern (VALEO-Dienste sind schreibgeschützt)'
              : 'Eigene Maßnahme in der Ackerschlagkartei dokumentieren'}
          </DialogDescription>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Schlag</Label>
              <NativeSelect value={form.schlagId} onValueChange={v => setForm(p => ({ ...p, schlagId: v }))} placeholder="Schlag waehlen" options={[{ value: '', label: 'Kein Schlag' }, ...schlaege.map((s) => ({ value: s.id, label: s.name }))]} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="massnahme-datum">Datum *</Label>
              <Input id="massnahme-datum" data-testid="massnahme-datum" type="date" value={form.datum} onChange={e => setForm(p => ({ ...p, datum: e.target.value }))} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="massnahme-typ">Maßnahme-Typ *</Label>
              <NativeSelect id="massnahme-typ" data-testid="massnahme-typ" value={form.typ} onValueChange={v => setForm(p => ({ ...p, typ: v }))} options={Object.entries(typConfig).map(([key, cfg]) => ({ value: key, label: cfg.label }))} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="massnahme-mittel">Mittel / Produkt</Label>
              <Input id="massnahme-mittel" data-testid="massnahme-mittel" value={form.mittel} onChange={e => setForm(p => ({ ...p, mittel: e.target.value }))} placeholder="z.B. Roundup PowerFlex" />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1">
              <Label htmlFor="massnahme-menge">Menge</Label>
              <Input id="massnahme-menge" data-testid="massnahme-menge" type="number" step="0.1" value={form.menge} onChange={e => setForm(p => ({ ...p, menge: e.target.value }))} placeholder="3.5" />
            </div>
            <div className="space-y-1">
              <Label>Einheit</Label>
              <NativeSelect value={form.einheit} onValueChange={v => setForm(p => ({ ...p, einheit: v }))} options={['l/ha', 'kg/ha', 'ml/ha', 'g/ha', 't/ha', 'Stueck/ha'].map((e) => ({ value: e, label: e }))} />
            </div>
            <div className="space-y-1">
              <Label htmlFor="massnahme-flaeche">Fläche (ha)</Label>
              <Input id="massnahme-flaeche" data-testid="massnahme-flaeche" type="number" step="0.01" value={form.flaeche} onChange={e => setForm(p => ({ ...p, flaeche: e.target.value }))} placeholder="12.4" />
            </div>
          </div>
          {form.typ === 'aussaat' && (
            <div className="space-y-1">
              <Label>Sorte *</Label>
              <Input value={form.sorte} onChange={e => setForm(p => ({ ...p, sorte: e.target.value }))} placeholder="z.B. RGT Reform" />
            </div>
          )}
          {form.typ === 'aum' && (
            <div className="space-y-1">
              <Label>AUM-Code *</Label>
              <Input value={form.aumCode} onChange={e => setForm(p => ({ ...p, aumCode: e.target.value }))} placeholder="z.B. ÖRö1" />
            </div>
          )}
          {form.typ === 'psm' && (
            <div className="grid grid-cols-2 gap-3">
              <div className="space-y-1">
                <Label htmlFor="massnahme-begruendung">Begründung *</Label>
                <Input id="massnahme-begruendung" data-testid="massnahme-begruendung" value={form.begruendung} onChange={e => setForm(p => ({ ...p, begruendung: e.target.value }))} placeholder="Schadschwelle / Notwendigkeit" />
              </div>
              <div className="space-y-1">
                <Label htmlFor="massnahme-sachkunde-nr">Sachkunde-Nr. *</Label>
                <Input id="massnahme-sachkunde-nr" data-testid="massnahme-sachkunde-nr" value={form.sachkundeNummer} onChange={e => setForm(p => ({ ...p, sachkundeNummer: e.target.value }))} placeholder="SK-…" />
              </div>
              <div className="space-y-1">
                <Label htmlFor="massnahme-sachkunde-bis">Sachkunde gültig bis *</Label>
                <Input id="massnahme-sachkunde-bis" data-testid="massnahme-sachkunde-bis" type="date" value={form.sachkundeGueltigBis} onChange={e => setForm(p => ({ ...p, sachkundeGueltigBis: e.target.value }))} />
              </div>
            </div>
          )}
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label htmlFor="massnahme-anwender">Anwender</Label>
              <Input id="massnahme-anwender" data-testid="massnahme-anwender" value={form.anwender} onChange={e => setForm(p => ({ ...p, anwender: e.target.value }))} placeholder="Eigenleistung" />
            </div>
            <div className="space-y-1">
              <Label htmlFor="massnahme-bemerkung">Bemerkung</Label>
              <Input id="massnahme-bemerkung" data-testid="massnahme-bemerkung" value={form.bemerkung} onChange={e => setForm(p => ({ ...p, bemerkung: e.target.value }))} />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Abbrechen</Button>
          <Button onClick={() => void handleSubmit()} disabled={!form.datum || !form.typ || pending}>
            {pending ? 'Speichern…' : editing ? 'Änderungen speichern' : 'Maßnahme erfassen'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Export Dialog ──────────────────────────────────────────────────────────

function ExportDialog({
  open,
  onOpenChange,
  schlaege,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  schlaege: PortalSchlag[]
}) {
  const [format, setFormat] = useState<'csv' | 'ackerschlagkartei'>('ackerschlagkartei')
  const [schlagId, setSchlagId] = useState('')
  const [von, setVon] = useState('')
  const [bis, setBis] = useState('')
  const [loading, setLoading] = useState(false)
  const [success, setSuccess] = useState(false)

  const handleExport = async () => {
    setLoading(true)
    try {
      await exportFeldbuchCsv(format, {
        schlagId: schlagId || undefined,
        von: von || undefined,
        bis: bis || undefined,
      })
      setSuccess(true)
      setTimeout(() => setSuccess(false), 3000)
    } finally {
      setLoading(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileDown className="h-5 w-5" />
            Ackerschlagkartei exportieren
          </DialogTitle>
          <DialogDescription>Maßnahmen als CSV für externe Ackerschlagkartei-Software</DialogDescription>
        </DialogHeader>

        {success && (
          <Alert className="border-emerald-200 bg-emerald-50">
            <CheckCircle2 className="h-4 w-4 text-status-success" />
            <AlertTitle className="text-emerald-800">Export erfolgreich</AlertTitle>
            <AlertDescription className="text-emerald-700">Die CSV-Datei wurde heruntergeladen.</AlertDescription>
          </Alert>
        )}

        <div className="grid gap-3">
          <div className="space-y-1">
            <Label>Format</Label>
            <NativeSelect value={format} onValueChange={v => setFormat(v as 'csv' | 'ackerschlagkartei')} options={[{ value: 'ackerschlagkartei', label: 'Ackerschlagkartei-CSV (proPlant, 365FarmNet)' }, { value: 'csv', label: 'Generisches CSV (alle Felder)' }]} />
          </div>
          <div className="space-y-1">
            <Label>Schlag (optional)</Label>
            <NativeSelect value={schlagId} onValueChange={setSchlagId} placeholder="Alle Schlaege" options={[{ value: '', label: 'Alle Schlaege' }, ...schlaege.map((s) => ({ value: s.id, label: s.name }))]} />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Von Datum</Label>
              <Input type="date" value={von} onChange={e => setVon(e.target.value)} />
            </div>
            <div className="space-y-1">
              <Label>Bis Datum</Label>
              <Input type="date" value={bis} onChange={e => setBis(e.target.value)} />
            </div>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Schließen</Button>
          <Button onClick={handleExport} disabled={loading} className="gap-2">
            <Download className="h-4 w-4" />
            {loading ? 'Exportiere…' : 'CSV herunterladen'}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Import Dialog ──────────────────────────────────────────────────────────

function ImportDialog({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
}) {
  const queryClient = useQueryClient()
  const fileInputRef = useRef<HTMLInputElement>(null)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<{ created: number; updated: number; errors: string[] } | null>(null)
  const [error, setError] = useState<string | null>(null)

  const handleFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return
    setLoading(true)
    setResult(null)
    setError(null)
    try {
      const res = await importFeldbuchCsv(file)
      setResult(res)
      await queryClient.invalidateQueries({ queryKey: ['portal', 'feldbuch'] })
    } catch (err: unknown) {
      setError(getAxiosErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  const handleClose = () => {
    setResult(null)
    setError(null)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileUp className="h-5 w-5" />
            CSV importieren
          </DialogTitle>
          <DialogDescription>
            Schläge und Maßnahmen aus externer Ackerschlagkartei importieren
          </DialogDescription>
        </DialogHeader>

        {result ? (
          <div className="space-y-3">
            <Alert className="border-emerald-200 bg-emerald-50">
              <CheckCircle2 className="h-4 w-4 text-status-success" />
              <AlertTitle className="text-emerald-800">Import abgeschlossen</AlertTitle>
              <AlertDescription className="text-emerald-700">
                {result.created} Maßnahmen importiert, {result.updated} aktualisiert.
              </AlertDescription>
            </Alert>
            {result.errors.length > 0 && (
              <Alert variant="destructive">
                <AlertTriangle className="h-4 w-4" />
                <AlertTitle>{result.errors.length} Warnungen</AlertTitle>
                <AlertDescription>
                  <ul className="mt-1 list-disc pl-4 text-xs space-y-0.5">
                    {result.errors.slice(0, 5).map((e, i) => <li key={i}>{e}</li>)}
                    {result.errors.length > 5 && <li>… und {result.errors.length - 5} weitere</li>}
                  </ul>
                </AlertDescription>
              </Alert>
            )}
          </div>
        ) : (
          <>
            <Alert>
              <Info className="h-4 w-4" />
              <AlertTitle>Unterstützte Formate</AlertTitle>
              <AlertDescription className="text-sm">
                CSV mit Semikolon oder Komma als Trennzeichen.
                Bekannte Spalten (dt./engl.): Schlag, Datum, Maßnahme, Mittel, Menge, Einheit, Fläche, Anwender.
              </AlertDescription>
            </Alert>

            <div className="rounded-lg border-2 border-dashed p-8 text-center">
              <FileSpreadsheet className="mx-auto h-12 w-12 text-muted-foreground" />
              <p className="mt-2 text-sm text-muted-foreground">
                CSV-Datei aus Ackerschlagkartei auswählen
              </p>
              <input
                ref={fileInputRef}
                type="file"
                accept=".csv"
                onChange={handleFile}
                className="hidden"
                data-testid="feldbuch-import-file"
              />
              <Button
                variant="outline"
                className="mt-3 gap-2"
                data-testid="feldbuch-import-pick"
                onClick={() => fileInputRef.current?.click()}
                disabled={loading}
              >
                <Upload className="h-4 w-4" />
                {loading ? 'Importiere…' : 'Datei auswählen'}
              </Button>
            </div>

            {error && (
              <Alert variant="destructive">
                <AlertTitle>Import fehlgeschlagen</AlertTitle>
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
          </>
        )}

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>Schließen</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function SammelDuengungDialog({
  open,
  onOpenChange,
  schlaege,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  schlaege: PortalSchlag[]
}) {
  const sammel = usePortalSammelDuengung()
  const [selected, setSelected] = useState<string[]>([])
  const [form, setForm] = useState({
    datum: new Date().toISOString().split('T')[0],
    mittel: 'KAS',
    menge: '350',
    nGehalt: '27',
    anwender: '',
  })

  const toggle = (id: string) => {
    setSelected((prev) => (prev.includes(id) ? prev.filter((x) => x !== id) : [...prev, id]))
  }

  const handleSubmit = async () => {
    if (selected.length === 0 || sammel.isPending) return
    try {
      const result = await sammel.mutateAsync({
        schlag_ids: selected,
        datum: new Date(form.datum).toISOString(),
        mittel: form.mittel,
        menge_kg_ha: parseFloat(form.menge),
        n_gehalt: parseFloat(form.nGehalt) || 0,
        duenger_form: 'M',
        anwender: form.anwender || undefined,
      })
      toast.success(`Sammeldüngung: ${String(result.anzahl ?? selected.length)} Maßnahmen angelegt`)
      setSelected([])
      onOpenChange(false)
    } catch (err) {
      toast.error(getAxiosErrorMessage(err) || 'Sammeldüngung fehlgeschlagen')
    }
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Sammeldüngung</DialogTitle>
          <DialogDescription>Eine Düngung auf mehrere Schläge verteilen (flächenproportional).</DialogDescription>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="max-h-40 space-y-1 overflow-y-auto rounded border p-2">
            {schlaege.map((s) => (
              <label key={s.id} className="flex items-center gap-2 text-sm">
                <input
                  type="checkbox"
                  checked={selected.includes(s.id)}
                  onChange={() => toggle(s.id)}
                />
                {s.name} ({s.flaeche.toFixed(2)} ha)
              </label>
            ))}
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Datum</Label>
              <Input type="date" value={form.datum} onChange={(e) => setForm((p) => ({ ...p, datum: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label>Mittel</Label>
              <Input value={form.mittel} onChange={(e) => setForm((p) => ({ ...p, mittel: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label>Menge kg/ha</Label>
              <Input type="number" value={form.menge} onChange={(e) => setForm((p) => ({ ...p, menge: e.target.value }))} />
            </div>
            <div className="space-y-1">
              <Label>N-Gehalt %</Label>
              <Input type="number" value={form.nGehalt} onChange={(e) => setForm((p) => ({ ...p, nGehalt: e.target.value }))} />
            </div>
          </div>
          <div className="space-y-1">
            <Label>Anwender</Label>
            <Input value={form.anwender} onChange={(e) => setForm((p) => ({ ...p, anwender: e.target.value }))} />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Abbrechen</Button>
          <Button onClick={() => void handleSubmit()} disabled={selected.length === 0 || sammel.isPending}>
            {sammel.isPending ? 'Buche…' : `Auf ${selected.length} Schläge buchen`}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

function SchlaginfoDialog({
  open,
  onOpenChange,
  schlagId,
  wirtschaftsjahr,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  schlagId: string | null
  wirtschaftsjahr: number
}) {
  const { data, isLoading, isError, error } = usePortalSchlaginfo(schlagId, wirtschaftsjahr)
  const kosten = (data?.kosten ?? {}) as Record<string, unknown>
  const schlag = (data?.schlag ?? {}) as Record<string, unknown>

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle>Schlaginformation</DialogTitle>
          <DialogDescription>
            Gesamtdokumentation WJ {wirtschaftsjahr}
            {schlag.name ? ` — ${String(schlag.name)}` : ''}
          </DialogDescription>
        </DialogHeader>
        {isLoading && <Skeleton className="h-24 w-full" />}
        {isError && (
          <Alert variant="destructive">
            <AlertTitle>Schlaginfo nicht geladen</AlertTitle>
            <AlertDescription>{getAxiosErrorMessage(error)}</AlertDescription>
          </Alert>
        )}
        {data && !isLoading && (
          <div className="space-y-2 text-sm">
            <p>Aussaat: {Array.isArray(data.aussaat) ? data.aussaat.length : 0}</p>
            <p>Düngung: {Array.isArray(data.duengung) ? data.duengung.length : 0}</p>
            <p>Pflanzenschutz: {Array.isArray(data.pflanzenschutz) ? data.pflanzenschutz.length : 0}</p>
            <p>Beregnung: {Array.isArray(data.beregnung) ? data.beregnung.length : 0}</p>
            <p>AUM: {Array.isArray(data.aum) ? data.aum.length : 0}</p>
            <p>Ernte: {Array.isArray(data.ernte) ? data.ernte.length : 0}</p>
            <div className="rounded border p-3">
              <p className="font-semibold">Direktkostenfreie Leistung</p>
              <p>{Number(kosten.direktkostenfreieLeistungEur ?? 0).toLocaleString('de-DE', { maximumFractionDigits: 2 })} €</p>
              <p className="text-muted-foreground">
                {kosten.direktkostenfreieLeistungEurHa != null
                  ? `${Number(kosten.direktkostenfreieLeistungEurHa).toLocaleString('de-DE', { maximumFractionDigits: 2 })} €/ha`
                  : '–'}
              </p>
            </div>
          </div>
        )}
        <DialogFooter>
          <Button
            variant="outline"
            disabled={!schlagId}
            onClick={() => {
              if (!schlagId) return
              window.open(
                `/api/v1/portal/feldbuch/schlaege/${schlagId}/schlaginfo.txt?wirtschaftsjahr=${wirtschaftsjahr}`,
                '_blank',
              )
            }}
          >
            Druck/Text
          </Button>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Schließen</Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

// ── Skeleton ───────────────────────────────────────────────────────────────

function FeldbuchSkeleton() {
  return (
    <div className="space-y-6">
      <div className="flex justify-between">
        <Skeleton className="h-10 w-48" />
        <div className="flex gap-2">
          <Skeleton className="h-10 w-24" />
          <Skeleton className="h-10 w-24" />
        </div>
      </div>
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {[...Array(4)].map((_, i) => (
          <Card key={i}><CardContent className="p-4"><Skeleton className="h-12 w-full" /></CardContent></Card>
        ))}
      </div>
      <Skeleton className="h-10 w-full" />
      <Card><CardContent className="p-4 space-y-3">{[...Array(5)].map((_, i) => <Skeleton key={i} className="h-12 w-full" />)}</CardContent></Card>
    </div>
  )
}

// ── Hauptkomponente ────────────────────────────────────────────────────────

export default function PortalFeldbuch() {
  const currentYear = new Date().getFullYear()
  const [activeTab, setActiveTab] = useState('schlaege')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSchlag, setSelectedSchlag] = useState<string>('alle')
  const [wirtschaftsjahr, setWirtschaftsjahr] = useState(currentYear)
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [showImportDialog, setShowImportDialog] = useState(false)
  const [showSchlagDialog, setShowSchlagDialog] = useState(false)
  const [showMassnahmeDialog, setShowMassnahmeDialog] = useState(false)
  const [showSammelDialog, setShowSammelDialog] = useState(false)
  const [schlaginfoId, setSchlaginfoId] = useState<string | null>(null)
  const [editSchlag, setEditSchlag] = useState<PortalSchlag | null>(null)
  const [editMassnahme, setEditMassnahme] = useState<PortalMassnahme | null>(null)
  const [pendingKeys, setPendingKeys] = useState<Set<string>>(new Set())
  const pendingRef = useRef<Set<string>>(new Set())

  const { data: schlaege = [], isLoading: loadingSchlaege, isError: errSchlaege, error: errSchlaegObj, refetch: refetchSchlaege } = usePortalFeldbuchSchlaege()
  const { data: massnahmen = [], isLoading: loadingMassnahmen, isError: errMassnahmen, error: errMassnahmenObj } = usePortalFeldbuchMassnahmen()
  const { data: stats } = usePortalFeldbuchStats()
  const { data: kontext } = usePortalArbeitskontext(wirtschaftsjahr)
  const jahreswechsel = usePortalJahreswechsel()
  const deleteSchlag = useDeletePortalSchlag()
  const deleteMassnahme = useDeletePortalMassnahme()

  const withPending = useCallback(async (key: string, run: () => Promise<void>) => {
    if (pendingRef.current.has(key)) return
    pendingRef.current.add(key)
    setPendingKeys(new Set(pendingRef.current))
    try {
      await run()
    } finally {
      pendingRef.current.delete(key)
      setPendingKeys(new Set(pendingRef.current))
    }
  }, [])

  const isLoading = loadingSchlaege || loadingMassnahmen
  const isError = errSchlaege || errMassnahmen

  if (isLoading) return <FeldbuchSkeleton />
  if (isError) {
    return <ErrorState error={(errSchlaegObj ?? errMassnahmenObj) as Error} onRetry={() => { void refetchSchlaege() }} />
  }

  const handleDeleteSchlag = (schlag: PortalSchlag) => {
    if (!window.confirm(`Schlag „${schlag.name}“ wirklich löschen? Zugehörige Portal-Maßnahmen werden mitgelöscht.`)) return
    void withPending(`schlag:delete:${schlag.id}`, async () => {
      try {
        await deleteSchlag.mutateAsync(schlag.id)
        toast.success('Schlag gelöscht')
      } catch (err) {
        toast.error(getAxiosErrorMessage(err) || 'Schlag konnte nicht gelöscht werden')
      }
    })
  }

  const handleDeleteMassnahme = (m: PortalMassnahme) => {
    if (m.quelle === 'erp_service' || m.quelle === 'erp_lieferschein') {
      toast.error('VALEO-Dienstleistungen können nicht gelöscht werden')
      return
    }
    if (!window.confirm(`Maßnahme vom ${m.datum} wirklich löschen?`)) return
    void withPending(`massnahme:delete:${m.id}`, async () => {
      try {
        await deleteMassnahme.mutateAsync(m.id)
        toast.success('Maßnahme gelöscht')
      } catch (err) {
        toast.error(getAxiosErrorMessage(err) || 'Maßnahme konnte nicht gelöscht werden')
      }
    })
  }

  const handleJahreswechsel = async () => {
    if (jahreswechsel.isPending) return
    try {
      const result = await jahreswechsel.mutateAsync({
        von_jahr: wirtschaftsjahr,
        nach_jahr: wirtschaftsjahr + 1,
      })
      toast.success(
        `Jahreswechsel: ${String(result.angelegt ?? 0)} Schläge nach ${wirtschaftsjahr + 1} übernommen`,
      )
      setWirtschaftsjahr(wirtschaftsjahr + 1)
    } catch (err) {
      toast.error(getAxiosErrorMessage(err) || 'Jahreswechsel fehlgeschlagen')
    }
  }

  // Filter
  const filteredSchlaege = schlaege.filter(s => {
    const matchesYear = s.wirtschaftsjahr == null || s.wirtschaftsjahr === wirtschaftsjahr
    const matchesSearch =
      s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.kultur ?? '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (s.flik ?? '').toLowerCase().includes(searchTerm.toLowerCase())
    return matchesYear && matchesSearch
  })

  const filteredMassnahmen = massnahmen.filter(m => {
    const matchesSearch =
      (m.bezeichnung ?? '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (m.schlagName ?? '').toLowerCase().includes(searchTerm.toLowerCase()) ||
      (m.mittel ?? '').toLowerCase().includes(searchTerm.toLowerCase())
    const matchesSchlag = selectedSchlag === 'alle' || m.schlagId === selectedSchlag
    return matchesSearch && matchesSchlag
  })

  const gesamtFlaeche = stats?.gesamtFlaeche ?? schlaege.reduce((sum, s) => sum + s.flaeche, 0)
  const valeoDienste = stats?.valeoDienste ?? massnahmen.filter(m => m.quelle !== 'portal').length
  const offenePruefungen = massnahmen.filter(m => m.typ === 'psm' && !m.compliant).length
  const nextPortalAction = schlaege.length === 0
    ? 'Legen Sie zuerst Ihre Schlaege an. Danach koennen Sie Massnahmen dokumentieren oder CSV-Daten importieren.'
    : offenePruefungen > 0
      ? 'Pruefen Sie Pflanzenschutz-Massnahmen mit Hinweis und ergaenzen Sie fehlende Angaben.'
      : 'Dokumentieren Sie neue Massnahmen zeitnah oder exportieren Sie die Ackerschlagkartei fuer Ihre Unterlagen.'

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Ackerschlagkartei</h1>
          <p className="text-muted-foreground">Ihre Schläge, dokumentierten Maßnahmen und VALEO-Dienstleistungen</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <NativeSelect
            value={String(wirtschaftsjahr)}
            onValueChange={(v) => setWirtschaftsjahr(Number(v))}
            options={[currentYear - 1, currentYear, currentYear + 1].map((y) => ({
              value: String(y),
              label: `WJ ${y}`,
            }))}
          />
          <Button variant="outline" onClick={() => setShowSammelDialog(true)} className="gap-2">
            <Droplets className="h-4 w-4" />
            Sammeldüngung
          </Button>
          <Button
            variant="outline"
            onClick={() => void handleJahreswechsel()}
            disabled={jahreswechsel.isPending}
            className="gap-2"
          >
            Jahreswechsel
          </Button>
          <Button variant="outline" onClick={() => setShowImportDialog(true)} className="gap-2">
            <Upload className="h-4 w-4" />
            Import
          </Button>
          <Button variant="outline" onClick={() => setShowExportDialog(true)} className="gap-2">
            <Download className="h-4 w-4" />
            Export
          </Button>
        </div>
      </div>

      {kontext && (
        <Alert>
          <Info className="h-4 w-4" />
          <AlertTitle>Arbeitskontext</AlertTitle>
          <AlertDescription>
            {kontext.betriebName} · WJ {kontext.wirtschaftsjahr} · Ernte {kontext.erntejahr} ·{' '}
            {kontext.rolle} · Sync: {kontext.syncStatus}
          </AlertDescription>
        </Alert>
      )}

      <NextActionPanel
        title="Was ist als Naechstes sinnvoll?"
        action={nextPortalAction}
        tone={offenePruefungen > 0 ? 'amber' : schlaege.length === 0 ? 'blue' : 'emerald'}
      />

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2 text-status-success">
                <MapPin className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats?.schlaege ?? schlaege.length}</p>
                <p className="text-sm text-muted-foreground">Schläge</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-100 p-2 text-blue-600">
                <Leaf className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{gesamtFlaeche.toFixed(1)} ha</p>
                <p className="text-sm text-muted-foreground">Gesamtfläche</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-amber-100 p-2 text-status-warning">
                <Calendar className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{stats?.massnahmen ?? massnahmen.length}</p>
                <p className="text-sm text-muted-foreground">Maßnahmen</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-purple-100 p-2 text-purple-600">
                <Globe className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{valeoDienste}</p>
                <p className="text-sm text-muted-foreground">VALEO Dienstleistungen</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Search & Filter */}
      <div className="flex flex-col gap-4 md:flex-row">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            placeholder="Schlag, Kultur, Mittel suchen…"
            value={searchTerm}
            onChange={e => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
        {activeTab === 'massnahmen' && (
          <NativeSelect value={selectedSchlag} onValueChange={setSelectedSchlag} placeholder="Schlag waehlen" options={[{ value: 'alle', label: 'Alle Schlaege' }, ...schlaege.map((s) => ({ value: s.id, label: s.name }))]} />
        )}
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <div className="flex items-center justify-between">
          <TabsList>
            <TabsTrigger value="schlaege">Schläge ({schlaege.length})</TabsTrigger>
            <TabsTrigger value="massnahmen">Maßnahmen ({massnahmen.length})</TabsTrigger>
          </TabsList>
          {activeTab === 'schlaege' && (
            <Button
              size="sm"
              data-testid="schlag-create"
              onClick={() => { setEditSchlag(null); setShowSchlagDialog(true) }}
              className="gap-1"
            >
              <Plus className="h-4 w-4" />
              Schlag anlegen
            </Button>
          )}
          {activeTab === 'massnahmen' && (
            <Button
              size="sm"
              data-testid="massnahme-create"
              onClick={() => { setEditMassnahme(null); setShowMassnahmeDialog(true) }}
              className="gap-1"
            >
              <Plus className="h-4 w-4" />
              Maßnahme erfassen
            </Button>
          )}
        </div>

        {/* ── Schläge Tab ── */}
        <TabsContent value="schlaege" className="mt-4">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Name</TableHead>
                  <TableHead>Kultur</TableHead>
                  <TableHead className="text-right">Fläche</TableHead>
                  <TableHead>FLIK</TableHead>
                  <TableHead>Gemeinde</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead className="text-right">Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredSchlaege.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={7} className="text-center text-muted-foreground py-8">
                      {schlaege.length === 0
                        ? 'Noch keine Schläge angelegt. Klicken Sie auf "Schlag anlegen".'
                        : 'Keine Schläge gefunden'}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredSchlaege.map(schlag => {
                    const rowBusy = pendingKeys.has(`schlag:delete:${schlag.id}`)
                    return (
                    <TableRow key={schlag.id} data-testid={`schlag-row-${schlag.id}`}>
                      <TableCell className="font-medium">{schlag.name}</TableCell>
                      <TableCell>
                        {schlag.kultur ? <Badge variant="secondary">{schlag.kultur}</Badge> : <span className="text-muted-foreground">–</span>}
                      </TableCell>
                      <TableCell className="text-right">{schlag.flaeche.toFixed(2)} ha</TableCell>
                      <TableCell className="font-mono text-xs">{schlag.flik || '–'}</TableCell>
                      <TableCell>{schlag.gemeinde || '–'}</TableCell>
                      <TableCell>
                        <Badge variant={schlag.status === 'aktiv' ? 'default' : 'secondary'}>
                          {schlag.status}
                        </Badge>
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button size="sm" variant="ghost" onClick={() => setSchlaginfoId(schlag.id)} aria-label={`Info ${schlag.name}`}>
                            Info
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            aria-label={`Bearbeiten ${schlag.name}`}
                            data-testid={`schlag-edit-${schlag.id}`}
                            onClick={() => { setEditSchlag(schlag); setShowSchlagDialog(true) }}
                            disabled={rowBusy}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            aria-label={`Löschen ${schlag.name}`}
                            data-testid={`schlag-delete-${schlag.id}`}
                            onClick={() => handleDeleteSchlag(schlag)}
                            disabled={rowBusy}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                    )
                  })
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        {/* ── Maßnahmen Tab ── */}
        <TabsContent value="massnahmen" className="mt-4">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Datum</TableHead>
                  <TableHead>Schlag</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead>Mittel / Bezeichnung</TableHead>
                  <TableHead>Menge</TableHead>
                  <TableHead>Anwender</TableHead>
                  <TableHead>Quelle</TableHead>
                  <TableHead>Compliance</TableHead>
                  <TableHead className="text-right">Aktionen</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredMassnahmen.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center text-muted-foreground py-8">
                      {massnahmen.length === 0
                        ? 'Noch keine Maßnahmen dokumentiert.'
                        : 'Keine Maßnahmen gefunden'}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredMassnahmen.map(m => {
                    const isErp = m.quelle === 'erp_service' || m.quelle === 'erp_lieferschein'
                    const rowBusy = pendingKeys.has(`massnahme:delete:${m.id}`)
                    return (
                    <TableRow key={m.id} data-testid={`massnahme-row-${m.id}`}>
                      <TableCell className="whitespace-nowrap">{m.datum}</TableCell>
                      <TableCell className="font-medium">{m.schlagName || '–'}</TableCell>
                      <TableCell>
                        <TypBadge typ={m.typ} />
                      </TableCell>
                      <TableCell>
                        {m.mittel && <span className="font-medium">{m.mittel}</span>}
                        {m.bezeichnung && m.bezeichnung !== m.mittel && (
                          <span className="text-muted-foreground text-xs ml-1">{m.bezeichnung}</span>
                        )}
                      </TableCell>
                      <TableCell>
                        {m.menge != null ? (
                          <span>{m.menge} {m.einheit}</span>
                        ) : <span className="text-muted-foreground">–</span>}
                      </TableCell>
                      <TableCell>
                        {m.anwender ? (
                          <span className="text-sm">{m.anwender}</span>
                        ) : <span className="text-muted-foreground">–</span>}
                      </TableCell>
                      <TableCell>
                        <QuelleBadge quelle={m.quelle} />
                      </TableCell>
                      <TableCell>
                        {m.typ === 'psm' && (
                          m.compliant === false
                          || !m.begruendung
                          || !m.sachkundeNummer
                          || !m.sachkundeGueltigBis
                        ) && (
                          <Badge className="bg-red-100 text-red-800 gap-1" data-testid={`psm-pruefen-${m.id}`}>
                            <AlertTriangle className="h-3 w-3" />
                            Prüfen
                          </Badge>
                        )}
                      </TableCell>
                      <TableCell className="text-right">
                        <div className="flex justify-end gap-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            aria-label={`Bearbeiten Maßnahme ${m.datum}`}
                            data-testid={`massnahme-edit-${m.id}`}
                            disabled={isErp || rowBusy}
                            onClick={() => { setEditMassnahme(m); setShowMassnahmeDialog(true) }}
                          >
                            <Pencil className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            aria-label={`Löschen Maßnahme ${m.datum}`}
                            data-testid={`massnahme-delete-${m.id}`}
                            disabled={isErp || rowBusy}
                            onClick={() => handleDeleteMassnahme(m)}
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      </TableCell>
                    </TableRow>
                    )
                  })
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Dialoge */}
      <SchlagFormDialog
        open={showSchlagDialog}
        onOpenChange={(v) => { if (!v) setEditSchlag(null); setShowSchlagDialog(v) }}
        wirtschaftsjahr={wirtschaftsjahr}
        initial={editSchlag}
      />
      <MassnahmeDialog
        open={showMassnahmeDialog}
        onOpenChange={(v) => { if (!v) setEditMassnahme(null); setShowMassnahmeDialog(v) }}
        schlaege={schlaege}
        initial={editMassnahme}
      />
      <SammelDuengungDialog open={showSammelDialog} onOpenChange={setShowSammelDialog} schlaege={filteredSchlaege} />
      <SchlaginfoDialog
        open={Boolean(schlaginfoId)}
        onOpenChange={(v) => { if (!v) setSchlaginfoId(null) }}
        schlagId={schlaginfoId}
        wirtschaftsjahr={wirtschaftsjahr}
      />
      <ExportDialog open={showExportDialog} onOpenChange={setShowExportDialog} schlaege={schlaege} />
      <ImportDialog open={showImportDialog} onOpenChange={setShowImportDialog} />
    </div>
  )
}
