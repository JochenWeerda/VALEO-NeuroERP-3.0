/**
 * Quadriga-Connector – Konfiguration und Sync für Quadriga-Anbindung.
 */

import { useState, useEffect } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Switch } from '@/components/ui/switch'
import { LayoutGrid, Save, RefreshCw, ArrowRightLeft } from 'lucide-react'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

type ConnectorConfig = {
  id: string
  tenant_id: string
  connector_code: string
  name?: string
  config_json: Record<string, unknown>
  is_active: boolean
  created_at: string
  updated_at: string
}

function useQuadrigaConfig() {
  return useQuery({
    queryKey: ['finance', 'quadriga-connector', 'config'],
    queryFn: async () => {
      return await apiClient.get<ConnectorConfig | null>('/api/v1/finance/quadriga-connector/config')
    },
  })
}

export default function QuadrigaConnectorPage(): JSX.Element {
  const { toast } = useToast()
  const qc = useQueryClient()
  const { data: config, isLoading } = useQuadrigaConfig()
  const [name, setName] = useState('Quadriga')
  const [endpoint, setEndpoint] = useState('')
  const [isActive, setIsActive] = useState(true)
  const [syncing, setSyncing] = useState(false)

  useEffect(() => {
    if (config) {
      setName(config.name ?? 'Quadriga')
      setIsActive(config.is_active)
      const c = config.config_json as Record<string, string>
      setEndpoint(c?.endpoint_url ?? '')
    }
  }, [config])

  const saveMutation = useMutation({
    mutationFn: async () => {
      await apiClient.put('/api/v1/finance/quadriga-connector/config', {
        name,
        config_json: { endpoint_url: endpoint },
        is_active: isActive,
      })
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['finance', 'quadriga-connector', 'config'] })
      toast({ title: 'Gespeichert', description: 'Quadriga-Konfiguration wurde gespeichert.' })
    },
    onError: (e: Error) => {
      toast({ title: 'Fehler', description: e.message, variant: 'destructive' })
    },
  })

  const syncMutation = useMutation({
    mutationFn: async (direction: 'export' | 'import') => {
      return await apiClient.post<{ success: boolean; message: string }>('/api/v1/finance/quadriga-connector/sync', {
        direction,
        options: {},
      })
    },
    onMutate: () => setSyncing(true),
    onSettled: () => setSyncing(false),
    onSuccess: (data) => {
      toast({ title: 'Sync', description: data.message })
    },
    onError: (e: Error) => {
      toast({ title: 'Fehler', description: e.message, variant: 'destructive' })
    },
  })

  return (
    <div className="p-6 max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-3">
        <LayoutGrid className="h-8 w-8 text-primary" />
        <div>
          <h1 className="text-2xl font-bold">Quadriga-Connector</h1>
          <p className="text-muted-foreground text-sm">Anbindung an Quadriga-Systeme – Konfiguration und Sync</p>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Konfiguration</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label>Bezeichnung</Label>
            <Input value={name} onChange={(e) => setName(e.target.value)} placeholder="Quadriga" />
          </div>
          <div className="space-y-2">
            <Label>Endpoint-URL (optional)</Label>
            <Input
              value={endpoint}
              onChange={(e) => setEndpoint(e.target.value)}
              placeholder="https://…"
            />
          </div>
          <div className="flex items-center justify-between">
            <Label>Connector aktiv</Label>
            <Switch checked={isActive} onCheckedChange={setIsActive} />
          </div>
          <Button onClick={() => saveMutation.mutate()} disabled={saveMutation.isPending} className="gap-2">
            <Save className="h-4 w-4" /> Speichern
          </Button>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle className="text-base">Sync</CardTitle>
        </CardHeader>
        <CardContent className="flex flex-wrap gap-4">
          <Button
            variant="outline"
            onClick={() => syncMutation.mutate('export')}
            disabled={syncing || isLoading || !config?.is_active}
            className="gap-2"
          >
            <ArrowRightLeft className="h-4 w-4" /> Export zu Quadriga
          </Button>
          <Button
            variant="outline"
            onClick={() => syncMutation.mutate('import')}
            disabled={syncing || isLoading || !config?.is_active}
            className="gap-2"
          >
            <RefreshCw className="h-4 w-4" /> Import von Quadriga
          </Button>
        </CardContent>
      </Card>

      {!config && !isLoading && (
        <p className="text-sm text-muted-foreground">
          Noch keine Konfiguration vorhanden. Bezeichnung setzen und „Speichern“ klicken, um eine Konfiguration anzulegen.
        </p>
      )}
    </div>
  )
}
