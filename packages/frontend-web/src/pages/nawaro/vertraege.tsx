import { useEffect, useMemo, useState } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Checkbox } from '@/components/ui/checkbox'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { useToast } from '@/hooks/use-toast'
import { Plus, Save, Trash2 } from 'lucide-react'
import {
  createContractSheet,
  deleteContractSheet,
  listContractSheets,
  updateContractSheet,
} from '@/lib/api/nawaro'

type ContractRow = {
  id: number
  vertragsNr: string
  kundenname: string
  name1: string
  gesFlaeche: string
  standardMenge: string
  anzLief: string
  liefermittel: string
  mengeB: string
  ernteerklaerung: string
}

function emptyRow(id: number): ContractRow {
  return {
    id,
    vertragsNr: '',
    kundenname: '',
    name1: '',
    gesFlaeche: '',
    standardMenge: '',
    anzLief: '',
    liefermittel: '',
    mengeB: '',
    ernteerklaerung: '',
  }
}

export default function NaWaRoVertraegePage(): JSX.Element {
  const { toast } = useToast()
  const queryClient = useQueryClient()

  const [selectedId, setSelectedId] = useState<string>('')
  const [erntejahr, setErntejahr] = useState<number>(2025)
  const [artikelNr, setArtikelNr] = useState<string>('')
  const [sommer, setSommer] = useState<boolean>(true)
  const [winter, setWinter] = useState<boolean>(false)
  const [rows, setRows] = useState<ContractRow[]>([emptyRow(1)])

  const sheetsQuery = useQuery({
    queryKey: ['nawaro', 'contract-sheets'],
    queryFn: listContractSheets,
  })

  useEffect(() => {
    if (!sheetsQuery.data || sheetsQuery.data.length === 0 || selectedId) {
      return
    }
    const latest = sheetsQuery.data[0]
    loadSheet(latest.id)
  }, [sheetsQuery.data, selectedId])

  const totalArea = useMemo(
    () => rows.reduce((sum, row) => sum + (Number(row.gesFlaeche.replace(',', '.')) || 0), 0),
    [rows],
  )

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        harvest_year: erntejahr,
        article_number: artikelNr || null,
        is_summer: sommer,
        is_winter: winter,
        rows: rows.map((row) => ({
          contract_number: row.vertragsNr || null,
          customer_name: row.kundenname || null,
          name_1: row.name1 || null,
          total_area: row.gesFlaeche || null,
          standard_quantity: row.standardMenge || null,
          delivery_count: row.anzLief ? Number(row.anzLief) : null,
          delivery_resource: row.liefermittel || null,
          quantity_b: row.mengeB || null,
          harvest_declaration: row.ernteerklaerung || null,
        })),
      }
      if (selectedId) {
        return updateContractSheet(selectedId, payload)
      }
      return createContractSheet(payload)
    },
    onSuccess: (saved) => {
      setSelectedId(saved.id)
      toast({ title: 'NaWaRo-Vertraege gespeichert', description: `${saved.rows.length} Positionen` })
      void queryClient.invalidateQueries({ queryKey: ['nawaro', 'contract-sheets'] })
    },
  })

  const deleteMutation = useMutation({
    mutationFn: async () => {
      if (!selectedId) {
        return
      }
      await deleteContractSheet(selectedId)
    },
    onSuccess: () => {
      clearForm()
      toast({ title: 'Datensatz geloescht' })
      void queryClient.invalidateQueries({ queryKey: ['nawaro', 'contract-sheets'] })
    },
  })

  function loadSheet(sheetId: string): void {
    const sheet = sheetsQuery.data?.find((entry) => entry.id === sheetId)
    if (!sheet) {
      return
    }
    setSelectedId(sheet.id)
    setErntejahr(sheet.harvest_year)
    setArtikelNr(sheet.article_number ?? '')
    setSommer(sheet.is_summer)
    setWinter(sheet.is_winter)
    setRows(
      sheet.rows.length > 0
        ? sheet.rows.map((row, idx) => ({
            id: idx + 1,
            vertragsNr: row.contract_number ?? '',
            kundenname: row.customer_name ?? '',
            name1: row.name_1 ?? '',
            gesFlaeche: row.total_area ?? '',
            standardMenge: row.standard_quantity ?? '',
            anzLief: row.delivery_count != null ? String(row.delivery_count) : '',
            liefermittel: row.delivery_resource ?? '',
            mengeB: row.quantity_b ?? '',
            ernteerklaerung: row.harvest_declaration ?? '',
          }))
        : [emptyRow(1)],
    )
  }

  function clearForm(): void {
    setSelectedId('')
    setErntejahr(2025)
    setArtikelNr('')
    setSommer(true)
    setWinter(false)
    setRows([emptyRow(1)])
  }

  function addRow(): void {
    setRows((prev) => [...prev, emptyRow(prev.length ? Math.max(...prev.map((r) => r.id)) + 1 : 1)])
  }

  function removeRow(id: number): void {
    setRows((prev) => (prev.length > 1 ? prev.filter((row) => row.id !== id) : prev))
  }

  function updateRow(id: number, field: keyof Omit<ContractRow, 'id'>, value: string): void {
    setRows((prev) => prev.map((row) => (row.id === id ? { ...row, [field]: value } : row)))
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">NaWaRo-Vertraege</h1>
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
              {sheet.harvest_year} {sheet.article_number ?? '-'}
            </Button>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Filter und Kopfdaten</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-4 md:grid-cols-3">
          <div className="space-y-2">
            <Label htmlFor="erntejahr">Erntejahr</Label>
            <Input id="erntejahr" type="number" min={2000} max={2100} value={erntejahr} onChange={(e) => setErntejahr(Number(e.target.value) || 0)} />
          </div>
          <div className="space-y-2">
            <Label htmlFor="artikelNr">Artikel-Nr.</Label>
            <Input id="artikelNr" value={artikelNr} onChange={(e) => setArtikelNr(e.target.value)} />
          </div>
          <div className="space-y-2">
            <Label>Saison</Label>
            <div className="flex gap-6 pt-2 text-sm">
              <label className="flex items-center gap-2">
                <Checkbox checked={sommer} onCheckedChange={(checked) => setSommer(checked === true)} />Sommer
              </label>
              <label className="flex items-center gap-2">
                <Checkbox checked={winter} onCheckedChange={(checked) => setWinter(checked === true)} />Winter
              </label>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader className="flex flex-row items-center justify-between">
          <CardTitle>Vertragspositionen</CardTitle>
          <Button variant="outline" size="sm" className="gap-2" onClick={addRow}>
            <Plus className="h-4 w-4" />Zeile
          </Button>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Vertrag-Nr.</TableHead>
                  <TableHead>Kundenname</TableHead>
                  <TableHead>Name 1</TableHead>
                  <TableHead>Ges. Flaeche</TableHead>
                  <TableHead>Standard-Menge</TableHead>
                  <TableHead>Anz. Lief.</TableHead>
                  <TableHead>Liefermittel</TableHead>
                  <TableHead>Menge B.</TableHead>
                  <TableHead>Ernteerklaerung</TableHead>
                  <TableHead className="w-12" />
                </TableRow>
              </TableHeader>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.id}>
                    <TableCell><Input value={row.vertragsNr} onChange={(e) => updateRow(row.id, 'vertragsNr', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.kundenname} onChange={(e) => updateRow(row.id, 'kundenname', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.name1} onChange={(e) => updateRow(row.id, 'name1', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.gesFlaeche} onChange={(e) => updateRow(row.id, 'gesFlaeche', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.standardMenge} onChange={(e) => updateRow(row.id, 'standardMenge', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.anzLief} onChange={(e) => updateRow(row.id, 'anzLief', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.liefermittel} onChange={(e) => updateRow(row.id, 'liefermittel', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.mengeB} onChange={(e) => updateRow(row.id, 'mengeB', e.target.value)} /></TableCell>
                    <TableCell><Input value={row.ernteerklaerung} onChange={(e) => updateRow(row.id, 'ernteerklaerung', e.target.value)} /></TableCell>
                    <TableCell>
                      <Button variant="ghost" size="icon" onClick={() => removeRow(row.id)}><Trash2 className="h-4 w-4" /></Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6 text-sm">
          Summen Flaechen: <span className="font-semibold">{totalArea.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}</span>
        </CardContent>
      </Card>

      <div className="flex gap-2">
        <Button className="gap-2" onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending}><Save className="h-4 w-4" />Speichern</Button>
        <Button variant="destructive" className="gap-2" onClick={() => deleteMutation.mutate()} disabled={!selectedId || deleteMutation.isPending}><Trash2 className="h-4 w-4" />Loeschen</Button>
      </div>
    </div>
  )
}
