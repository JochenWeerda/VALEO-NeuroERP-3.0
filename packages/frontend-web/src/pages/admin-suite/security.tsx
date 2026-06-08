import { Link } from '@/app/routing/typed-router'
import { ArrowLeft, Bot, ShieldCheck, UserCog } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState, LoadingState } from '@/components/ErrorState'
import { useAdminSuiteSecurity, type SecurityRole } from '@/lib/api/admin-suite'

function RoleCard({ role }: { role: SecurityRole }): JSX.Element {
  const Icon = role.actor_type === 'agent' ? Bot : UserCog
  return (
    <Card>
      <CardHeader><Icon className="h-5 w-5 text-primary" /><CardTitle className="text-base">{role.key}</CardTitle><CardDescription>{role.notes ?? 'Bestehendes RBAC-Rollenpaket'}</CardDescription></CardHeader>
      <CardContent className="flex flex-wrap gap-1">{role.permissions.map((permission) => <Badge key={permission} variant="outline">{permission}</Badge>)}</CardContent>
    </Card>
  )
}

export default function AdminSuiteSecurityPage(): JSX.Element {
  const query = useAdminSuiteSecurity()
  if (query.isLoading) return <LoadingState message="Security Governance wird geladen..." />
  if (query.isError || !query.data) return <ErrorState error={query.error instanceof Error ? query.error : null} onRetry={() => void query.refetch()} />
  return (
    <div className="container mx-auto space-y-6 py-8">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div><h1 className="text-3xl font-bold">Security und Agent Governance</h1><p className="mt-2 text-muted-foreground">Lesende Sicht auf bestehende RBAC-Pakete. Simulationen veraendern keine Rechte.</p></div>
        <Button asChild variant="outline"><Link to="/admin-suite"><ArrowLeft className="mr-2 h-4 w-4" />Zur Admin Suite</Link></Button>
      </div>
      <Card><CardHeader><ShieldCheck className="h-5 w-5 text-primary" /><CardTitle>Governance-Leitplanke</CardTitle><CardDescription>Agentenrollen bleiben getrennt und erhalten keine Systemadministration. SoD-Warnungen werden serverseitig simuliert.</CardDescription></CardHeader></Card>
      <section className="space-y-3"><h2 className="text-xl font-semibold">Menschenrollen</h2><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{query.data.roles.map((role) => <RoleCard key={role.key} role={role} />)}</div></section>
      <section className="space-y-3"><h2 className="text-xl font-semibold">Agentenrollen</h2><div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">{query.data.agent_roles.map((role) => <RoleCard key={role.key} role={role} />)}</div></section>
    </div>
  )
}
