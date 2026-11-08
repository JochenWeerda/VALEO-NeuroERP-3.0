import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/** Neuer Lieferschein: Anlage ueber den creation-Block der Belegvariante (DocFlow). Vorher zeigte die Route die Liste. */
export default function LieferungNeuPage(): JSX.Element {
  return <UniversalNativeDetailPage screenId="beleg/sales-delivery" entityId="neu" testId="beleg-sales-delivery" />
}
