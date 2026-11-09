import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Saatgut-Bestellungen: Studio-Liste `agrar/saatgut-bestellungen-liste` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="agrar/saatgut-bestellungen-liste" testId="screen-agrar/saatgut-bestellungen-liste" />
}
