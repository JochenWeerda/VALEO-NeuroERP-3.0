import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Verkaufsangebote: Variante `sales-offer` der Belegliste (DocFlow, config/mask_families/beleg-liste.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="beleg-liste/sales-offer" testId="screen-beleg-liste/sales-offer" />
}
