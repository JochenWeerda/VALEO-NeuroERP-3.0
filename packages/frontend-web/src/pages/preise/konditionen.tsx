import { useMemo } from 'react'
import { useQuery } from '@tanstack/react-query'
import { apiClient } from '@/lib/api-client'
import { usePriceLists } from '@/lib/api/price-lists'
import { buildPriceWorkspace, formatCurrency } from '@/lib/professional-workspaces'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Skeleton } from '@/components/ui/skeleton'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Save } from 'lucide-react'
import { ErrorState } from '@/components/ErrorState'

type KonditionData = {
  id: string
  kunde: string
  artikel: string
  basispreis: number
  rabatt: number
  skonto: number
  gueltigAb: string
  gueltigBis: string
  status: 'aktiv' | 'abgelaufen'
}

export default function KonditionenPage(): JSX.Element {
  const { data: kondition, isLoading, isError, error, refetch } = useQuery({
    queryKey: ['preise', 'konditionen'],
    queryFn: async () => {
      const response = await apiClient.get<KonditionData>('/api/v1/preise/konditionen')
      return response.data
    },
    staleTime: 5 * 60 * 1000,
  })
  const { data: priceLists = [] } = usePriceLists()

  const workspace = useMemo(() => {
    if (!kondition) return null
    const nettopreis = kondition.basispreis * (1 - kondition.rabatt / 100)
    const tierBreaks = priceLists.flatMap((priceList) =>
      (priceList.items ?? []).map((item) => ({
        minQuantity: Number(item.min_quantity ?? 0),
        maxQuantity: item.max_quantity == null ? undefined : Number(item.max_quantity),
        price: Number(item.unit_price ?? 0),
        discountPercent: Number(item.discount_percent ?? 0),
        sourceLabel: priceList.name,
      })),
    )
    return buildPriceWorkspace({
      listPrice: kondition.basispreis,
      purchasePrice: nettopreis * 0.84,
      agreements: [
        {
          partnerName: kondition.kunde,
          priceNet: nettopreis,
          validFrom: kondition.gueltigAb,
          validTo: kondition.gueltigBis,
        },
      ],
      tierBreaks,
    })
  }, [kondition, priceLists])

  if (isLoading) {
    return (
      <div className="space-y-6 p-3 md:p-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-10 w-64" />
          <Skeleton className="h-10 w-32" />
        </div>
        <Skeleton className="h-80" />
      </div>
    )
  }

  if (isError || !kondition || !workspace) {
    return <ErrorState error={(error as Error) ?? new Error('Konditionen konnten nicht geladen werden')} onRetry={() => { void refetch() }} />
  }

  const nettopreis = kondition.basispreis * (1 - kondition.rabatt / 100)
  const activePriceLists = priceLists.filter((priceList) => priceList.is_active)

  return (
    <div className="space-y-6 p-3 md:p-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Preiskonditionen</h1>
          <p className="text-muted-foreground">{kondition.kunde}</p>
        </div>
        <Button className="gap-2">
          <Save className="h-4 w-4" />
          Speichern
        </Button>
      </div>

      <div className="grid gap-4 lg:grid-cols-4">
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Listenpreis</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{formatCurrency(kondition.basispreis)} / t</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Sonderpreis</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{formatCurrency(nettopreis)} / t</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Aktive Preislisten</CardTitle></CardHeader>
          <CardContent><div className="text-2xl font-bold">{activePriceLists.length}</div></CardContent>
        </Card>
        <Card>
          <CardHeader className="pb-2"><CardTitle className="text-sm font-medium">Preisdruck</CardTitle></CardHeader>
          <CardContent><Badge variant={workspace.pricePressure === 'hoch' ? 'destructive' : 'outline'}>{workspace.pricePressure}</Badge></CardContent>
        </Card>
      </div>

      <Card>
        <CardContent className="grid gap-3 p-6 md:grid-cols-3">
          <div className="rounded-lg border p-4">
            <div className="text-sm text-muted-foreground">Aktive Sonderkonditionen</div>
            <div className="mt-2 text-2xl font-bold">{workspace.activeAgreements}</div>
            <div className="mt-1 text-sm text-muted-foreground">Kunden- oder objektspezifische Preisvereinbarungen</div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-sm text-muted-foreground">Deckungsbeitrag / Einheit</div>
            <div className="mt-2 text-2xl font-bold">{formatCurrency(workspace.marginPerUnit)}</div>
            <div className="mt-1 text-sm text-muted-foreground">Listenpreis minus angenommener Beschaffungskorridor</div>
          </div>
          <div className="rounded-lg border p-4">
            <div className="text-sm text-muted-foreground">Naechste Aktion</div>
            <div className="mt-2 font-semibold">{workspace.nextAction}</div>
            <div className="mt-1 text-sm text-muted-foreground">Preislisten, Marge und Laufzeit zusammen betrachten</div>
          </div>
        </CardContent>
      </Card>

      <Tabs defaultValue="preise">
        <TabsList>
          <TabsTrigger value="preise">Preise</TabsTrigger>
          <TabsTrigger value="konditionen">Konditionen</TabsTrigger>
          <TabsTrigger value="historie">Historie</TabsTrigger>
        </TabsList>

        <TabsContent value="preise">
          <Card>
            <CardHeader>
              <CardTitle>Preisgestaltung - {kondition.artikel}</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Basispreis (EUR/t)</Label>
                  <Input type="number" value={kondition.basispreis} step="0.01" readOnly />
                </div>
                <div>
                  <Label>Rabatt (%)</Label>
                  <Input type="number" value={kondition.rabatt} step="0.1" readOnly />
                </div>
              </div>
              <div className="rounded-lg border bg-muted p-4">
                <div className="flex items-center justify-between">
                  <div>
                    <div className="text-sm text-muted-foreground">Netto-Preis</div>
                    <div className="text-3xl font-bold">{formatCurrency(nettopreis)} / t</div>
                  </div>
                  <Badge variant="outline" className="px-4 py-2 text-lg">-{kondition.rabatt}% Rabatt</Badge>
                </div>
              </div>
              <div className="rounded-lg border p-4">
                <div className="text-sm text-muted-foreground">Preisstory</div>
                <div className="mt-2 grid gap-3 md:grid-cols-3">
                  <div>
                    <div className="text-sm text-muted-foreground">Bester Kundenpreis</div>
                    <div className="font-semibold">{workspace.bestCustomerPrice ? formatCurrency(workspace.bestCustomerPrice) : '-'}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Preislistenpositionen</div>
                    <div className="font-semibold">{workspace.tierBreakCount}</div>
                  </div>
                  <div>
                    <div className="text-sm text-muted-foreground">Aktive Preislisten</div>
                    <div className="font-semibold">{activePriceLists.map((priceList) => priceList.name).slice(0, 2).join(', ') || 'keine'}</div>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="konditionen">
          <Card>
            <CardContent className="space-y-4 pt-6">
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Skonto (%)</Label>
                  <Input type="number" value={kondition.skonto} step="0.1" readOnly />
                </div>
                <div>
                  <Label>Zahlungsziel (Tage)</Label>
                  <Input type="number" value={30} readOnly />
                </div>
              </div>
              <div className="grid gap-4 sm:grid-cols-2">
                <div>
                  <Label>Gueltig ab</Label>
                  <Input type="date" value={kondition.gueltigAb} readOnly />
                </div>
                <div>
                  <Label>Gueltig bis</Label>
                  <Input type="date" value={kondition.gueltigBis} readOnly />
                </div>
              </div>
              <div>
                <Label>Status</Label>
                <div className="mt-2 flex items-center gap-3">
                  <Badge variant={kondition.status === 'aktiv' ? 'outline' : 'destructive'}>
                    {kondition.status === 'aktiv' ? 'Aktiv' : 'Abgelaufen'}
                  </Badge>
                  <span className="text-sm text-muted-foreground">{workspace.nextAction}</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="historie">
          <Card>
            <CardContent className="space-y-3 pt-6">
              <div className="rounded-lg border p-4">
                <div className="font-medium">Aktuelle Vereinbarung</div>
                <div className="text-sm text-muted-foreground">{kondition.kunde} fuer {kondition.artikel}</div>
                <div className="mt-2 text-sm text-muted-foreground">{kondition.gueltigAb} bis {kondition.gueltigBis}</div>
              </div>
              {activePriceLists.slice(0, 3).map((priceList) => (
                <div key={priceList.id} className="rounded-lg border p-4">
                  <div className="font-medium">{priceList.name}</div>
                  <div className="text-sm text-muted-foreground">{priceList.description || 'Aktive Preisliste ohne Zusatzbeschreibung'}</div>
                  <div className="mt-2 text-sm text-muted-foreground">{priceList.item_count} Positionen</div>
                </div>
              ))}
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
