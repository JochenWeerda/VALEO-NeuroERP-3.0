import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useToast } from '@/hooks/use-toast'
import { FileText, Plus, Printer, Save, Trash2 } from 'lucide-react'
import { createAreaSheet, deleteAreaSheet, listAreaSheets, updateAreaSheet } from '@/lib/api/nawaro'

type AreaRow = {
  id: number
  kundenname: string
  name1: string
  name2: string
  plz: string
  ort: string
  telefon: string
  telefax: string
  flaeche2022: string
  flaeche2023: string
  flaeche2024: string
  flaeche2025: string
  flaeche2026: string
}

const yearFields: Array<keyof Pick<AreaRow, 'flaeche2022' | 'flaeche2023' | 'flaeche2024' | 'flaeche2025' | 'flaeche2026'>> = [
  'flaeche2022',
  'flaeche2023',
  'flaeche2024',
  'flaeche2025',
  'flaeche2026',
]

function emptyRow(id: number): AreaRow {
  return {
    id,
    kundenname: '',
    name1: '',
    name2: '',
    plz: '',
    ort: '',
    telefon: '',
    telefax: '',
    flaeche2022: '',
    flaeche2023: '',
    flaeche2024: '',
    flaeche2025: '',
    flaeche2026: '',
  }
}

export default function NaWaRoAnbauflaechenPage(): JSX.Element {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const [selectedId, setSelectedId] = useState<string>('')
  const [erntejahrVon, setErntejahrVon] = useState<number>(2022)
  const [erntejahrBis, setErntejahrBis] = useState<number>(2026)
  const [artikelNr, setArtikelNr] = useState<string>('')
  const [sommer, setSommer] = useState<boolean>(true)
  const [winter, setWinter] = useState<boolean>(false)
  const [formular, setFormular] = useState<string>('W12071')
  const [rows, setRows] = useState<AreaRow[]>([emptyRow(1)])

  const sheetsQuery = useQuery({
    queryKey: ['nawaro', 'area-sheets'],
    queryFn: listAreaSheets,
  })

  useEffect(() => {
    if (!sheetsQuery.data || sheetsQuery.data.length === 0 || selectedId) {
      return
    }
    loadSheet(sheetsQuery.data[0].id)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [sheetsQuery.data, selectedId])

  const sums = useMemo(() => {
    return yearFields.reduce<Record<string, number>>((acc, field) => {
      acc[field] = rows.reduce((sum, row) => sum + (Number(row[field].replace(',', '.')) || 0), 0)
      return acc
    }, {})
  }, [rows])

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        harvest_year_from: erntejahrVon,
        harvest_year_to: erntejahrBis,
        article_number: artikelNr || null,
        is_summer: sommer,
        is_winter: winter,
        form_code: formular,
        rows: rows.map((row) => ({
          customer_name: row.kundenname || null,
          name_1: row.name1 || null,
          name_2: row.name2 || null,
          postal_code: row.plz || null,
          city: row.ort || null,
          phone: row.telefon || null,
          fax: row.telefax || null,
          area_2022: row.flaeche2022 || null,
          area_2023: row.flaeche2023 || null,
          area_2024: row.flaeche2024 || null,
          area_2025: row.flaeche2025 || null,
          area_2026: row.flaeche2026 || null,
        })),
      }
      if (selectedId) {
        return updateAreaSheet(selectedId, payload)
      }
      return createAreaSheet(payload)
    },
    onSuccess: (saved) => {
      setSelectedId(saved.id)
      toast({ title: 'NaWaRo-Anbauflaechen gespeichert', description: `${saved.rows.length} Positionen` })
      void queryClient.invalidateQueries({ queryKey: ['nawaro', 'area-sheets'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async () => {
      if (!selectedId) {
        return
      }
      await deleteAreaSheet(selectedId)
    },
    onSuccess: () => {
      clearForm()
      toast({ title: 'Datensatz geloescht' })
      void queryClient.invalidateQueries({ queryKey: ['nawaro', 'area-sheets'] })
    },
  })

  function loadSheet(sheetId: string): void {
    const sheet = sheetsQuery.data?.find((entry) => entry.id === sheetId)
    if (!sheet) {
      return
    }
    setSelectedId(sheet.id)
    setErntejahrVon(sheet.harvest_year_from)
    setErntejahrBis(sheet.harvest_year_to)
    setArtikelNr(sheet.article_number ?? '')
    setSommer(sheet.is_summer)
    setWinter(sheet.is_winter)
    setFormular(sheet.form_code)
    setRows(
      sheet.rows.length > 0
        ? sheet.rows.map((row, idx) => ({
            id: idx + 1,
            kundenname: row.customer_name ?? '',
            name1: row.name_1 ?? '',
            name2: row.name_2 ?? '',
            plz: row.postal_code ?? '',
            ort: row.city ?? '',
            telefon: row.phone ?? '',
            telefax: row.fax ?? '',
            flaeche2022: row.area_2022 ?? '',
            flaeche2023: row.area_2023 ?? '',
            flaeche2024: row.area_2024 ?? '',
            flaeche2025: row.area_2025 ?? '',
            flaeche2026: row.area_2026 ?? '',
          }))
        : [emptyRow(1)],
    )
  }

  function clearForm(): void {
    setSelectedId('')
    setErntejahrVon(2022)
    setErntejahrBis(2026)
    setArtikelNr('')
    setSommer(true)
    setWinter(false)
    setFormular('W12071')
    setRows([emptyRow(1)])
  }

  function updateRow(id: number, field: keyof Omit<AreaRow, 'id'>, value: string): void {
    setRows((prev) => prev.map((row) => (row.id === id ? { ...row, [field]: value } : row)))
  }

  function addRow(): void {
    setRows((prev) => [...prev, emptyRow(prev.length ? Math.max(...prev.map((r) => r.id)) + 1 : 1)])
  }

  function removeRow(id: number): void {
    setRows((prev) => (prev.length > 1 ? prev.filter((row) => row.id !== id) : prev))
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">NaWaRo-Anbauflaechen</h1>
        <p className="text-muted-foreground">CRUD + DB angebunden</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Gespeicherte Datensaetze</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-2">
          <Button variant="outline" size="sm" onClick={clearForm}>Neu</Button>
          {(sheetsQuery.data ?? []).map((sheet) => (
            <Button key={sheet.id} variant={sheet.id === selectedId ? 'default' : 'outline'} size="sm" onClick={() => loadSheet(sheet.id)}>
              {sheet.harvest_year_from}-{sheet.harvest_year_to} {sheet.form_code}
            </Button>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Filter</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 lg:grid-cols-5">
          <div className="space-y-2">
            <Label htmlFor="erntejahrVon">Erntejahr von</Label>
            <Input id="erntejahrVon" type="number" value={erntejahrVon} onChange={(e) => setErntejahrVon(Number(e.target.value) || 0)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="erntejahrBis">Erntejahr bis</Label>
            <Input id="erntejahrBis" type="number" value={erntejahrBis} onChange={(e) => setErntejahrBis(Number(e.target.value) || 0)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="artikelNr">Artikel-Nr.</Label>
            <Input id="artikelNr" value={artikelNr} onChange={(e) => setArtikelNr(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Saison</Label>
            <div className="flex gap-4 pt-2 text-sm">
              <label className="flex items-center gap-2">
                <Checkbox checked={sommer} onCheckedChange={(checked) => setSommer(checked === true)} />Sommer
              </label>
              <label className="flex items-center gap-2">
                <Checkbox checked={winter} onCheckedChange={(checked) => setWinter(checked === true)} />Winter
              </label>
            </div>
          </div>
          <div className="space-y-2">
            <Label htmlFor="formular">Formular</Label>
            <Input id="formular" value={formular} onChange={(e) => setFormular(e.target.value)} />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Anbauflaechen</CardTitle>
          <Button variant="outline" size="sm" className="gap-2" onClick={addRow}><Plus className="h-4 w-4" />Zeile</Button>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Kundenname</TableHead>
                  <TableHead>Name 1</TableHead>
                  <TableHead>Name 2</TableHead>
                  <TableHead>PLZ</TableHead>
                  <TableHead>Ort</TableHead>
                  <TableHead>Telefon</TableHead>
                  <TableHead>Telefax</TableHead>
                  <TableHead>2022</TableHead>
                  <TableHead>2023</TableHead>
                  <TableHead>2024</TableHead>
                  <TableHead>2025</TableHead>
                  <TableHead>2026</TableHead>
                  <TableHead className="w-12" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell><Input value={row.kundenname} onChange={(e) => updateRow(row.id, 'kundenname', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.name1} onChange={(e) => updateRow(row.id, 'name1', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.name2} onChange={(e) => updateRow(row.id, 'name2', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.plz} onChange={(e) => updateRow(row.id, 'plz', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.ort} onChange={(e) => updateRow(row.id, 'ort', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.telefon} onChange={(e) => updateRow(row.id, 'telefon', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.telefax} onChange={(e) => updateRow(row.id, 'telefax', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.flaeche2022} onChange={(e) => updateRow(row.id, 'flaeche2022', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.flaeche2023} onChange={(e) => updateRow(row.id, 'flaeche2023', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.flaeche2024} onChange={(e) => updateRow(row.id, 'flaeche2024', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.flaeche2025} onChange={(e) => updateRow(row.id, 'flaeche2025', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.flaeche2026} onChange={(e) => updateRow(row.id, 'flaeche2026', e.target.value)} /></TableCell>
                    <TableCell><Button variant="ghost" size="icon" onClick={() => removeRow(row.id)}><Trash2 className="h-4 w-4" /></Button></TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6 text-sm">
          <div className="flex flex-wrap gap-4">
            <span>Summen Flaechen 2022: <strong>{(sums.flaeche2022 || 0).toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></span>
            <span>2023: <strong>{(sums.flaeche2023 || 0).toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></span>
            <span>2024: <strong>{(sums.flaeche2024 || 0).toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></span>
            <span>2025: <strong>{(sums.flaeche2025 || 0).toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></span>
            <span>2026: <strong>{(sums.flaeche2026 || 0).toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</strong></span>
          </div>
        </CardContent>
      </Card>

      <div className="flex flex-wrap gap-2">
        <Button variant="outline" className="gap-2" onClick={() => toast({ title: 'Druckjob erstellt' })}><Printer className="h-4 w-4" />Drucken</Button>
        <Button variant="outline" className="gap-2" onClick={() => toast({ title: 'Serienbrief erstellt' })}><FileText className="h-4 w-4" />Serienbrief erstellen</Button>
        <Button className="gap-2" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}><Save className="h-4 w-4" />Speichern</Button>
        <Button variant="destructive" className="gap-2" onClick={() => deleteMutation.mutate()} disabled={!selectedId || deleteMutation.isPending}><Trash2 className="h-4 w-4" />Loeschen</Button>
      </div>
    </div>
  )
}
