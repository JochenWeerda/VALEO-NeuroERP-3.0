import { useState, useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { FileDown, FileText, Plus, Search } from 'lucide-react'
import { useFrachtbriefe, type Frachtbrief } from '@/lib/api/misc-modules'
import { useSupplyChainOverview } from '@/lib/api/supply-chain'
import { summarizeSupplyOps } from '@/lib/professional-control-centers'

export default function FrachtbriefePage(): JSX.Element {
  const navigate = useNavigate()
  const { data: chain } = useSupplyChainOverview()
  const [searchTerm, setSearchTerm] = useState('')
  const { data: frachtbriefe, isLoading } = useFrachtbriefe()
  const list = useMemo(() => frachtbriefe ?? [], [frachtbriefe])
  const supplyOps = useMemo(() => summarizeSupplyOps(chain), [chain])

  const fallkopf = useMemo(() => {
    const unterwegs = list.filter((f) => f.status === 'unterwegs').length
    const erstellt = list.filter((f) => f.status === 'erstellt').length
    const total = list.length
    return {
      status: erstellt > 0 ? `${erstellt} Frachtbrief(e) noch nicht versendet` : unterwegs > 0 ? `${unterwegs} unterwegs` : 'Keine offenen Frachtbriefe',
      statusColor: erstellt > 0 ? 'text-amber-700 bg-amber-50 border-amber-300' : unterwegs > 0 ? 'text-blue-700 bg-blue-50 border-blue-300' : 'text-green-700 bg-green-50 border-green-300',
      blocker: erstellt > 0 ? `${erstellt} Dokument(e) warten auf Versand` : 'Kein Blocker',
      dokumentdruck: total > 0 ? `${total} Frachtbriefe gesamt, ${unterwegs} in Transit` : 'Keine Dokumente',
      naechsteAktion: erstellt > 0 ? 'Erstellte Frachtbriefe pruefen und versenden' : unterwegs > 0 ? 'Zustellung verfolgen' : 'Neuen Frachtbrief anlegen',
    }
  }, [list])

  const columns = [
    {
      key: 'nummer' as const,
      label: 'Frachtbrief-Nr.',
      render: (f: Frachtbrief) => (
        <button onClick={() => navigate(`/logistik/frachtbrief/${f.id}`)} className="font-medium text-blue-600 hover:underline font-mono">
          {f.nummer}
        </button>
      ),
    },
    { key: 'kennzeichen' as const, label: 'LKW', render: (f: Frachtbrief) => <span className="font-mono">{f.kennzeichen}</span> },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'menge' as const, label: 'Menge (t)', render: (f: Frachtbrief) => `${f.menge} t` },
    {
      key: 'empfaenger' as const,
      label: 'Von / Nach',
      render: (f: Frachtbrief) => (
        <div className="text-sm">
          <div>{f.absender}</div>
          <div className="text-muted-foreground">{'->'} {f.empfaenger}</div>
        </div>
      ),
    },
    {
      key: 'datum' as const,
      label: 'Datum',
      render: (f: Frachtbrief) => new Date(f.datum).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (f: Frachtbrief) => (
        <Badge variant={f.status === 'zugestellt' ? 'outline' : f.status === 'unterwegs' ? 'secondary' : 'default'}>
          {f.status === 'erstellt' ? 'Erstellt' : f.status === 'unterwegs' ? 'Unterwegs' : 'Zugestellt'}
        </Badge>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="space-y-4 p-3 md:p-6">
        <Skeleton className="h-10 w-48" />
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-24" />)}
        </div>
        <Skeleton className="h-64" />
      </div>
    )
  }

  return (
    <div className="space-y-4 p-3 md:p-6">
      {/* Operativer Fallkopf */}
      <Card className={`border ${fallkopf.statusColor}`}>
        <CardContent className="pt-4 pb-3 text-sm space-y-1">
          <div className="font-semibold">Frachtbriefe: {fallkopf.status}</div>
          <div>Blocker: {fallkopf.blocker}</div>
          <div>Dokumentdruck: {fallkopf.dokumentdruck}</div>
          <div>Naechste Aktion: {fallkopf.naechsteAktion}</div>
        </CardContent>
      </Card>

      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Frachtbriefe</h1>
          <p className="text-muted-foreground">Transport-Dokumentation</p>
        </div>
        <Button onClick={() => navigate('/logistik/frachtbrief/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neuer Frachtbrief
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Frachtbriefe Heute</CardTitle></CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{list.length}</span>
            </div>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Unterwegs</CardTitle></CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-orange-600">{list.filter((f) => f.status === 'unterwegs').length}</span>
          </CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Zugestellt</CardTitle></CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{list.filter((f) => f.status === 'zugestellt').length}</span>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Annahme offen</div><div className="text-2xl font-semibold">{chain.waitingInbound}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Wiegungen offen</div><div className="text-2xl font-semibold">{chain.openWeighingTickets}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Chargen gesperrt / Prüfung</div><div className="text-2xl font-semibold">{chain.blockedCharges}</div></CardContent></Card>
        <Card><CardContent className="pt-6"><div className="text-xs text-muted-foreground">Aktive Kennzeichen</div><div className="text-sm font-semibold">{chain.activeVehiclePlates.slice(0, 3).join(', ') || 'n/a'}</div></CardContent></Card>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Bottleneck</CardTitle></CardHeader><CardContent><div className="text-2xl font-semibold">{supplyOps.bottleneck}</div></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Druck</CardTitle></CardHeader><CardContent><Badge variant={supplyOps.pressure === 'hoch' ? 'destructive' : 'outline'}>{supplyOps.pressure}</Badge></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Naechste Aktion</CardTitle></CardHeader><CardContent><div className="text-sm font-semibold">{supplyOps.nextAction}</div></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={list} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
