import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Variante `abrechnung` der Kontraktlisten-Familie (config/mask_families/kontrakt-liste.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="kontrakt-liste/abrechnung" testId="screen-kontrakt-liste/abrechnung" />
}
