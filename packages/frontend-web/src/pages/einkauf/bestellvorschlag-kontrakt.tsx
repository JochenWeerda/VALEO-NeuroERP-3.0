import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Bestellvorschlag aus Kontrakten: Variante `rohware` der Familie bestellvorschlag (config/mask_families/bestellvorschlag.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="bestellvorschlag/rohware" testId="screen-bestellvorschlag/rohware" />
}
