import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Gespeicherte Bestellvorschlaege: Variante `gespeichert` der Familie bestellvorschlag (config/mask_families/bestellvorschlag.json). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="bestellvorschlag/gespeichert" testId="screen-bestellvorschlag/gespeichert" />
}
