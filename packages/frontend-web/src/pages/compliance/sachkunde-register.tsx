import { useState, useRef } from 'react'
import { useNavigate } from '@/app/routing/react-router-compat'
import { useSachkundeRegister, type Sachkundenachweis } from '@/lib/api/betrieb'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { KeyboardShortcutBar } from '@/components/keyboard/KeyboardShortcutBar'
import { buildCoreMaskShortcuts, useKeyboardShortcuts } from '@/hooks/useKeyboardShortcuts'
import { AlertTriangle, Award, FileDown, Plus, Search } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

export default function SachkundeRegisterPage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')
  const searchRef = useRef<HTMLInputElement | null>(null)
  const { data: sachkunde = [], isError, error, refetch } = useSachkundeRegister()

  const shortcuts = buildCoreMaskShortcuts({
    onNew: () => navigate('/compliance/sachkunde-neu'),
    onSearch: () => searchRef.current?.focus(),
    onRefresh: () => { void refetch() },
  })
  useKeyboardShortcuts(shortcuts)

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  const ablaufend = sachkunde.filter((s) => {
    const ablauf = new Date(s.gueltigBis)
    const warnung = new Date()
    warnung.setMonth(warnung.getMonth() + 3)
    return ablauf <= warnung && ablauf >= new Date()
  }).length

  const columns = [
    {
      key: 'kunde' as const,
      label: 'Kunde',
      render: (s: Sachkundenachweis) => (
        <button onClick={() => navigate(`/verkauf/kunden-stamm/${s.id}`)} className="font-medium text-blue-600 hover:underline">
          {s.kunde}
        </button>
      ),
    },
    { key: 'kundennr' as const, label: 'Kd-Nr', render: (s: Sachkundenachweis) => <span className="font-mono text-sm">{s.kundennr}</span> },
    { key: 'nachweisNr' as const, label: 'Nachweis-Nr', render: (s: Sachkundenachweis) => <span className="font-mono">{s.nachweisNr}</span> },
    {
      key: 'gueltigBis' as const,
      label: 'Gueltig bis',
      render: (s: Sachkundenachweis) => {
        const ablauf = new Date(s.gueltigBis)
        const istAblaufend = ablauf <= new Date(Date.now() + 90 * 24 * 60 * 60 * 1000)
        return <span className={istAblaufend ? 'font-semibold text-orange-600' : ''}>{ablauf.toLocaleDateString('de-DE')}</span>
      },
    },
    { key: 'ausstellendeStelle' as const, label: 'Ausgestellt von' },
    {
      key: 'status' as const,
      label: 'Status',
      render: (s: Sachkundenachweis) => (
        <Badge variant={s.status === 'gueltig' ? 'outline' : s.status === 'ablaufend' ? 'secondary' : 'destructive'}>
          {s.status === 'gueltig' ? 'Gueltig' : s.status === 'ablaufend' ? 'Laeuft ab' : 'Abgelaufen'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="flex flex-col">
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">PSM-Sachkunde-Register</h1>
          <p className="text-muted-foreground">Sachkundenachweis nach Paragraf 9 PflSchG</p>
        </div>
        <Button onClick={() => navigate('/compliance/sachkunde-neu')} className="gap-2"><Plus className="h-4 w-4" />Nachweis erfassen</Button>
      </div>

      {ablaufend > 0 && (
        <Card className="border-orange-500 bg-orange-50">
          <CardContent className="pt-4">
            <div className="flex items-center gap-2 text-orange-900">
              <AlertTriangle className="h-5 w-5" />
              <span className="font-semibold">{ablaufend} Nachweis(e) laufen in den naechsten 3 Monaten ab!</span>
            </div>
          </CardContent>
        </Card>
      )}

      <div className="rounded-lg bg-orange-50 p-4 text-sm text-orange-900">
        <div className="flex items-center gap-2"><Award className="h-4 w-4" /><p className="font-semibold">Verkaufsvoraussetzung PSM</p></div>
      </div>

      <div className="grid gap-4 md:grid-cols-4">
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Nachweise Gesamt</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold">{sachkunde.length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Gueltig</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-green-600">{sachkunde.filter((s) => s.status === 'gueltig').length}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Laeuft ab (3 Mon.)</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-orange-600">{ablaufend}</span></CardContent></Card>
        <Card><CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Abgelaufen</CardTitle></CardHeader><CardContent><span className="text-2xl font-bold text-red-600">{sachkunde.filter((s) => s.status === 'abgelaufen').length}</span></CardContent></Card>
      </div>

      <Card>
        <CardHeader><CardTitle>Suche</CardTitle></CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1"><Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" /><Input ref={searchRef} placeholder="Suche Kunde oder Nachweis-Nr..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" /></div>
            <Button variant="outline" className="gap-2"><FileDown className="h-4 w-4" />Export</Button>
          </div>
        </CardContent>
      </Card>

      <Card><CardContent className="pt-6"><DataTable data={sachkunde} columns={columns} /></CardContent></Card>
    </div>
    <KeyboardShortcutBar shortcuts={shortcuts} />
    </div>
  )
}
