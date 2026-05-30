import { Link } from 'react-router-dom'
import { ArrowLeft, FileSearch, HardDrive } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { useAdminSuiteOperations } from '@/lib/api/admin-suite'

export default function AdminSuiteOperationsPage(): JSX.Element {
  const query = useAdminSuiteOperations()
  if (query.isLoading) return <LoadingState message="Operations Center wird geladen..." />
  if (query.isError || !query.data) return <ErrorState error={query.error instanceof Error ? query.error : null} onRetry={() => void query.refetch()} />
  return <div className="container mx-auto space-y-6 py-8">
    <div className="flex justify-between gap-3"><div><h1 className="text-3xl font-bold">Operations Center</h1><p className="mt-2 text-muted-foreground">Deploybare Jobs sind kein Ersatz fuer nachgewiesene Betriebslaeufe.</p></div><div className="flex gap-2"><Button asChild variant="outline"><Link to="/admin-suite/diagnostics"><FileSearch className="mr-2 h-4 w-4" />Diagnosemanifest</Link></Button><Button asChild variant="outline"><Link to="/admin-suite"><ArrowLeft className="mr-2 h-4 w-4" />Zurueck</Link></Button></div></div>
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{query.data.map((item) => <Card key={item.key}><CardHeader><HardDrive className="h-5 w-5 text-primary" /><CardTitle className="text-base">{item.label}</CardTitle><CardDescription>{item.notes}</CardDescription></CardHeader><CardContent className="space-y-2 text-xs"><div className="flex gap-2"><Badge variant="outline">Implementierung: {item.implementation_status}</Badge><Badge variant="outline">Runtime: {item.runtime_status}</Badge></div><p className="break-all text-muted-foreground">Quelle: {item.source}</p></CardContent></Card>)}</div>
  </div>
}
