import { useState } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import { Badge, type BadgeVariant } from '@/components/ui/badge'
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
          type="button"
          onClick={() => navigate(`/agrar/psm/stamm/${psm.id}`)}
          className="min-h-11 font-medium text-primary touch-manipulation"
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
        const statusColors: Record<string, BadgeVariant> = {
          'eingegangen': 'warning',
          'geprueft': 'success',
          'abgelehnt': 'error',
        }
        return (
          <Badge variant={statusColors[psm.erklaerungLandwirtStatus as keyof typeof statusColors] || 'muted'}>
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
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold md:text-3xl">Pflanzenschutzmittel</h1>
          <p className="text-muted-foreground">Mittel suchen und öffnen</p>
        </div>
        <Button onClick={() => navigate('/agrar/psm/stamm/neu')} className="min-h-touch gap-2 touch-manipulation">
          <Plus className="h-4 w-4" />
          Neues PSM
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input
                aria-label="Suche Pflanzenschutzmittel"
                placeholder="Mittel oder Wirkstoff suchen"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="min-h-touch pl-10"
              />
            </div>
            <Button variant="outline" className="min-h-touch gap-2 touch-manipulation" onClick={handleExport}>
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
