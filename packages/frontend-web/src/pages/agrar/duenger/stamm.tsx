import { useMemo } from 'react'
import { useSearchParams } from 'react-router-dom'
import { ObjectPage, type ObjectPageSection } from '@/components/patterns/ObjectPage'
import { Badge } from '@/components/ui/badge'
import { Skeleton } from '@/components/ui/skeleton'
import { useFertilizerProduct } from '@/features/agrar/hooks'
import { type FertilizerProduct } from '@/features/agrar/types'

const buildKeyInfo = (product: FertilizerProduct): JSX.Element => (
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
      <p className="text-xs font-semibold text-muted-foreground">Bestand</p>
      <p className="text-sm font-medium">{product.stockTons.toLocaleString('de-DE')} t</p>
    </div>
  </div>
)

const buildSections = (product: FertilizerProduct): ObjectPageSection[] => [
  {
    id: 'general',
    label: 'Allgemein',
    content: (
      <div className="grid gap-4 sm:grid-cols-2">
        <div>
          <p className="text-xs font-semibold text-muted-foreground">Produktgruppe</p>
          <p className="text-sm font-medium">{product.productGroup}</p>
        </div>
        <div>
          <p className="text-xs font-semibold text-muted-foreground">Status</p>
          <Badge variant={product.status === 'active' ? 'default' : 'secondary'}>{product.status.toUpperCase()}</Badge>
        </div>
        <div>
          <p className="text-xs font-semibold text-muted-foreground">Angelegt</p>
          <p className="text-sm font-medium">{new Date(product.createdAt).toLocaleDateString('de-DE')}</p>
        </div>
        <div>
          <p className="text-xs font-semibold text-muted-foreground">Aktualisiert</p>
          <p className="text-sm font-medium">{new Date(product.updatedAt).toLocaleDateString('de-DE')}</p>
        </div>
      </div>
    ),
  },
  {
    id: 'composition',
    label: 'Zusammensetzung',
    content: (
      <div className="space-y-3">
        {product.composition.map((item) => (
          <div key={item.label} className="flex items-center justify-between rounded border bg-muted/40 px-4 py-3">
            <span className="text-sm font-medium">{item.label}</span>
            <span className="text-sm">{item.percentage}%</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'pricing',
    label: 'Preisstaffeln',
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
              <td className="py-2">
                {tier.pricePerKg.toLocaleString('de-DE', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} EUR
              </td>
              <td className="py-2">{new Date(tier.validUntil).toLocaleDateString('de-DE')}</td>
            </tr>
          ))}
        </tbody>
      </table>
    ),
  },
]

export default function FertilizerMasterPage(): JSX.Element {
  const [params] = useSearchParams()
  const productId = params.get('id') ?? 'FERT-2007'
  const { data, isLoading, error } = useFertilizerProduct(productId)

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
          Duenger-Datensatz konnte nicht geladen werden.
        </div>
      </div>
    )
  }

  return (
    <ObjectPage
      title={`Duenger ${data.name}`}
      subtitle={data.id}
      keyInfo={buildKeyInfo(data)}
      sections={sections}
      mcpContext={{
        pageDomain: 'agrar-duenger',
        entityType: 'fertilizer-product',
        documentId: data.id,
      }}
    />
  )
}
