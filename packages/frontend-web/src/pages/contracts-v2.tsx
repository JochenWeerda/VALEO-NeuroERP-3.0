import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Variante `uebersicht` der Kontraktlisten-Familie (config/mask_families/kontrakt-liste.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="kontrakt-liste/uebersicht" testId="screen-kontrakt-liste/uebersicht" />
}
