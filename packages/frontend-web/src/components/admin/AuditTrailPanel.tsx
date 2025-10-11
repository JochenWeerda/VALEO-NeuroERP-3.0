import { useCallback, useEffect, useMemo, useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
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

interface AuditApiResponse {
  ok?: boolean
  items?: AuditEntry[]
}

const ACTION_VARIANTS: Record<string, 'default' | 'secondary' | 'destructive' | 'outline'> = {
  submit: 'secondary',
  approve: 'default',
  reject: 'destructive',
  post: 'default',
  default: 'outline',
}

export default function AuditTrailPanel({ domain, number }: AuditTrailPanelProps): JSX.Element {
  const { toast } = useToast()
  const [entries, setEntries] = useState<AuditEntry[]>([])
  const [loading, setLoading] = useState<boolean>(true)

  const endpoint = useMemo(() => `/api/workflow/${domain}/${number}/audit`, [domain, number])

  const loadAudit = useCallback(async (): Promise<void> => {
    try {
      setLoading(true)
      const response = await fetch(endpoint)
      const data = (await response.json()) as AuditApiResponse

      if (data.ok === true && Array.isArray(data.items)) {
        setEntries(data.items)
      } else {
        setEntries([])
      }
    } catch (error) {
      const description = error instanceof Error ? error.message : 'Unbekannter Fehler'
      toast({
        title: 'Fehler beim Laden',
        description,
        variant: 'destructive',
      })
    } finally {
      setLoading(false)
    }
  }, [endpoint, toast])

  useEffect(() => {
    void loadAudit()
  }, [loadAudit])

  const formatTimestamp = (ts: number): string => {
    return new Date(ts * 1000).toLocaleString('de-DE', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    })
  }

  const getActionBadge = (action: string): JSX.Element => {
    const variant = ACTION_VARIANTS[action] ?? ACTION_VARIANTS.default
    return <Badge variant={variant}>{action.toUpperCase()}</Badge>
  }

  if (loading === true) {
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
          <p className="py-8 text-center text-muted-foreground">Noch keine Workflow-Aktionen</p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Audit-Trail</CardTitle>
        <CardDescription>Verlauf aller Workflow-Änderungen ({entries.length} Einträge)</CardDescription>
      </CardHeader>

      <CardContent>
        <div className="space-y-4">
          {entries.map((entry) => {
            const userName = typeof entry.user === 'string' ? entry.user : ''
            const reason = typeof entry.reason === 'string' ? entry.reason : ''
            const key = `${entry.ts}-${entry.action}-${entry.to}`

            return (
              <div
                key={key}
                className="flex items-center gap-4 rounded-lg border bg-gray-50 p-3"
                data-testid="audit-entry"
              >
                <div className="grid flex-1 grid-cols-2 gap-4 md:grid-cols-4">
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
                    <p className="space-x-1 text-sm">
                      <Badge variant="outline">{entry.from}</Badge>
                      <span>→</span>
                      <Badge variant="outline">{entry.to}</Badge>
                    </p>
                  </div>

                  {userName !== '' && (
                    <div>
                      <p className="text-xs font-medium text-gray-500">Benutzer</p>
                      <p className="text-sm">{userName}</p>
                    </div>
                  )}
                </div>

                {reason !== '' && (
                  <div className="flex-1">
                    <p className="text-xs font-medium text-gray-500">Grund</p>
                    <p className="text-sm italic text-gray-600">{reason}</p>
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </CardContent>
    </Card>
  )
}
