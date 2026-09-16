import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/**
 * Ausgangsrechnung — Kopf, Positionen und die Herkunft der berechneten Menge.
 *
 * Die Maske selbst steht in der ScreenDefinition `sales/invoice`
 * (`app/core/screen_definitions.py`) und entsteht ueber
 * ScreenDefinition -> RenderPlan -> UniversalMaskRenderer. Hier bleibt nur der
 * Einstieg mit der Belegkennung: Wer an der Maske etwas aendern will, aendert
 * die Definition, nicht diese Datei.
 */
export default function RechnungPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="sales/invoice" entityId={id} testId="sales-invoice" />
}
