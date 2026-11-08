import { useParams, useSearchParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/**
 * Einstieg der alten Belegrouten in die Belegmaske (BELEG-052, 08.11.2026: DocFlow einziger Belegspeicher).
 *
 * Jede fruehere Erfassungs- oder Detailseite (Angebot, Auftrag, Lieferschein, Rechnung, Gutschrift, Bestellung,
 * Wareneingang, Eingangsrechnung, Einkaufsgutschrift) oeffnet die Variante ihrer Belegart: mit `:id` bzw. `?id=`
 * den Beleg, sonst die Neuanlage ueber den creation-Block. Die Maske steht in der versionierten Belegfamilie.
 */
export function belegSeite(belegart: string): () => JSX.Element {
  const variante = belegart.replace(/_/g, '-')
  return function BelegSeite(): JSX.Element {
    const { id } = useParams<{ id?: string }>()
    const [suche] = useSearchParams()
    const kennung = id ?? suche.get('id') ?? 'neu'
    return <UniversalNativeDetailPage screenId={`beleg/${variante}`} entityId={kennung} testId={`beleg-${variante}`} />
  }
}
