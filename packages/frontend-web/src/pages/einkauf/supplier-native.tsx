import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/** Lieferantenstamm als Studio-Maske (``einkauf/supplier``); ohne ID (``/einkauf/lieferant/neu``) die Anlage. */
export default function SupplierNativePage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="einkauf/supplier" entityId={id ?? 'neu'} testId="einkauf-supplier" />
}
