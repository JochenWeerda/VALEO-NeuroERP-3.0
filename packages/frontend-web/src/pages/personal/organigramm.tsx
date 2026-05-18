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

function buildTree(units: OrgUnit[]): OrgUnit[] {
  const map = new Map<string, OrgUnit>()
  units.forEach((u) => map.set(u.id, { ...u, children: [] }))
  const roots: OrgUnit[] = []
  map.forEach((u) => {
    if (u.parent_id && map.has(u.parent_id)) {
      const parent = map.get(u.parent_id)
      if (parent) { parent.children = parent.children ?? []; parent.children.push(u) }
    } else {
      roots.push(u)
    }
  })
  return roots
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
  const { data, isError, error, refetch } = useQuery<{ units: OrgUnit[] }>({
    queryKey: ['org-chart'],
    queryFn: async () => (await apiClient.get('/api/v1/personal/org-chart')).data,
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  const tree = buildTree(data?.units ?? [])

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div>
          <h1 className="text-3xl font-bold">Organigramm</h1>
          <p className="text-muted-foreground">Organisationsstruktur und Abteilungen</p>
        </div>

        <Card>
          <CardHeader><CardTitle>Organisationsstruktur ({data?.units.length ?? 0} Einheiten)</CardTitle></CardHeader>
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
