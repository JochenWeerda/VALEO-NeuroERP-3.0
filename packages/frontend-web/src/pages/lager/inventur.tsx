import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { CheckCircle, ClipboardList, Search } from 'lucide-react'
import { useToast } from '@/hooks/use-toast'
import { useInventur, useCompleteInventurPositions, type InventurPosition } from '@/lib/api/inventory'

export default function InventurPage(): JSX.Element {
  const [searchTerm, setSearchTerm] = useState('')
  const [selected, setSelected] = useState<Set<string>>(new Set())
  const { toast } = useToast()

  const { data, isLoading } = useInventur({ search: searchTerm || undefined })
  const completeMutation = useCompleteInventurPositions()
  const positionen = data?.items ?? []

  const handleComplete = async () => {
    const ids = Array.from(selected)
    try {
      await completeMutation.mutateAsync(ids)
      setSelected(new Set())
      toast({ title: 'Abgeschlossen', description: `${ids.length} Position(en) abgeschlossen.` })
    } catch {
      toast({ title: 'Fehler', description: 'Positionen konnten nicht abgeschlossen werden.', variant: 'destructive' })
    }
  }

  const columns = [
    {
      key: 'select' as const,
      label: '',
      render: (pos: InventurPosition) => (
        <input type="checkbox" checked={selected.has(pos.id)} onChange={() => {
          const newSet = new Set(selected)
          if (newSet.has(pos.id)) newSet.delete(pos.id)
          else newSet.add(pos.id)
          setSelected(newSet)
        }} className="h-4 w-4" />
      ),
    },
    { key: 'artikel' as const, label: 'Artikel' },
    { key: 'lagerort' as const, label: 'Lagerort' },
    { key: 'sollBestand' as const, label: 'Soll (t)' },
    { key: 'istBestand' as const, label: 'Ist (t)' },
    {
      key: 'differenz' as const,
      label: 'Differenz',
      render: (pos: InventurPosition) => (
        <span className={pos.differenz !== 0 ? 'font-semibold text-orange-600' : ''}>
          {pos.differenz > 0 ? '+' : ''}{pos.differenz} t
        </span>
      ),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (pos: InventurPosition) => (
        <Badge variant={pos.status === 'abgeschlossen' ? 'outline' : 'default'}>
          {pos.status === 'offen' ? 'Offen' : pos.status === 'gezaehlt' ? 'Gezählt' : 'Abgeschlossen'}
        </Badge>
      ),
    },
  ]

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <Skeleton className="h-8 w-32" />
            <Skeleton className="h-4 w-48" />
          </div>
          <Skeleton className="h-10 w-48" />
        </div>
        <div className="grid gap-4 md:grid-cols-3">
          {[1, 2, 3].map(i => <Skeleton key={i} className="h-24 w-full" />)}
        </div>
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Inventur</h1>
          <p className="text-muted-foreground">Stichtagsinventur {new Date().getFullYear()}</p>
        </div>
        <Button disabled={selected.size === 0 || completeMutation.isPending} onClick={handleComplete}>
          <CheckCircle className="h-4 w-4 mr-2" />
          {selected.size} Position(en) abschließen
        </Button>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Positionen Gesamt</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <ClipboardList className="h-5 w-5" />
              <span className="text-2xl font-bold">{positionen.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Offen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold">{positionen.filter((p) => p.status === 'offen').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Abgeschlossen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{positionen.filter((p) => p.status === 'abgeschlossen').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={positionen} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
