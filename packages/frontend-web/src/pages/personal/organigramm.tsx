import { useQuery } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Building2 } from 'lucide-react'

type OrgUnit = {
  id: string
  unit_code: string
  name: string
  unit_type: string
  parent_id: string | null
  children?: OrgUnit[]
}

/**
 * Der Endpunkt liefert den Baum schon verschachtelt (`org_chart`), also wird er
 * hier nicht zweimal gebaut. Bis zum 06.10.2026 las diese Maske `data.units` —
 * ein Feld, das es in der Antwort nie gab. Sie zeigte deshalb immer „Keine
 * Organisationseinheiten vorhanden", auch als der Endpunkt noch 503 antwortete,
 * weil `domain_hr.org_units` in keiner Datenbank existierte.
 */
function zaehleEinheiten(units: OrgUnit[]): number {
  return units.reduce((summe, u) => summe + 1 + zaehleEinheiten(u.children ?? []), 0)
}

function OrgNode({ unit, depth = 0 }: { unit: OrgUnit; depth?: number }): JSX.Element {
  return (
    <div className={depth > 0 ? 'ml-6 border-l pl-4' : ''}>
      <div className="my-1 flex items-center gap-2 rounded border bg-card px-3 py-2 shadow-sm">
        <Building2 className="h-4 w-4 text-muted-foreground shrink-0" />
        <span className="font-mono text-xs text-muted-foreground">{unit.unit_code}</span>
        <span className="font-medium text-sm">{unit.name}</span>
        <Badge variant="outline" className="ml-auto text-xs">{unit.unit_type}</Badge>
      </div>
      {unit.children?.map((child) => (
        <OrgNode key={child.id} unit={child} depth={depth + 1} />
      ))}
    </div>
  )
}

export default function OrganigrammPage(): JSX.Element {
  const { data, isError, error, refetch } = useQuery<{ org_chart: OrgUnit[] }>({
    queryKey: ['org-chart'],
    queryFn: async () =>
      (await apiClient.get<{ org_chart: OrgUnit[] }>('/api/v1/personal/org-chart')).data,
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const tree = data?.org_chart ?? []
  const anzahl = zaehleEinheiten(tree)

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div>
          <h1 className="text-xl font-semibold tracking-tight">Organigramm</h1>
          <p className="text-muted-foreground">Organisationsstruktur und Abteilungen</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>Organisationsstruktur ({anzahl} Einheiten)</CardTitle>
          </CardHeader>
          <CardContent>
            {tree.length === 0 && <p className="text-sm text-muted-foreground">Keine Organisationseinheiten vorhanden.</p>}
            {tree.map((root) => (
              <OrgNode key={root.id} unit={root} depth={0} />
            ))}
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
