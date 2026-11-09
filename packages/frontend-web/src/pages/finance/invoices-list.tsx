import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Ausgangsrechnungen: Variante `sales-invoice` der Belegliste (DocFlow). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="beleg-liste/sales-invoice" testId="screen-beleg-liste/sales-invoice" />
}
