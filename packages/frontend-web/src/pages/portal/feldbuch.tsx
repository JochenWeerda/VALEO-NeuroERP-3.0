/**
 * Kundenportal - Ackerschlagkartei / Feldbuch
 * 
 * Kunden können ihre Feldbu-Daten einsehen und CSV exportieren/importieren
 */

import { useState, useEffect, useRef } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import {
  Search,
  Download,
  Upload,
  Leaf,
  MapPin,
  Calendar,
  FileSpreadsheet,
  Info,
  CheckCircle2,
  AlertCircle,
  Droplets,
  Bug,
  Eye,
  FileDown,
  FileUp,
  Sprout,
} from 'lucide-react'

interface Schlag {
  id: string
  name: string
  flaeche: number
  kultur: string
  flik: string
  gemeinde: string
  gemarkung: string
}

interface Massnahme {
  id: string
  schlagId: string
  schlagName: string
  datum: string
  typ: 'duengung' | 'psm' | 'aussaat' | 'ernte' | 'bodenbearbeitung'
  bezeichnung: string
  mittel?: string
  menge?: number
  einheit?: string
  anwender?: string
  bemerkung?: string
}

const mockSchlaege: Schlag[] = [
  { id: '1', name: 'Großer Acker', flaeche: 12.5, kultur: 'Winterweizen', flik: 'DENI0123456789', gemeinde: 'Musterstadt', gemarkung: 'Flur 1' },
  { id: '2', name: 'Hinteres Feld', flaeche: 8.3, kultur: 'Wintergerste', flik: 'DENI0123456790', gemeinde: 'Musterstadt', gemarkung: 'Flur 2' },
  { id: '3', name: 'Waldstück', flaeche: 5.2, kultur: 'Mais', flik: 'DENI0123456791', gemeinde: 'Musterstadt', gemarkung: 'Flur 3' },
  { id: '4', name: 'Wiese am Bach', flaeche: 6.8, kultur: 'Grünland', flik: 'DENI0123456792', gemeinde: 'Musterdorf', gemarkung: 'Flur 1' },
]

const mockMassnahmen: Massnahme[] = [
  { id: '1', schlagId: '1', schlagName: 'Großer Acker', datum: '2024-11-15', typ: 'duengung', bezeichnung: 'N-Düngung Herbst', mittel: 'AHL 28%', menge: 150, einheit: 'l/ha', anwender: 'VALEO GmbH' },
  { id: '2', schlagId: '1', schlagName: 'Großer Acker', datum: '2024-10-20', typ: 'psm', bezeichnung: 'Herbizidbehandlung', mittel: 'Atlantis Flex', menge: 1.5, einheit: 'l/ha', anwender: 'VALEO GmbH' },
  { id: '3', schlagId: '1', schlagName: 'Großer Acker', datum: '2024-10-05', typ: 'aussaat', bezeichnung: 'Winterweizen Aussaat', mittel: 'WW Reform', menge: 180, einheit: 'kg/ha' },
  { id: '4', schlagId: '2', schlagName: 'Hinteres Feld', datum: '2024-11-10', typ: 'duengung', bezeichnung: 'Grunddüngung', mittel: 'NPK 15-15-15', menge: 300, einheit: 'kg/ha', anwender: 'VALEO GmbH' },
  { id: '5', schlagId: '3', schlagName: 'Waldstück', datum: '2024-09-25', typ: 'ernte', bezeichnung: 'Maisernte', bemerkung: 'Ertrag: 45 t/ha' },
  { id: '6', schlagId: '2', schlagName: 'Hinteres Feld', datum: '2024-09-20', typ: 'aussaat', bezeichnung: 'Wintergerste Aussaat', mittel: 'Hyvido', menge: 1.5, einheit: 'Einheiten/ha' },
]

