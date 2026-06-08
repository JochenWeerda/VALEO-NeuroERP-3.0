import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { ErrorState } from '@/components/ErrorState'
import { FileDown, Plus, Search } from 'lucide-react'
import { toast } from '@/hooks/use-toast'
import { usePSM, type PSM } from '@/lib/api/agrar'

export default function PSMListePage(): JSX.Element {
  const navigate = useNavigate()
  const [searchTerm, setSearchTerm] = useState('')

  const { data, isLoading, isError, error, refetch } = usePSM({ search: searchTerm || undefined, source: 'bvl' })
  const psmList = data?.items ?? []

  const handleExport = () => {
    try {
      const csvHeader = 'Mittel;Wirkstoff;Kulturen;Zulassung bis;Status;Erklärung Landwirt\n'
      const csvContent = psmList.map(psm =>
        `"${psm.mittel}";"${psm.wirkstoff}";"${psm.kulturen.join(', ')}";"${psm.zulassungBis}";"${psm.status}";"${psm.erklaerungLandwirtStatus || ''}"`
      ).join('\n')

      const csv = csvHeader + csvContent
      const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' })
      const link = document.createElement('a')
      const url = URL.createObjectURL(blob)
      link.setAttribute('href', url)
      link.setAttribute('download', `psm-liste-${new Date().toISOString().split('T')[0]}.csv`)
      link.style.visibility = 'hidden'
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)

      toast({
        title: 'Export erfolgreich',
        description: `${psmList.length} PSM-Datensätze wurden exportiert.`,
      })
    } catch {
      toast({
        variant: 'destructive',
        title: 'Export fehlgeschlagen',
        description: 'Beim Exportieren ist ein Fehler aufgetreten.',
      })
    }
  }

  const columns = [
    {
      key: 'mittel' as const,
      label: 'Mittel',
      render: (psm: PSM) => (
        <button
          onClick={() => navigate(`/agrar/psm/stamm/${psm.id}`)}
          className="font-medium text-blue-600 hover:underline"
        >
          {psm.mittel}
        </button>
      ),
    },
    {
      key: 'wirkstoff' as const,
      label: 'Wirkstoff',
    },
    {
      key: 'kulturen' as const,
      label: 'Kulturen',
      render: (psm: PSM) => (
        <div className="flex flex-wrap gap-1">
          {psm.kulturen.slice(0, 2).map((k, i) => (
            <Badge key={i} variant="outline">{k}</Badge>
          ))}
          {psm.kulturen.length > 2 && <Badge variant="secondary">+{psm.kulturen.length - 2}</Badge>}
        </div>
      ),
    },
    {
      key: 'zulassungBis' as const,
      label: 'Zulassung bis',
      render: (psm: PSM) => new Date(psm.zulassungBis).toLocaleDateString('de-DE'),
    },
    {
      key: 'status' as const,
      label: 'Status',
      render: (psm: PSM) => (
        <Badge variant={psm.status === 'aktiv' ? 'outline' : 'destructive'}>
          {psm.status === 'aktiv' ? 'Aktiv' : psm.status === 'auslaufend' ? 'Auslaufend' : 'Widerrufen'}
        </Badge>
      ),
    },
    {
      key: 'erklaerungLandwirtStatus' as const,
      label: 'Erklärung Landwirt',
      render: (psm: PSM) => {
        if (!psm.erklaerungLandwirtStatus) return <span className="text-muted-foreground">-</span>
        const statusColors = {
          'eingegangen': 'bg-yellow-100 text-yellow-800',
          'geprueft': 'bg-green-100 text-green-800',
          'abgelehnt': 'bg-red-100 text-red-800',
        }
        return (
          <Badge className={statusColors[psm.erklaerungLandwirtStatus as keyof typeof statusColors] || 'bg-gray-100 text-gray-800'}>
            {psm.erklaerungLandwirtStatus === 'eingegangen' ? 'Eingegangen' :
             psm.erklaerungLandwirtStatus === 'geprueft' ? 'Geprüft' : 'Abgelehnt'}
          </Badge>
        )
      },
    },
  ]

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <Skeleton className="h-8 w-56" />
            <Skeleton className="h-4 w-32" />
          </div>
          <Skeleton className="h-10 w-32" />
        </div>
        <Skeleton className="h-20 w-full" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  if (isError) {
    return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />
  }

  return (
    <div className="space-y-4 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Pflanzenschutzmittel</h1>
          <p className="text-muted-foreground">PSM-Stammdaten</p>
        </div>
        <Button onClick={() => navigate('/agrar/psm/stamm/neu')} className="gap-2">
          <Plus className="h-4 w-4" />
          Neues PSM
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                placeholder="Suche nach Mittel oder Wirkstoff..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
              />
            </div>
            <Button variant="outline" className="gap-2" onClick={handleExport}>
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={psmList} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
