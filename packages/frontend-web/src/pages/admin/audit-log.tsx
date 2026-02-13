import { useState } from 'react'
import { useAuditLog, type AuditEntry } from '@/lib/api/admin'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { DataTable } from '@/components/ui/data-table'
import { Input } from '@/components/ui/input'
import { Skeleton } from '@/components/ui/skeleton'
import { FileDown, FileText, Search } from 'lucide-react'

export default function AuditLogPage(): JSX.Element {
  const { data: items, isLoading } = useAuditLog()
  const [searchTerm, setSearchTerm] = useState('')

  if (isLoading) return (
    <div className="p-3 md:p-6 space-y-4">
      <Skeleton className="h-8 w-64" />
      <Skeleton className="h-[400px] w-full" />
    </div>
  )

  const list = items ?? []

  const columns = [
    {
      key: 'zeitstempel' as const,
      label: 'Zeitstempel',
      render: (a: AuditEntry) => <span className="font-mono text-sm">{a.zeitstempel}</span>,
    },
    { key: 'benutzer' as const, label: 'Benutzer' },
    { key: 'aktion' as const, label: 'Aktion' },
    { key: 'objekt' as const, label: 'Objekt', render: (a: AuditEntry) => <span className="font-mono">{a.objekt}</span> },
    {
      key: 'status' as const,
      label: 'Status',
      render: (a: AuditEntry) => (
        <Badge variant={a.status === 'erfolg' ? 'outline' : 'destructive'}>
          {a.status === 'erfolg' ? 'Erfolg' : 'Fehler'}
        </Badge>
      ),
    },
  ]

  return (
    <div className="space-y-4 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Audit-Log</h1>
          <p className="text-muted-foreground">System-Aktivitäten</p>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Einträge Heute</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              <FileText className="h-5 w-5 text-blue-600" />
              <span className="text-2xl font-bold">{list.length}</span>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Erfolgreiche Aktionen</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-green-600">{list.filter((a) => a.status === 'erfolg').length}</span>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Fehler</CardTitle>
          </CardHeader>
          <CardContent>
            <span className="text-2xl font-bold text-red-600">{list.filter((a) => a.status === 'fehler').length}</span>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Suche & Filter</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex gap-4">
            <div className="relative flex-1">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <Input placeholder="Suche..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="pl-10" />
            </div>
            <Button variant="outline" className="gap-2">
              <FileDown className="h-4 w-4" />
              Export
            </Button>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardContent className="pt-6">
          <DataTable data={list} columns={columns} />
        </CardContent>
      </Card>
    </div>
  )
}
