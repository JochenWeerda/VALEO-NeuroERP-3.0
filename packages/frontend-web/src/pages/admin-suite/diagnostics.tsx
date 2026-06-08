import { Link } from '@/app/routing/react-router-compat'
import { ArrowLeft, FileSearch } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { useAdminSuiteDiagnostics } from '@/lib/api/admin-suite'

export default function AdminSuiteDiagnosticsPage(): JSX.Element {
  const query = useAdminSuiteDiagnostics()
  if (query.isLoading) return <LoadingState message="Diagnosepaket-Manifest wird geladen..." />
  if (query.isError || !query.data) return <ErrorState error={query.error instanceof Error ? query.error : null} onRetry={() => void query.refetch()} />

  return <div className="container mx-auto space-y-6 py-8">
    <div className="flex justify-between gap-3">
      <div>
        <h1 className="text-3xl font-bold">Diagnosepaket-Manifest</h1>
        <p className="mt-2 text-muted-foreground">Der Katalog beschreibt erlaubte Supportdaten. Beim Oeffnen werden keine Logs oder Live-Daten gesammelt.</p>
      </div>
      <Button asChild variant="outline"><Link to="/admin-suite/operations"><ArrowLeft className="mr-2 h-4 w-4" />Zurueck</Link></Button>
    </div>

    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {query.data.map((item) => <Card key={item.key}>
        <CardHeader>
          <FileSearch className="h-5 w-5 text-primary" />
          <CardTitle className="text-base">{item.label}</CardTitle>
          <CardDescription>{item.notes}</CardDescription>
        </CardHeader>
        <CardContent className="space-y-3 text-xs">
          <div className="flex flex-wrap gap-2">
            <Badge variant="outline">Sammlung: {item.collection_status}</Badge>
            <Badge variant="secondary">Redaktion: {item.redaction}</Badge>
          </div>
          <p className="break-all text-muted-foreground">Quelle: {item.source}</p>
        </CardContent>
      </Card>)}
    </div>
  </div>
}
