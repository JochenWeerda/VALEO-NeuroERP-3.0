import { useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useZulassungenRegister, type Zulassung } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AlertTriangle, FileDown, Search, ShieldCheck } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

export default function ZulassungenRegisterPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const searchRef = useRef<HTMLInputElement | null>(null)
  const { data: zulassungen = [], isError, error, refetch } = useZulassungenRegister()

  const shortcuts = buildCoreMaskShortcuts({
    onSearch: () => searchRef.current?.focus(),
    onRefresh: () => {
      void refetch()
    },
  })
  useKeyboardShortcuts(shortcuts)

  const gefilterteZulassungen = useMemo(() => {
    const needle = searchTerm.trim().toLowerCase()
    if (!needle) return zulassungen
    return zulassungen.filter((z) =>
      [z.produkt, z.typ, z.nummer, z.behoerde, z.status].some((value) => value.toLowerCase().includes(needle)),
    )
  }, [searchTerm, zulassungen])

  const auslaufendeZulassungen = gefilterteZulassungen.filter((z) => z.status === 'auslaufend')
  const aktiveZulassungen = gefilterteZulassungen.filter((z) => z.status === 'aktiv')

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const handleExport = (): void => {
    const rows = [
      ['Produkt', 'Typ', 'Zulassungsnummer', 'Behoerde', 'Gueltig bis', 'Status'],
      ...gefilterteZulassungen.map((z) => [z.produkt, z.typ, z.nummer, z.behoerde, z.gueltigBis, z.status]),
    ]
    const csv = rows.map((row) => row.map((value) => `"${String(value).replace(/"/g, '""')}"`).join(';')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = 'zulassungen-register.csv'
    link.click()
    URL.revokeObjectURL(url)
  }

  const columns = [
    {
      key: 'produkt' as const,
      label: 'Produkt',
      render: (z: Zulassung) => <div><div className="font-medium">{z.produkt}</div><Badge variant="outline" className="mt-1">{z.typ}</Badge></div>,
    },
    { key: 'nummer' as const, label: 'Zulassungsnummer', render: (z: Zulassung) => <span className="font-mono text-sm">{z.nummer}</span> },
    { key: 'behoerde' as const, label: 'Behoerde' },
    { key: 'gueltigBis' as const, label: 'Gueltig bis', render: (z: Zulassung) => new Date(z.gueltigBis).toLocaleDateString('de-DE') },
    { key: 'status' as const, label: 'Status', render: (z: Zulassung) => <Badge variant={z.status === 'aktiv' ? 'outline' : z.status === 'auslaufend' ? 'secondary' : 'destructive'}>{z.status === 'aktiv' ? 'Aktiv' : z.status === 'auslaufend' ? 'Auslaufend' : 'Abgelaufen'}</Badge> },
  ]

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between"><div><h1 className="text-3xl font-bold">Zulassungsregister</h1><p className="text-muted-foreground">PSM, Saatgut & Duenger</p></div></div>
        {auslaufendeZulassungen.length > 0 && <Card className="border-orange-500 bg-orange-50"><CardContent className="pt-4"><div className="flex items-center gap-2 text-orange-900"><AlertTriangle className="h-5 w-5" /><span className="font-semibold">{auslaufendeZulassungen.length} Zulassung(en) laufen bald ab!</span></div></CardContent></Card>}
        <div className="grid gap-4 md:grid-cols-3">
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Zulassungen Gesamt</CardTitle></CardHeader><CardContent><div className="flex items-center gap-2"><ShieldCheck className="h-5 w-5 text-blue-600" /><span className="text-2xl font-bold">{gefilterteZulassungen.length}</span></div></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aktiv</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{aktiveZulassungen.length}</span></CardContent></Card>
          <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Auslaufend</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{auslaufendeZulassungen.length}</span></CardContent></Card>
        </div>
        <div className="grid gap-4 xl:grid-cols-[minmax(0,1fr)_320px]">
          <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex gap-4"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input ref={searchRef} placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" /></div><Button variant="outline" className="gap-2" onClick={handleExport}><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
          <Card><CardHeader><CardTitle>Operator-Fokus</CardTitle></CardHeader><CardContent className="space-y-3 text-sm"><div className="rounded-lg border p-3"><div className="font-medium">Auslaufende Zulassungen</div><div className="text-muted-foreground">{auslaufendeZulassungen.length} Fall/Faelle mit unmittelbarem Handlungsbedarf.</div></div><Button className="w-full justify-start" variant="outline" onClick={() => { const target = auslaufendeZulassungen[0] ?? gefilterteZulassungen[0]; if (target) setSearchTerm(target.nummer) }}>Kritische Zulassung fokussieren</Button><Button className="w-full justify-start" variant="outline" onClick={() => navigate('/dokumente/ablage')}>Dokumentenablage oeffnen</Button><Button className="w-full justify-start" variant="outline" onClick={() => navigate('/compliance/meldewesen-konsole')}>Meldewesen-Konsole oeffnen</Button></CardContent></Card>
        </div>
        <Card><CardContent className="pt-6"><DataTable data={gefilterteZulassungen} columns={columns} /></CardContent></Card>
      </div>
      <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
