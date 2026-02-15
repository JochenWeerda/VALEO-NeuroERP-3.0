import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { toast } from '@/hooks/use-toast'
import { useCreateReportPermission, useDeleteReportPermission, useReportPermissions } from '@/lib/api/admin'

function parseCsv(input: string): string[] {
  return input
    .split(',')
    .map((part) => part.trim())
    .filter(Boolean)
}

export default function ReportBerechtigungenPage(): JSX.Element {
  const { data: items = [], isLoading } = useReportPermissions({ activeOnly: false })
  const createMutation = useCreateReportPermission()
  const deleteMutation = useDeleteReportPermission()

  const [roleId, setRoleId] = useState('controller')
  const [reportKey, setReportKey] = useState('finance.bwa')
  const [canView, setCanView] = useState(true)
  const [canExport, setCanExport] = useState(false)
  const [allowedScopes, setAllowedScopes] = useState('')
  const [filters, setFilters] = useState('{}')

  const onCreate = async () => {
    if (!roleId || !reportKey) {
      toast({ title: 'Pflichtfelder fehlen', description: 'Rolle und Report-Key sind erforderlich.', variant: 'destructive' })
      return
    }
    try {
      const parsedFilters = filters ? JSON.parse(filters) : {}
      await createMutation.mutateAsync({
        role_id: roleId,
        report_key: reportKey,
        can_view: canView,
        can_export: canExport,
        allowed_scopes: parseCsv(allowedScopes),
        filters: parsedFilters,
        active: true,
      })
      toast({ title: 'Berechtigung angelegt' })
    } catch (error) {
      toast({ title: 'Anlegen fehlgeschlagen', description: String(error), variant: 'destructive' })
    }
  }

  return (
    <div className="space-y-6 p-6">
      <div>
        <h1 className="text-3xl font-bold">Report-Berechtigungen</h1>
        <p className="text-muted-foreground">Self-Service-Reports rollenbasiert freigeben (View/Export/Filter).</p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Neue Berechtigung</CardTitle>
        </CardHeader>
        <CardContent className="grid gap-3 md:grid-cols-2">
          <div className="space-y-1">
            <Label htmlFor="role">Rolle</Label>
            <Input id="role" value={roleId} onChange={(e) => setRoleId(e.target.value)} />
          </div>
          <div className="space-y-1">
            <Label htmlFor="report-key">Report-Key</Label>
            <Input id="report-key" value={reportKey} onChange={(e) => setReportKey(e.target.value)} />
          </div>
          <div className="space-y-1">
            <Label htmlFor="scopes">Allowed Scopes (CSV)</Label>
            <Input id="scopes" value={allowedScopes} onChange={(e) => setAllowedScopes(e.target.value)} placeholder="tenant,region,cost_center" />
          </div>
          <div className="space-y-1">
            <Label htmlFor="filters">Filter JSON</Label>
            <Input id="filters" value={filters} onChange={(e) => setFilters(e.target.value)} />
          </div>
          <div className="flex items-center gap-2">
            <input id="can-view" type="checkbox" checked={canView} onChange={(e) => setCanView(e.target.checked)} />
            <Label htmlFor="can-view">View</Label>
          </div>
          <div className="flex items-center gap-2">
            <input id="can-export" type="checkbox" checked={canExport} onChange={(e) => setCanExport(e.target.checked)} />
            <Label htmlFor="can-export">Export</Label>
          </div>
          <div className="md:col-span-2">
            <Button onClick={onCreate} disabled={createMutation.isPending}>Berechtigung anlegen</Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Vorhandene Berechtigungen</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2">
          {isLoading ? <div className="text-sm text-muted-foreground">Lade...</div> : null}
          {items.map((item) => (
            <div key={item.id} className="flex items-center justify-between rounded border p-3">
              <div>
                <div className="font-medium">{item.role_id} {'->'} {item.report_key}</div>
                <div className="flex items-center gap-2 text-xs text-muted-foreground">
                  <Badge variant="outline">{item.can_view ? 'view' : 'no-view'}</Badge>
                  <Badge variant="outline">{item.can_export ? 'export' : 'no-export'}</Badge>
                  <Badge variant="outline">{item.active ? 'aktiv' : 'inaktiv'}</Badge>
                </div>
              </div>
              <Button
                variant="ghost"
                size="sm"
                onClick={() => deleteMutation.mutate(item.id)}
                disabled={deleteMutation.isPending}
              >
                Loeschen
              </Button>
            </div>
          ))}
        </CardContent>
      </Card>
    </div>
  )
}
