import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Lieferscheine: Variante `sales-delivery` der Belegliste (DocFlow, config/mask_families/beleg-liste.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="beleg-liste/sales-delivery" testId="screen-beleg-liste/sales-delivery" />
}
