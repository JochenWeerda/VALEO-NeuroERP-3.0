/**
 * Frachtaufträge zu eingehenden Lieferscheinen
 * 1:1 Nachbau der zvoove FRACHTAUFTRÄGE-Maske
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Card } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select'
import { useToast } from '@/components/ui/toast-provider'
import { apiClient } from '@/lib/axios'
import { MoreHorizontal, RefreshCw, Truck, Eye, Calculator } from 'lucide-react'

type Frachtauftrag = {
  id: string
  belegart: string
  belegNr: string
  datum: string
  lieferTermin: string
  ladeDatum: string
  spedNr: string
  spedName: string
  eLiefSchNr: string
  frachtArtikel: string
  pauschalFracht: number
}

export default function FrachtauftraegeEingangPage(): JSX.Element {
  const navigate = useNavigate()
  const { push } = useToast()

  const today = (): string => {
    const d = new Date()
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-${String(d.getDate()).padStart(2, '0')}`
  }
  const firstOfYear = (): string => `${new Date().getFullYear()}-01-01`

  const [filterStatus, setFilterStatus] = useState('nicht-erzeugt')
  const [filterBelegart, setFilterBelegart] = useState('alle')
  const [filterNiederlassung, setFilterNiederlassung] = useState('')
  const [filterVon, setFilterVon] = useState(firstOfYear())
  const [filterBis, setFilterBis] = useState(today())
  const [filterSpedNr, setFilterSpedNr] = useState('')
  const [filterSpedName, setFilterSpedName] = useState('')
  const [filterKundenNr, setFilterKundenNr] = useState('')

  const [items, setItems] = useState<Frachtauftrag[]>([])
  const [selected, setSelected] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const loadData = async (): Promise<void> => {
    setLoading(true)
    try {
      const params: Record<string, string> = {
        liefer_termin_von: filterVon,
        liefer_termin_bis: filterBis,
      }
      if (filterNiederlassung) params['niederlassung'] = filterNiederlassung
      if (filterSpedNr) params['spediteur_nr'] = filterSpedNr
      if (filterKundenNr) params['kunden_nr'] = filterKundenNr

      const data = await apiClient.get<any[]>('/api/v1/einkauf/frachtauftraege', { params })
      setItems((data || []).map((r: any) => ({
        id: r.id,
        belegart: r.belegart || 'Lieferschein',
        belegNr: r.belegnummer || r.frachtauftrag_nr || '',
        datum: r.frachtauftrag_erzeugt?.substring(0, 10) || '',
        lieferTermin: r.liefertermin || '',
        ladeDatum: r.lade_datum || '',
        spedNr: r.spediteur_nr || '',
        spedName: r.spediteur_name || '',
        eLiefSchNr: r.e_lief_sch_nr || '',
        frachtArtikel: r.fracht_artikel || '',
        pauschalFracht: parseFloat(r.pauschal_fracht || '0'),
      })))
    } catch {
      setItems([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { void loadData() }, [])

  const selectedItem = items.find((i) => i.id === selected)

  return (
    <div className="h-screen flex flex-col bg-gray-50">
      <div className="bg-gray-700 text-white px-4 py-2">
        <h1 className="text-lg font-bold">FRACHTAUFTRÄGE</h1>
      </div>

      <div className="flex-1 overflow-auto p-4">
        {/* Filter-Bereich */}
        <Card className="mb-4 p-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-44 text-sm shrink-0">Filter:</Label>
                <Select value={filterStatus} onValueChange={setFilterStatus}>
                  <SelectTrigger className="flex-1 h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="nicht-erzeugt">Lieferschein nicht erzeugt</SelectItem>
                    <SelectItem value="alle-offen">Alle offenen</SelectItem>
                    <SelectItem value="erledigt">Erledigt</SelectItem>
                    <SelectItem value="alle">Alle</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-44 text-sm shrink-0">Belegart:</Label>
                <Select value={filterBelegart} onValueChange={setFilterBelegart}>
                  <SelectTrigger className="flex-1 h-8">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="alle">Alle Belege</SelectItem>
                    <SelectItem value="lieferschein">Lieferschein</SelectItem>
                    <SelectItem value="bestellung">Bestellung</SelectItem>
                  </SelectContent>
                </Select>
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-44 text-sm shrink-0">Niederlassung:</Label>
                <Input value={filterNiederlassung}
                  onChange={(e) => setFilterNiederlassung(e.target.value)}
                  className="flex-1 h-8" placeholder="Alle" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </div>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">Liefer-Termin von:</Label>
                <Input type="date" value={filterVon}
                  onChange={(e) => setFilterVon(e.target.value)}
                  className="flex-1 h-8" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">bis:</Label>
                <Input type="date" value={filterBis}
                  onChange={(e) => setFilterBis(e.target.value)}
                  className="flex-1 h-8" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">Spediteur-Nr.:</Label>
                <Input value={filterSpedNr}
                  onChange={(e) => setFilterSpedNr(e.target.value)}
                  className="w-24 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
                <Input value={filterSpedName}
                  onChange={(e) => setFilterSpedName(e.target.value)}
                  className="flex-1 h-8" placeholder="Spediteur-Name" />
              </div>
              <div className="flex items-center gap-2">
                <Label className="w-36 text-sm shrink-0">Kunden-Nr.:</Label>
                <Input value={filterKundenNr}
                  onChange={(e) => setFilterKundenNr(e.target.value)}
                  className="w-24 h-8" />
                <Button variant="ghost" size="sm" className="h-8 w-8 p-0">
                  <MoreHorizontal className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </div>
          <div className="mt-3 flex justify-end">
            <Button onClick={() => void loadData()} disabled={loading} size="sm" className="gap-2">
              <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Aufbereiten
            </Button>
          </div>
        </Card>

        {/* Frachtaufträge lt. Filter */}
        <Card className="mb-4 p-4">
          <h2 className="font-semibold text-sm mb-2">
            Frachtaufträge lt. Filter
            {items.length > 0 && <span className="text-muted-foreground font-normal ml-2">({items.length} Einträge)</span>}
          </h2>
          <div className="overflow-x-auto">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead className="w-28">Belegart</TableHead>
                  <TableHead className="w-32">Beleg-Nr. / Datum</TableHead>
                  <TableHead className="w-28">Liefer-Termin</TableHead>
                  <TableHead className="w-28">Lade-Datum</TableHead>
                  <TableHead className="w-24">Sped.-Nr.</TableHead>
                  <TableHead className="w-40">Sped.-Name</TableHead>
                  <TableHead className="w-32">E.-Lief.-Sch.-Nr.</TableHead>
                  <TableHead className="w-40">Fracht-Artikel</TableHead>
                  <TableHead className="w-28">Pauschal-Fracht</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.length === 0 && !loading && (
                  <TableRow>
                    <TableCell colSpan={9} className="text-center text-muted-foreground py-8">
                      Keine Frachtaufträge gefunden. Filter anpassen und „Aufbereiten" klicken.
                    </TableCell>
                  </TableRow>
                )}
                {items.map((item) => (
                  <TableRow key={item.id}
                    className={`cursor-pointer ${selected === item.id ? 'bg-blue-100' : 'hover:bg-muted/50'}`}
                    onClick={() => setSelected(item.id)}>
                    <TableCell>{item.belegart}</TableCell>
                    <TableCell>
                      <div className="font-medium">{item.belegNr}</div>
                      <div className="text-xs text-muted-foreground">{item.datum}</div>
                    </TableCell>
                    <TableCell>{item.lieferTermin}</TableCell>
                    <TableCell>{item.ladeDatum}</TableCell>
                    <TableCell>{item.spedNr}</TableCell>
                    <TableCell>{item.spedName}</TableCell>
                    <TableCell>{item.eLiefSchNr}</TableCell>
                    <TableCell>{item.frachtArtikel}</TableCell>
                    <TableCell className="text-right">
                      {item.pauschalFracht > 0 ? item.pauschalFracht.toFixed(2) : ''}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </div>
        </Card>
      </div>

      {/* Bottom Toolbar */}
      <div className="border-t bg-white px-4 py-2 flex items-center gap-3">
        <Button variant="outline" size="sm" className="gap-2"
          onClick={() => void loadData()} disabled={loading}>
          <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          Aufbereiten
        </Button>
        <Button variant="outline" size="sm" className="gap-2"
          onClick={() => {
            if (!selected) { push('Bitte einen Frachtauftrag auswählen'); return }
            navigate(`/einkauf/frachtauftrag/${selected}`)
          }}>
          <Truck className="h-4 w-4" />
          Frachtauftrag
        </Button>
        <Button variant="outline" size="sm" className="gap-2"
          onClick={() => {
            if (!selectedItem) { push('Bitte einen Frachtauftrag auswählen'); return }
            push(`Beleg anzeigen: ${selectedItem.belegNr}`)
          }}>
          <Eye className="h-4 w-4" />
          Beleg anzeigen
        </Button>
        <Button variant="outline" size="sm" className="gap-2"
          onClick={() => {
            if (!selectedItem) { push('Bitte einen Frachtauftrag auswählen'); return }
            const neu = parseFloat(prompt(`Pauschalfracht für ${selectedItem.belegNr} (aktuell: ${selectedItem.pauschalFracht.toFixed(2)} €):`) ?? '')
            if (!isNaN(neu) && neu >= 0) {
              setItems((prev) => prev.map((i) => i.id === selectedItem.id ? { ...i, pauschalFracht: neu } : i))
              push(`Pauschalfracht auf ${neu.toFixed(2)} € gesetzt.`)
            }
          }}>
          <Calculator className="h-4 w-4" />
          Calc
        </Button>
        <div className="ml-auto">
          <Button variant="outline" onClick={() => navigate('/einkauf')} size="sm">
            Schließen
          </Button>
        </div>
      </div>
    </div>
  )
}
