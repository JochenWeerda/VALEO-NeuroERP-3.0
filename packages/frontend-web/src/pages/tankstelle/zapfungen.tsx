import { useState } from 'react'
import { useZapfungen, type Zapfung } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { FileDown, Fuel, Search } from 'lucide-react'

const mockZapfungen: Zapfung[] = [
  { id: '1', kennzeichen: 'AB-LH 101', artikel: 'Diesel', menge: 120.5, zeitstempel: '2025-10-11 08:15', fahrer: 'Schmidt' },
  { id: '2', kennzeichen: 'AB-LH 102', artikel: 'Diesel', menge: 98.3, zeitstempel: '2025-10-11 09:45', fahrer: 'Mueller' },
]

export default function ZapfungenPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const { data: zapfungen = mockZapfungen } = useZapfungen()

  const columns = [
    { key: 'zeitstempel' as const, label: 'Zeitpunkt', render: (z: Zapfung) => <span className="font-mono text-sm">{z.zeitstempel}</span> },
    { key: 'kennzeichen' as const, label: 'Fahrzeug', render: (z: Zapfung) => <span className="font-mono font-bold">{z.kennzeichen}</span> },
    { key: 'fahrer' as const, label: 'Fahrer' },
    { key: 'artikel' as const, label: 'Kraftstoff', render: (z: Zapfung) => <Badge variant="outline">{z.artikel}</Badge> },
    { key: 'menge' as const, label: 'Menge (l)', render: (z: Zapfung) => `${z.menge} l` },
  ]

  const gesamtMenge = zapfungen.reduce((sum, z) => sum + z.menge, 0)

  return (
    <div className="space-y-4 p-6">
      <div><h1 className="text-3xl font-bold">Tankstellen-Zapfungen</h1><p className="text-muted-foreground">Betriebstankstelle</p></div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Zapfungen Heute</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><Fuel className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{zapfungen.length}</span></div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gesamt-Menge</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{gesamtMenge.toFixed(1)} l</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Durchschnitt</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{(gesamtMenge / Math.max(zapfungen.length, 1)).toFixed(1)} l</span></CardContent></Card>
      </div>
      <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex gap-4"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" /></div><Button variant="outline" className="gap-2"><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
      <Card><CardContent className="pt-6"><DataTable data={zapfungen} columns={columns} /></CardContent></Card>
    </div>
  )
}
