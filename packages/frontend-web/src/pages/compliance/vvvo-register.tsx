import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { useVVVORegister, type VVVOBetrieb } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { FileDown, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

export default function VVVORegisterPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const searchRef = useRef<HTMLInputElement | null>(null)
  const { data: vvvo = [], isError, error, refetch } = useVVVORegister()

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => navigate('/compliance/vvvo-neu'),
    onSearch: () => searchRef.current?.focus(),
    onRefresh: () => { void refetch() },
  })
  useKeyboardShortcuts(shortcuts)

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const columns = [
    { key: 'betriebsname' as const, label: 'Betrieb', render: (v: VVVOBetrieb) => <button onClick={() => navigate(`/crm/betrieb/${v.id}`)} className="font-medium text-blue-600 hover:underline">{v.betriebsname}</button> },
    { key: 'vvvo' as const, label: 'VVVO-Betriebsnummer', render: (v: VVVOBetrieb) => <span className="font-mono font-bold text-lg">{v.vvvo}</span> },
    { key: 'bundesland' as const, label: 'Bundesland' },
    { key: 'tierart' as const, label: 'Tierart', render: (v: VVVOBetrieb) => <Badge variant="outline">{v.tierart}</Badge> },
    { key: 'letzteAktualisierung' as const, label: 'Aktualisierung', render: (v: VVVOBetrieb) => new Date(v.letzteAktualisierung).toLocaleDateString('de-DE') },
    { key: 'status' as const, label: 'Status', render: (v: VVVOBetrieb) => <Badge variant={v.status === 'aktiv' ? 'outline' : 'secondary'}>{v.status === 'aktiv' ? 'Aktiv' : 'Inaktiv'}</Badge> },
  ]

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between"><div><h1 className="text-3xl font-bold">VVVO-Register</h1><p className="text-muted-foreground">Viehverkehrsverordnung - Betriebsnummern</p></div><Button onClick={() => navigate('/compliance/vvvo-neu')} className="gap-2"><Plus className="h-4 w-4" />Betrieb erfassen</Button></div>
      <div className="grid gap-4 md:grid-cols-3">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Betriebe Gesamt</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{vvvo.length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aktiv</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{vvvo.filter((v) => v.status === 'aktiv').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Bundeslaender</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{new Set(vvvo.map((v) => v.bundesland)).size}</span></CardContent></Card>
      </div>
      <Card><CardHeader><CardTitle>Suche</CardTitle></CardHeader><CardContent><div className="flex gap-4"><div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input ref={searchRef} placeholder="Suche Betrieb oder VVVO-Nummer..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" /></div><Button variant="outline" className="gap-2"><FileDown className="h-4 w-4" />Export</Button></div></CardContent></Card>
      <Card><CardContent className="pt-6"><DataTable data={vvvo} columns={columns} /></CardContent></Card>
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
