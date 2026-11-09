import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Variante `engagement-artikel` der Kontraktlisten-Familie (config/mask_families/kontrakt-liste.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="kontrakt-liste/engagement-artikel" testId="screen-kontrakt-liste/engagement-artikel" />
}
