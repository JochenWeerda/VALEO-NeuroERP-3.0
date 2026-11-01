import { useParams } from '@/app/routing/typed-router'
import { createStammNativeDetailPage, isStammCreationEntityId } from '@/components/mask-builder'
import { InvoiceCapturePage } from '@/pages/finance/InvoiceCapturePage'

/** Existing incoming invoices open their detail; only a new invoice uses the capture form. */
const RechnungseingangDetailPage = createStammNativeDetailPage(
  'finance/ap-invoice',
  'einkauf-rechnungseingang',
  () => import('./rechnungseingang-legacy'),
)

export default function RechnungseingangPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  if (isStammCreationEntityId(id)) return <InvoiceCapturePage purchase />
  return <RechnungseingangDetailPage />
}
