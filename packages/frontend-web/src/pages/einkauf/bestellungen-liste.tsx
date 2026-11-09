import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Bestellungen: Variante `purchase-order` der Belegliste (DocFlow, config/mask_families/beleg-liste.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="beleg-liste/purchase-order" testId="screen-beleg-liste/purchase-order" />
}
