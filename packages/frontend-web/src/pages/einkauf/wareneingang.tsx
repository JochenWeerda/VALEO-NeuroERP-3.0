import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Wareneingaenge: Variante `goods-receipt` der Belegliste (DocFlow). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="beleg-liste/goods-receipt" testId="screen-beleg-liste/goods-receipt" />
}
