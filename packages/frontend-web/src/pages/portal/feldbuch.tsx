/**
 * Kundenportal - Ackerschlagkartei / Feldbuch
 *
 * Echte Daten via:
 *   GET /portal/feldbuch/schlaege
 *   GET /portal/feldbuch/massnahmen
 *   GET /portal/feldbuch/stats
 *   POST /portal/feldbuch/massnahmen
 *   GET /portal/feldbuch/export?format=ackerschlagkartei
 *   POST /portal/feldbuch/import
 */

import { useRef, useState } from 'react'
import {
  exportFeldbuchCsv,
  importFeldbuchCsv,
  useCreatePortalMassnahme,
  useCreatePortalSchlag,
  usePortalFeldbuchMassnahmen,
  usePortalFeldbuchSchlaege,
  usePortalFeldbuchStats,
  type PortalMassnahme,
  type PortalSchlag,
} from '@/lib/api/portal'
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
  Plus,
  Search,
  Sprout,
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

// ── Schlag anlegen Dialog ──────────────────────────────────────────────────

function SchlagAnlegenDialog({
  open,
  onOpenChange,
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
}) {
  const createSchlag = useCreatePortalSchlag()
  const [form, setForm] = useState({ name: '', flaeche: '', kultur: '', gemeinde: '', flik: '' })

  const handleSubmit = async () => {
    if (!form.name || !form.flaeche) return
    await createSchlag.mutateAsync({
      name: form.name,
      flaeche: parseFloat(form.flaeche),
      kultur: form.kultur,
      gemeinde: form.gemeinde,
      flik: form.flik || undefined,
      status: 'aktiv',
    } as Omit<PortalSchlag, 'id'>)
    setForm({ name: '', flaeche: '', kultur: '', gemeinde: '', flik: '' })
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-md">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <MapPin className="h-5 w-5" />
            Schlag anlegen
          </DialogTitle>
          <DialogDescription>Neuen Feldschlag in Ihrer Ackerschlagkartei erfassen</DialogDescription>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="space-y-1">
            <Label>Name *</Label>
            <Input value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} placeholder="z.B. Südfeld" />
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Fläche (ha) *</Label>
              <Input type="number" step="0.01" value={form.flaeche} onChange={e => setForm(p => ({ ...p, flaeche: e.target.value }))} placeholder="12.5" />
            </div>
            <div className="space-y-1">
              <Label>Kultur</Label>
              <Input value={form.kultur} onChange={e => setForm(p => ({ ...p, kultur: e.target.value }))} placeholder="Winterweizen" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Gemeinde</Label>
              <Input value={form.gemeinde} onChange={e => setForm(p => ({ ...p, gemeinde: e.target.value }))} placeholder="Musterdorf" />
            </div>
            <div className="space-y-1">
              <Label>FLIK</Label>
              <Input value={form.flik} onChange={e => setForm(p => ({ ...p, flik: e.target.value }))} placeholder="DE-09-12345-0001" />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Abbrechen</Button>
          <Button onClick={handleSubmit} disabled={!form.name || !form.flaeche || createSchlag.isPending}>
            {createSchlag.isPending ? 'Speichern…' : 'Schlag anlegen'}
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
}: {
  open: boolean
  onOpenChange: (v: boolean) => void
  schlaege: PortalSchlag[]
}) {
  const createMassnahme = useCreatePortalMassnahme()
  const [form, setForm] = useState({
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
  })

  const handleSubmit = async () => {
    if (!form.datum || !form.typ) return
    await createMassnahme.mutateAsync({
      schlagId: form.schlagId || null,
      schlagName: schlaege.find(s => s.id === form.schlagId)?.name ?? null,
      datum: form.datum,
      typ: form.typ,
      bezeichnung: form.bezeichnung || undefined,
      mittel: form.mittel || undefined,
      menge: form.menge ? parseFloat(form.menge) : undefined,
      einheit: form.einheit || undefined,
      flaeche: form.flaeche ? parseFloat(form.flaeche) : undefined,
      anwender: form.anwender || undefined,
      bemerkung: form.bemerkung || undefined,
    } as Omit<PortalMassnahme, 'id' | 'quelle' | 'compliant' | 'exportiert'>)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-lg">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <Calendar className="h-5 w-5" />
            Maßnahme erfassen
          </DialogTitle>
          <DialogDescription>Eigene Maßnahme in der Ackerschlagkartei dokumentieren</DialogDescription>
        </DialogHeader>
        <div className="grid gap-3">
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Schlag</Label>
              <NativeSelect value={form.schlagId} onValueChange={v => setForm(p => ({ ...p, schlagId: v }))} placeholder="Schlag waehlen" options={[{ value: '', label: 'Kein Schlag' }, ...schlaege.map((s) => ({ value: s.id, label: s.name }))]} />
            </div>
            <div className="space-y-1">
              <Label>Datum *</Label>
              <Input type="date" value={form.datum} onChange={e => setForm(p => ({ ...p, datum: e.target.value }))} />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Maßnahme-Typ *</Label>
              <NativeSelect value={form.typ} onValueChange={v => setForm(p => ({ ...p, typ: v }))} options={Object.entries(typConfig).map(([key, cfg]) => ({ value: key, label: cfg.label }))} />
            </div>
            <div className="space-y-1">
              <Label>Mittel / Produkt</Label>
              <Input value={form.mittel} onChange={e => setForm(p => ({ ...p, mittel: e.target.value }))} placeholder="z.B. Roundup PowerFlex" />
            </div>
          </div>
          <div className="grid grid-cols-3 gap-3">
            <div className="space-y-1">
              <Label>Menge</Label>
              <Input type="number" step="0.1" value={form.menge} onChange={e => setForm(p => ({ ...p, menge: e.target.value }))} placeholder="3.5" />
            </div>
            <div className="space-y-1">
              <Label>Einheit</Label>
              <NativeSelect value={form.einheit} onValueChange={v => setForm(p => ({ ...p, einheit: v }))} options={['l/ha', 'kg/ha', 'ml/ha', 'g/ha', 't/ha', 'Stueck/ha'].map((e) => ({ value: e, label: e }))} />
            </div>
            <div className="space-y-1">
              <Label>Fläche (ha)</Label>
              <Input type="number" step="0.01" value={form.flaeche} onChange={e => setForm(p => ({ ...p, flaeche: e.target.value }))} placeholder="12.4" />
            </div>
          </div>
          <div className="grid grid-cols-2 gap-3">
            <div className="space-y-1">
              <Label>Anwender</Label>
              <Input value={form.anwender} onChange={e => setForm(p => ({ ...p, anwender: e.target.value }))} placeholder="Eigenleistung" />
            </div>
            <div className="space-y-1">
              <Label>Bemerkung</Label>
              <Input value={form.bemerkung} onChange={e => setForm(p => ({ ...p, bemerkung: e.target.value }))} />
            </div>
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" onClick={() => onOpenChange(false)}>Abbrechen</Button>
          <Button onClick={handleSubmit} disabled={!form.datum || !form.typ || createMassnahme.isPending}>
            {createMassnahme.isPending ? 'Speichern…' : 'Maßnahme erfassen'}
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
            <CheckCircle2 className="h-4 w-4 text-emerald-600" />
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
              <CheckCircle2 className="h-4 w-4 text-emerald-600" />
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
              />
              <Button
                variant="outline"
                className="mt-3 gap-2"
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
  const [activeTab, setActiveTab] = useState('schlaege')
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedSchlag, setSelectedSchlag] = useState<string>('alle')
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [showImportDialog, setShowImportDialog] = useState(false)
  const [showSchlagDialog, setShowSchlagDialog] = useState(false)
  const [showMassnahmeDialog, setShowMassnahmeDialog] = useState(false)

  const { data: schlaege = [], isLoading: loadingSchlaege, isError: errSchlaege, error: errSchlaegObj, refetch: refetchSchlaege } = usePortalFeldbuchSchlaege()
  const { data: massnahmen = [], isLoading: loadingMassnahmen, isError: errMassnahmen, error: errMassnahmenObj } = usePortalFeldbuchMassnahmen()
  const { data: stats } = usePortalFeldbuchStats()

  const isLoading = loadingSchlaege || loadingMassnahmen
  const isError = errSchlaege || errMassnahmen

  if (isLoading) return <FeldbuchSkeleton />
  if (isError) {
    return <ErrorState error={(errSchlaegObj ?? errMassnahmenObj) as Error} onRetry={() => { void refetchSchlaege() }} />
  }

  // Filter
  const filteredSchlaege = schlaege.filter(s =>
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    (s.kultur ?? '').toLowerCase().includes(searchTerm.toLowerCase()) ||
    (s.flik ?? '').toLowerCase().includes(searchTerm.toLowerCase())
  )

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

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Ackerschlagkartei</h1>
          <p className="text-muted-foreground">Ihre Schläge, dokumentierten Maßnahmen und VALEO-Dienstleistungen</p>
        </div>
        <div className="flex gap-2">
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

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
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
              <div className="rounded-lg bg-amber-100 p-2 text-amber-600">
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
            <Button size="sm" onClick={() => setShowSchlagDialog(true)} className="gap-1">
              <Plus className="h-4 w-4" />
              Schlag anlegen
            </Button>
          )}
          {activeTab === 'massnahmen' && (
            <Button size="sm" onClick={() => setShowMassnahmeDialog(true)} className="gap-1">
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
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredSchlaege.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground py-8">
                      {schlaege.length === 0
                        ? 'Noch keine Schläge angelegt. Klicken Sie auf "Schlag anlegen".'
                        : 'Keine Schläge gefunden'}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredSchlaege.map(schlag => (
                    <TableRow key={schlag.id}>
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
                    </TableRow>
                  ))
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
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredMassnahmen.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={8} className="text-center text-muted-foreground py-8">
                      {massnahmen.length === 0
                        ? 'Noch keine Maßnahmen dokumentiert.'
                        : 'Keine Maßnahmen gefunden'}
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredMassnahmen.map(m => (
                    <TableRow key={m.id}>
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
                        {m.typ === 'psm' && !m.compliant && (
                          <Badge className="bg-red-100 text-red-800 gap-1">
                            <AlertTriangle className="h-3 w-3" />
                            Prüfen
                          </Badge>
                        )}
                      </TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>
      </Tabs>

      {/* Dialoge */}
      <SchlagAnlegenDialog open={showSchlagDialog} onOpenChange={setShowSchlagDialog} />
      <MassnahmeDialog open={showMassnahmeDialog} onOpenChange={setShowMassnahmeDialog} schlaege={schlaege} />
      <ExportDialog open={showExportDialog} onOpenChange={setShowExportDialog} schlaege={schlaege} />
      <ImportDialog open={showImportDialog} onOpenChange={setShowImportDialog} />
    </div>
  )
}
