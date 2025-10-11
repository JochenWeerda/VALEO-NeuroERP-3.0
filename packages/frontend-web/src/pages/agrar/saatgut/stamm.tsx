import { useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ObjectPage, type ObjectPageSection } from '@/components/patterns/ObjectPage'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useSeedProduct } from '@/features/agrar/hooks'
import { type SeedProduct } from '@/features/agrar/types'

const formatCurrencyPerKg = (value: number): string =>
  `${value.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} EUR`

const buildKeyInfo = (product: SeedProduct): JSX.Element => (
  <div className="grid gap-4 sm:grid-cols-3">
    <div>
      <p className="text-xs font-semibold text-muted-foreground">Produkt</p>
      <p className="text-sm font-medium">{product.name}</p>
    </div>
    <div>
      <p className="text-xs font-semibold text-muted-foreground">Lieferant</p>
      <p className="text-sm font-medium">{product.supplier}</p>
    </div>
    <div>
      <p className="text-xs font-semibold text-muted-foreground">Status</p>
      <Badge variant={product.status === 'active' ? 'default' : product.status === 'draft' ? 'secondary' : 'outline'}>
        {product.status.toUpperCase()}
      </Badge>
    </div>
  </div>
)

const buildSections = (product: SeedProduct): ObjectPageSection[] => [
  {
    id: 'general',
    label: 'Allgemein',
    content: (
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <p className="text-xs font-semibold text-muted-foreground">Kategorie</p>
          <p className="text-sm font-medium">{product.category}</p>
        </div>
        <div>
          <p className="text-xs font-semibold text-muted-foreground">Saison</p>
          <p className="text-sm font-medium">{product.season}</p>
        </div>
        <div>
          <p className="text-xs font-semibold text-muted-foreground">Varietaet</p>
          <p className="text-sm font-medium">{product.variety}</p>
        </div>
        <div>
          <p className="text-xs font-semibold text-muted-foreground">Forecast</p>
          <p className="text-sm font-medium">{product.forecastTons.toLocaleString('de-DE')} t</p>
        </div>
        <div className="sm:col-span-2">
          <p className="text-xs font-semibold text-muted-foreground">Notizen</p>
          <p className="text-sm">{product.notes ?? 'Keine Notizen hinterlegt.'}</p>
        </div>
      </div>
    ),
  },
  {
    id: 'pricing',
    label: 'Preisstaffeln',
    badge: <Badge variant="secondary">{product.pricing.length} Staffeln</Badge>,
    content: (
      <table className="w-full text-sm">
        <thead>
          <tr className="text-left text-muted-foreground">
            <th className="py-2">Menge (kg)</th>
            <th className="py-2">Preis pro kg</th>
            <th className="py-2">Gueltig bis</th>
          </tr>
        </thead>
        <tbody>
          {product.pricing.map((tier, index) => (
            <tr key={tier.minQuantityKg} className={index > 0 ? 'border-t' : undefined}>
              <td className="py-2">
                {tier.minQuantityKg.toLocaleString('de-DE')}
                {typeof tier.maxQuantityKg === 'number'
                  ? ` - ${tier.maxQuantityKg.toLocaleString('de-DE')}`
                  : ' +'}
              </td>
              <td className="py-2">{formatCurrencyPerKg(tier.pricePerKg)}</td>
              <td className="py-2">{new Date(tier.validUntil).toLocaleDateString('de-DE')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    ),
  },
  {
    id: 'quality',
    label: 'Qualitaet',
    content: (
      <div className="grid gap-4 sm:grid-cols-3">
        <div className="rounded border bg-muted/40 p-4">
          <p className="text-xs text-muted-foreground">Reinheit</p>
          <p className="text-2xl font-semibold">{product.quality.purityPercent}%</p>
        </div>
        <div className="rounded border bg-muted/40 p-4">
          <p className="text-xs text-muted-foreground">Keimfaehigkeit</p>
          <p className="text-2xl font-semibold">{product.quality.germinationPercent}%</p>
        </div>
        <div className="rounded border bg-muted/40 p-4">
          <p className="text-xs text-muted-foreground">Feuchtigkeit</p>
          <p className="text-2xl font-semibold">{product.quality.moisturePercent}%</p>
        </div>
      </div>
    ),
  },
  {
    id: 'licenses',
    label: 'Lizenzen',
    badge: <Badge variant="outline">{product.licenseCount}</Badge>,
    content: (
      <div className="space-y-3 text-sm">
        {product.licenses.map((license) => (
          <div key={license.id} className="rounded border bg-muted/40 px-4 py-3">
            <p className="font-medium">{license.name}</p>
            <p className="text-xs text-muted-foreground">
              Gueltig bis {new Date(license.validUntil).toLocaleDateString('de-DE')}
            </p>
          </div>
        ))}
      </div>
    ),
  },
]

export default function SeedMasterPage(): JSX.Element {
  const [params] = useSearchParams()
  const productId = params.get('id') ?? 'SEED-00123'
  const { data, isLoading, error } = useSeedProduct(productId)

  const sections = useMemo(() => (data ? buildSections(data) : []), [data])

  if (isLoading || data === undefined) {
    return (
      <div className="space-y-4 p-6">
        <Skeleton className="h-12 w-3/4" />
        <Skeleton className="h-48 w-full" />
      </div>
    )
  }

  if (error != null || data === null) {
    return (
      <div className="p-6">
        <div className="rounded border border-destructive/40 bg-destructive/10 p-4 text-sm text-destructive">
          Saatgut-Datensatz konnte nicht geladen werden.
        </div>
      </div>
    )
  }

  return (
    <ObjectPage
      title={`Saatgut ${data.name}`}
      subtitle={data.id}
      keyInfo={buildKeyInfo(data)}
      sections={sections}
      onEdit={() => {
        // placeholder for edit flow
      }}
      mcpContext={{
        pageDomain: 'agrar-saatgut',
        entityType: 'seed-product',
        documentId: data.id,
      }}
    />
  )
}