const typConfig: Record<string, { label: string; icon: React.ReactNode; color: string }> = {
  'duengung': { label: 'Düngung', icon: <Droplets className="h-4 w-4" />, color: 'bg-blue-100 text-blue-800' },
  'psm': { label: 'Pflanzenschutz', icon: <Bug className="h-4 w-4" />, color: 'bg-amber-100 text-amber-800' },
  'aussaat': { label: 'Aussaat', icon: <Sprout className="h-4 w-4" />, color: 'bg-emerald-100 text-emerald-800' },
  'ernte': { label: 'Ernte', icon: <Leaf className="h-4 w-4" />, color: 'bg-yellow-100 text-yellow-800' },
  'bodenbearbeitung': { label: 'Bodenbearbeitung', icon: <MapPin className="h-4 w-4" />, color: 'bg-gray-100 text-gray-800' },
}

export default function PortalFeldbuch() {
  const [loading, setLoading] = useState(true)
  const [schlaege, setSchlaege] = useState<Schlag[]>([])
  const [massnahmen, setMassnahmen] = useState<Massnahme[]>([])
  const [searchTerm, setSearchTerm] = useState('')
  const [activeTab, setActiveTab] = useState('schlaege')
  const [selectedSchlag, setSelectedSchlag] = useState<string>('alle')
  const [showExportDialog, setShowExportDialog] = useState(false)
  const [showImportDialog, setShowImportDialog] = useState(false)
  const [importSuccess, setImportSuccess] = useState(false)
  const [exportSuccess, setExportSuccess] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    const timer = setTimeout(() => {
      setSchlaege(mockSchlaege)
      setMassnahmen(mockMassnahmen)
      setLoading(false)
    }, 500)
    return () => clearTimeout(timer)
  }, [])

  const filteredSchlaege = schlaege.filter((s) =>
    s.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.kultur.toLowerCase().includes(searchTerm.toLowerCase()) ||
    s.flik.toLowerCase().includes(searchTerm.toLowerCase())
  )

  const filteredMassnahmen = massnahmen.filter((m) => {
    const matchesSearch = m.bezeichnung.toLowerCase().includes(searchTerm.toLowerCase()) ||
      m.schlagName.toLowerCase().includes(searchTerm.toLowerCase())
    const matchesSchlag = selectedSchlag === 'alle' || m.schlagId === selectedSchlag
    return matchesSearch && matchesSchlag
  })

  const gesamtFlaeche = schlaege.reduce((sum, s) => sum + s.flaeche, 0)

  const generateCSV = (data: any[], filename: string) => {
    // Generate CSV content
    const headers = Object.keys(data[0] || {}).join(';')
    const rows = data.map(item => Object.values(item).join(';')).join('\n')
    const csv = `${headers}\n${rows}`
    
    // Create download
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = filename
    link.click()
    URL.revokeObjectURL(url)
  }

  const handleExportSchlaege = () => {
    const exportData = schlaege.map(s => ({
      Name: s.name,
      'Fläche (ha)': s.flaeche,
      Kultur: s.kultur,
      FLIK: s.flik,
      Gemeinde: s.gemeinde,
      Gemarkung: s.gemarkung,
    }))
    generateCSV(exportData, `schlaege_export_${new Date().toISOString().split('T')[0]}.csv`)
    setExportSuccess(true)
    setTimeout(() => setExportSuccess(false), 3000)
  }

  const handleExportMassnahmen = () => {
    const exportData = massnahmen.map(m => ({
      Datum: m.datum,
      Schlag: m.schlagName,
      Typ: typConfig[m.typ]?.label || m.typ,
      Bezeichnung: m.bezeichnung,
      Mittel: m.mittel || '',
      Menge: m.menge || '',
      Einheit: m.einheit || '',
      Anwender: m.anwender || '',
      Bemerkung: m.bemerkung || '',
    }))
    generateCSV(exportData, `massnahmen_export_${new Date().toISOString().split('T')[0]}.csv`)
    setExportSuccess(true)
    setTimeout(() => setExportSuccess(false), 3000)
  }

  const handleImport = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      // TODO: Parse CSV and import data
      setImportSuccess(true)
      setTimeout(() => {
        setShowImportDialog(false)
        setImportSuccess(false)
      }, 2000)
    }
  }

  if (loading) {
    return <FeldbuchSkeleton />
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold">Ackerschlagkartei</h1>
          <p className="text-muted-foreground">Ihre Schläge und dokumentierte Maßnahmen</p>
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

      {/* Export Success Alert */}
      {exportSuccess && (
        <Alert className="border-emerald-200 bg-emerald-50">
          <CheckCircle2 className="h-4 w-4 text-emerald-600" />
          <AlertTitle className="text-emerald-800">Export erfolgreich</AlertTitle>
          <AlertDescription className="text-emerald-700">
            Die CSV-Datei wurde heruntergeladen.
          </AlertDescription>
        </Alert>
      )}

      {/* KPIs */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-emerald-100 p-2 text-emerald-600">
                <MapPin className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">{schlaege.length}</p>
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
                <p className="text-2xl font-bold">{massnahmen.length}</p>
                <p className="text-sm text-muted-foreground">Maßnahmen</p>
              </div>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-purple-100 p-2 text-purple-600">
                <Droplets className="h-5 w-5" />
              </div>
              <div>
                <p className="text-2xl font-bold">
                  {massnahmen.filter(m => m.anwender === 'VALEO GmbH').length}
                </p>
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
            placeholder="Suchen..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="pl-9"
          />
        </div>
        {activeTab === 'massnahmen' && (
          <Select value={selectedSchlag} onValueChange={setSelectedSchlag}>
            <SelectTrigger className="w-[200px]">
              <SelectValue placeholder="Schlag wählen" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="alle">Alle Schläge</SelectItem>
              {schlaege.map((s) => (
                <SelectItem key={s.id} value={s.id}>{s.name}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        )}
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab}>
        <TabsList>
          <TabsTrigger value="schlaege">Schläge</TabsTrigger>
          <TabsTrigger value="massnahmen">Maßnahmen</TabsTrigger>
        </TabsList>

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
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredSchlaege.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={5} className="text-center text-muted-foreground">
                      Keine Schläge gefunden
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredSchlaege.map((schlag) => (
                    <TableRow key={schlag.id}>
                      <TableCell className="font-medium">{schlag.name}</TableCell>
                      <TableCell>
                        <Badge variant="secondary">{schlag.kultur}</Badge>
                      </TableCell>
                      <TableCell className="text-right">{schlag.flaeche.toFixed(2)} ha</TableCell>
                      <TableCell className="font-mono text-sm">{schlag.flik}</TableCell>
                      <TableCell>{schlag.gemeinde}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </Card>
        </TabsContent>

        <TabsContent value="massnahmen" className="mt-4">
          <Card>
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Datum</TableHead>
                  <TableHead>Schlag</TableHead>
                  <TableHead>Typ</TableHead>
                  <TableHead>Bezeichnung</TableHead>
                  <TableHead>Mittel/Menge</TableHead>
                  <TableHead>Anwender</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredMassnahmen.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={6} className="text-center text-muted-foreground">
                      Keine Maßnahmen gefunden
                    </TableCell>
                  </TableRow>
                ) : (
                  filteredMassnahmen.map((massnahme) => {
                    const typ = typConfig[massnahme.typ]
                    return (
                      <TableRow key={massnahme.id}>
                        <TableCell>{massnahme.datum}</TableCell>
                        <TableCell className="font-medium">{massnahme.schlagName}</TableCell>
                        <TableCell>
                          <Badge className={`${typ.color} gap-1`}>
                            {typ.icon}
                            {typ.label}
                          </Badge>
                        </TableCell>
                        <TableCell>{massnahme.bezeichnung}</TableCell>
                        <TableCell>
                          {massnahme.mittel && massnahme.menge && (
                            <span>{massnahme.mittel} - {massnahme.menge} {massnahme.einheit}</span>
                          )}
                          {massnahme.bemerkung && !massnahme.mittel && (
                            <span className="text-muted-foreground">{massnahme.bemerkung}</span>
                          )}
                        </TableCell>
                        <TableCell>
                          {massnahme.anwender ? (
                            <Badge variant="outline" className="text-emerald-700 border-emerald-300 bg-emerald-50">
                              {massnahme.anwender}
                            </Badge>
                          ) : (
                            <span className="text-muted-foreground">-</span>
                          )}
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

      {/* Export Dialog */}
      <Dialog open={showExportDialog} onOpenChange={setShowExportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileDown className="h-5 w-5" />
              Daten exportieren
            </DialogTitle>
            <DialogDescription>
              Exportieren Sie Ihre Ackerschlagkartei als CSV-Datei
            </DialogDescription>
          </DialogHeader>

          <div className="space-y-4">
            <Button 
              onClick={handleExportSchlaege} 
              variant="outline" 
              className="w-full justify-start gap-3 h-auto py-4"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-emerald-100">
                <MapPin className="h-5 w-5 text-emerald-600" />
              </div>
              <div className="text-left">
                <p className="font-medium">Schläge exportieren</p>
                <p className="text-sm text-muted-foreground">Alle {schlaege.length} Schläge als CSV</p>
              </div>
            </Button>

            <Button 
              onClick={handleExportMassnahmen} 
              variant="outline" 
              className="w-full justify-start gap-3 h-auto py-4"
            >
              <div className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-100">
                <Calendar className="h-5 w-5 text-blue-600" />
              </div>
              <div className="text-left">
                <p className="font-medium">Maßnahmen exportieren</p>
                <p className="text-sm text-muted-foreground">Alle {massnahmen.length} Maßnahmen als CSV</p>
              </div>
            </Button>
          </div>

          <DialogFooter>
            <Button variant="outline" onClick={() => setShowExportDialog(false)}>
              Schließen
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Import Dialog */}
      <Dialog open={showImportDialog} onOpenChange={setShowImportDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle className="flex items-center gap-2">
              <FileUp className="h-5 w-5" />
              Daten importieren
            </DialogTitle>
            <DialogDescription>
              Importieren Sie Schläge oder Maßnahmen aus einer CSV-Datei
            </DialogDescription>
          </DialogHeader>

          {importSuccess ? (
            <div className="flex flex-col items-center gap-4 py-8">
              <div className="flex h-16 w-16 items-center justify-center rounded-full bg-emerald-100">
                <CheckCircle2 className="h-8 w-8 text-emerald-600" />
              </div>
              <div className="text-center">
                <h3 className="text-lg font-semibold">Import erfolgreich!</h3>
                <p className="text-muted-foreground">Die Daten wurden importiert.</p>
              </div>
            </div>
          ) : (
            <>
              <Alert>
                <Info className="h-4 w-4" />
                <AlertTitle>CSV-Format</AlertTitle>
                <AlertDescription>
                  Die CSV-Datei muss im Standardformat vorliegen. 
                  Exportieren Sie zuerst Ihre bestehenden Daten als Vorlage.
                </AlertDescription>
              </Alert>

              <div className="space-y-4">
                <div className="rounded-lg border-2 border-dashed p-8 text-center">
                  <FileSpreadsheet className="mx-auto h-12 w-12 text-muted-foreground" />
                  <p className="mt-2 text-sm text-muted-foreground">
                    Ziehen Sie eine CSV-Datei hierher oder
                  </p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    onChange={handleImport}
                    className="hidden"
                  />
                  <Button
                    variant="outline"
                    className="mt-2"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    Datei auswählen
                  </Button>
                </div>
              </div>

              <DialogFooter>
                <Button variant="outline" onClick={() => setShowImportDialog(false)}>
                  Abbrechen
                </Button>
              </DialogFooter>
            </>
          )}
        </DialogContent>
      </Dialog>
    </div>
  )
}

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
          <Card key={i}>
            <CardContent className="p-4">
              <Skeleton className="h-12 w-full" />
            </CardContent>
          </Card>
        ))}
      </div>
      <Skeleton className="h-10 w-full" />
      <Card>
        <CardContent className="p-4 space-y-3">
          {[...Array(5)].map((_, i) => (
            <Skeleton key={i} className="h-12 w-full" />
          ))}
        </CardContent>
      </Card>
    </div>
  )
}

