import { useEffect, useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Table } from '@/components/ui/table'
import { useToast } from '@/hooks/use-toast'

interface AuditEntry {
  ts: number
  from: string
  to: string
  action: string
  user?: string
  reason?: string
}

interface AuditTrailPanelProps {
  domain: 'sales' | 'purchase'
  number: string
}

export default function AuditTrailPanel({ domain, number }: AuditTrailPanelProps) {
  const { toast } = useToast()
  const [entries, setEntries] = useState<AuditEntry[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadAudit()
  }, [domain, number])

  async function loadAudit() {
    try {
      setLoading(true)
      const response = await fetch(`/api/workflow/${domain}/${number}/audit`)
      const data = await response.json()

      if (data.ok) {
        setEntries(data.items || [])
      }
    } catch (e) {
      toast({
        title: 'Fehler beim Laden',
        description: e instanceof Error ? e.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }

  const formatTimestamp = (ts: number) => {
    return new Date(ts * 1000).toLocaleString('de-DE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  const getActionBadge = (action: string) => {
    const variants: Record<string, 'default' | 'secondary' | 'destructive'> = {
      submit: 'secondary',
      approve: 'default',
      reject: 'destructive',
      post: 'default',
    }
    return (
      <Badge variant={variants[action] || 'outline'}>
        {action.toUpperCase()}
      </Badge>
    )
  }

  if (loading) {
    return (
      <Card>
        <CardContent className="pt-6">
          <p className="text-center text-muted-foreground">Lädt Audit-Trail...</p>
        </CardContent>
      </Card>
    )
  }

  if (entries.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Audit-Trail</CardTitle>
          <CardDescription>Verlauf aller Workflow-Änderungen</CardDescription>
        </CardHeader>
        <CardContent>
          <p className="text-center text-muted-foreground py-8">
            Noch keine Workflow-Aktionen
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Audit-Trail</CardTitle>
        <CardDescription>
          Verlauf aller Workflow-Änderungen ({entries.length} Einträge)
        </CardDescription>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {entries.map((entry, idx) => (
            <div
              key={idx}
              className="flex items-center gap-4 p-3 bg-gray-50 rounded-lg border"
              data-testid="audit-entry"
            >
              <div className="flex-1 grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-xs font-medium text-gray-500">Zeitpunkt</p>
                  <p className="text-sm">{formatTimestamp(entry.ts)}</p>
                </div>

                <div>
                  <p className="text-xs font-medium text-gray-500">Aktion</p>
                  <div className="mt-1">{getActionBadge(entry.action)}</div>
                </div>

                <div>
                  <p className="text-xs font-medium text-gray-500">Transition</p>
                  <p className="text-sm">
                    <Badge variant="outline" className="mr-1">
                      {entry.from}
                    </Badge>
                    →
                    <Badge variant="outline" className="ml-1">
                      {entry.to}
                    </Badge>
                  </p>
                </div>

                {entry.user && (
                  <div>
                    <p className="text-xs font-medium text-gray-500">Benutzer</p>
                    <p className="text-sm">{entry.user}</p>
                  </div>
                )}
              </div>

              {entry.reason && (
                <div className="flex-1">
                  <p className="text-xs font-medium text-gray-500">Grund</p>
                  <p className="text-sm italic text-gray-600">{entry.reason}</p>
                </div>
              )}
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

