import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Maschinenauslastung aus der ScreenDefinition `agrar/maschinen-auslastung-liste`. */
export default function AgrarMaschinenAuslastungTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="agrar/maschinen-auslastung-liste" testId="screen-agrar/maschinen-auslastung-liste" />
  )
}
