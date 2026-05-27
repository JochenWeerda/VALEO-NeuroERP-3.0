import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { ErrorState } from '@/components/ErrorState'
import { apiClient } from '@/lib/api-client'
import { Plus, ShoppingCart, Download } from 'lucide-react'

type Connector = {
  id: string
  name: string
  platform: 'SHOPWARE6' | 'WOOCOMMERCE' | 'SHOPIFY' | 'MAGENTO' | 'CUSTOM'
  base_url: string
  api_key_masked: string
  aktiv: boolean
}

const PLATFORM_VARIANT: Record<string, 'default' | 'secondary' | 'outline'> = {
  SHOPWARE6: 'default',
  WOOCOMMERCE: 'secondary',
  SHOPIFY: 'default',
  MAGENTO: 'outline',
  CUSTOM: 'outline',
}

export default function WebshopPage(): JSX.Element {
  const queryClient = useQueryClient()
  const [importResult, setImportResult] = useState<Record<string, number>>({})

  const { data: connectors = [], isError, error, refetch } = useQuery<Connector[]>({
    queryKey: ['webshop-connectors'],
    queryFn: async () => (await apiClient.get<Connector[]>('/api/v1/webshop/connectors')).data,
  })

  const importMutation = useMutation({
    mutationFn: async (connectorId: string) =>
      (await apiClient.post<{ imported_count: number }>('/api/v1/webshop/orders/import', { connector_id: connectorId })).data,
    onSuccess: (data, connectorId) => {
      setImportResult((prev) => ({ ...prev, [connectorId]: data.imported_count }))
      void queryClient.invalidateQueries({ queryKey: ['webshop-connectors'] })
    },
  })

  if (isError) return <ErrorState error={error as Error} onRetry={() => { void refetch() }} />

  return (
    <div className="flex flex-col">
      <div className="space-y-4 p-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Webshop-Integration</h1>
            <p className="text-muted-foreground">Shop-Connectors und Bestellimport verwalten</p>
          </div>
          <Button className="gap-2"><Plus className="h-4 w-4" />Connector hinzufügen</Button>
        </div>

        {connectors.length === 0 && (
          <Card>
            <CardContent className="py-8 text-center text-muted-foreground">
              <ShoppingCart className="mx-auto h-10 w-10 mb-2" />
              <p>Keine Connectors konfiguriert. Fügen Sie einen Webshop-Connector hinzu.</p>
            </CardContent>
          </Card>
        )}

        <div className="grid gap-4 md:grid-cols-2">
          {connectors.map((c) => (
            <Card key={c.id}>
              <CardHeader>
                <div className="flex items-center justify-between">
                  <CardTitle className="text-base">{c.name}</CardTitle>
                  <div className="flex items-center gap-2">
                    <Badge variant={PLATFORM_VARIANT[c.platform] ?? 'outline'}>{c.platform}</Badge>
                    <Badge variant={c.aktiv ? 'success' : 'secondary'}>{c.aktiv ? 'Aktiv' : 'Inaktiv'}</Badge>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <dl className="space-y-1 text-sm">
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">URL</dt>
                    <dd className="font-mono">{c.base_url}</dd>
                  </div>
                  <div className="flex justify-between">
                    <dt className="text-muted-foreground">API-Key</dt>
                    <dd className="font-mono">{c.api_key_masked}</dd>
                  </div>
                </dl>
                <div className="mt-3 flex items-center gap-2">
                  <Button
                    size="sm"
                    variant="outline"
                    className="gap-1"
                    onClick={() => importMutation.mutate(c.id)}
                    disabled={importMutation.isPending}
                  >
                    <Download className="h-3 w-3" />Bestellungen importieren
                  </Button>
                  {importResult[c.id] !== undefined && (
                    <span className="text-sm text-[hsl(var(--color-semantic-success-700-hsl))]">{importResult[c.id]} importiert</span>
                  )}
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </div>
  )
}
