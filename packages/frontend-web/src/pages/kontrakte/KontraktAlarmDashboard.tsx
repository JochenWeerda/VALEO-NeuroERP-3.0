import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Variante `alarme` der Kontraktlisten-Familie (config/mask_families/kontrakt-liste.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="kontrakt-liste/alarme" testId="screen-kontrakt-liste/alarme" />
}
