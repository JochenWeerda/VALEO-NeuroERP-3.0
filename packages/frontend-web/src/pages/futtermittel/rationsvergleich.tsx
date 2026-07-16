import { useLocation } from '@/app/routing/typed-router'
import { RationComparison } from '@/features/feed-advice/RationComparison'

/** Variantenvergleich-Route (FEED-EDITOR-023): ?base=…&variant=… */
export default function RationsVergleichPage(): JSX.Element {
  const location = useLocation()
  const params = new URLSearchParams(location.search)
  const base = params.get('base')
  const variant = params.get('variant')

  if (!base || !variant) {
    return (
      <div className="p-6">
        <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground" role="status">
          Für den Vergleich zwei Versionen wählen (Aufruf mit <code>?base=…&amp;variant=…</code>).
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <RationComparison baseVersionId={base} variantVersionId={variant} />
    </div>
  )
}
