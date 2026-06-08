import { useQuery } from '@tanstack/react-query'
import { useNavigate } from '@/app/routing/typed-router'
import { apiClient } from '@/lib/api-client'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Skeleton } from '@/components/ui/skeleton'
import { Plus, FileText } from 'lucide-react'

type PCNMeldung = {
  meldung_id: string
  produktname: string
  ufi: string
  cas_nummern: string
  verwendungskategorie: string
  pcnStatus: string
  created_at: string | null
}

const statusBadge = (s: string) => {
  switch (s) {
    case 'uebermittelt': return <Badge className="bg-green-100 text-green-800">Uebermittelt</Badge>
    case 'entwurf': return <Badge variant="secondary">Entwurf</Badge>
    default: return <Badge variant="outline">{s}</Badge>
  }
}

export default function PCNListePage(): JSX.Element {
  const navigate = useNavigate()
  const { data, isLoading } = useQuery({
    queryKey: ['compliance', 'pcn-meldungen'],
    queryFn: async () => {
      const res = await apiClient.get<{ items: PCNMeldung[]; total: number }>('/api/v1/compliance/pcn-meldungen')
      return res.data
    },
  })

  const items = data?.items ?? []

  if (isLoading) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-64" />
      </div>
    )
  }

  return (
    <div className="space-y-6 p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-2">
            <FileText className="h-8 w-8 text-blue-600" />
            PCN-Meldungen
          </h1>
          <p className="text-muted-foreground">Product Classification Notifications (EU 2017/542)</p>
        </div>
        <Button onClick={() => navigate('/compliance/pcn-ufi')}>
          <Plus className="h-4 w-4 mr-2" />
          Neue Meldung
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Meldungen ({items.length})</CardTitle>
        </CardHeader>
        <CardContent>
          {items.length === 0 ? (
            <p className="text-muted-foreground text-center py-8">Noch keine PCN-Meldungen vorhanden.</p>
          ) : (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Produkt</TableHead>
                  <TableHead>UFI</TableHead>
                  <TableHead>Kategorie</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Erstellt</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {items.map((m) => (
                  <TableRow key={m.meldung_id}>
                    <TableCell className="font-medium">{m.produktname}</TableCell>
                    <TableCell className="font-mono text-sm">{m.ufi || '—'}</TableCell>
                    <TableCell>{m.verwendungskategorie || '—'}</TableCell>
                    <TableCell>{statusBadge(m.pcnStatus)}</TableCell>
                    <TableCell>{m.created_at ? new Date(m.created_at).toLocaleDateString('de-DE') : '—'}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
