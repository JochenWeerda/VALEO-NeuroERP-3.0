import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Einkaufsgutschriften: Variante `purchase-credit-memo` der Belegliste (DocFlow, config/mask_families/beleg-liste.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="beleg-liste/purchase-credit-memo" testId="screen-beleg-liste/purchase-credit-memo" />
}
