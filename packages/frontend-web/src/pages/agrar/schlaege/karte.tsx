import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Schlagkarte aus der ScreenDefinition `agrar/schlaege-karte-liste`. */
export default function AgrarSchlaegeKarteTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="agrar/schlaege-karte-liste" testId="screen-agrar/schlaege-karte-liste" />
  )
}
