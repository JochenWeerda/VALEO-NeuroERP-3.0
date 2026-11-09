import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Wetterwarnungen: Studio-Liste fuer den Betriebsstandort des Mandanten (vorher fest Emden). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="agrar/wetterwarnung" testId="screen-agrar-wetterwarnung" />
}
