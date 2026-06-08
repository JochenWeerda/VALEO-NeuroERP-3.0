import { Link } from '@/app/routing/react-router-compat'
import { ArrowLeft, Database, ShieldAlert } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { useAdminSuiteMigration } from '@/lib/api/admin-suite'

export default function AdminSuiteMigrationPage(): JSX.Element {
  const query = useAdminSuiteMigration()
  if (query.isLoading) return <LoadingState message="Migration Cockpit wird geladen..." />
  if (query.isError || !query.data) return <ErrorState error={query.error instanceof Error ? query.error : null} onRetry={() => void query.refetch()} />
  return (
    <div className="container mx-auto space-y-6 py-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div><h1 className="text-3xl font-bold">Migration Cockpit</h1><p className="mt-2 text-muted-foreground">Dry Run, Mapping-Version und Reconciliation vor jeder produktiven Freigabe.</p></div>
        <Button asChild variant="outline"><Link to="/admin-suite"><ArrowLeft className="mr-2 h-4 w-4" />Zur Admin Suite</Link></Button>
      </div>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {query.data.profiles.map((profile) => (
          <Card key={profile.key}>
            <CardHeader><Database className="h-5 w-5 text-primary" /><CardTitle className="text-base">{profile.label}</CardTitle><CardDescription>{profile.notes}</CardDescription></CardHeader>
            <CardContent><Badge variant={profile.status === 'available' ? 'default' : profile.status === 'blocked' ? 'destructive' : 'outline'}>{profile.status}</Badge></CardContent>
          </Card>
        ))}
      </div>
      <Card>
        <CardHeader><CardTitle>Batches</CardTitle><CardDescription>Das Cockpit schreibt noch keine Fachdaten. Es verwaltet Freigabe-Evidenz fuer den bestehenden Importpfad.</CardDescription></CardHeader>
        <CardContent className="space-y-3">
          {query.data.batches.length === 0 ? <p className="text-sm text-muted-foreground">Noch keine Batches angelegt.</p> : query.data.batches.map((batch) => (
            <div key={batch.id} className="rounded border p-3 text-sm">
              <div className="flex flex-wrap items-center gap-2"><Badge variant={batch.status === 'approved' ? 'default' : 'secondary'}>{batch.status}</Badge><span>{batch.source_profile}</span><span>{batch.mapping_version}</span></div>
              <p className="mt-2 text-xs text-muted-foreground">Batch {batch.id} · Hash {batch.source_hash}</p>
            </div>
          ))}
        </CardContent>
      </Card>
      <Card>
        <CardHeader><ShieldAlert className="h-5 w-5 text-primary" /><CardTitle className="text-base">Produktivimport gesperrt</CardTitle><CardDescription>Ein separater Execute-Adapter folgt erst nach fachlicher Abnahme der Reconciliation-Gates.</CardDescription></CardHeader>
      </Card>
    </div>
  )
}
