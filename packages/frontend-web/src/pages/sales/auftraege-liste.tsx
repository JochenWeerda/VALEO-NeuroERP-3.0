import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Verkaufsauftraege: Variante `sales-order` der Belegliste (DocFlow, config/mask_families/beleg-liste.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="beleg-liste/sales-order" testId="screen-beleg-liste/sales-order" />
}
