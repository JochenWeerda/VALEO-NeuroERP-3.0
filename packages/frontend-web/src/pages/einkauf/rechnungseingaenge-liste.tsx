import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Eingangsrechnungen: Variante `purchase-invoice` der Belegliste (DocFlow, config/mask_families/beleg-liste.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="beleg-liste/purchase-invoice" testId="screen-beleg-liste/purchase-invoice" />
}
