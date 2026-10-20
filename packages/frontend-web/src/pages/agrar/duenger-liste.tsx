import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Duenger aus der ScreenDefinition `agrar/duenger-liste`; Zeilen oeffnen die native Objektmaske `agrar/duenger`. */
export default function DuengerListePage(): JSX.Element {
  return <NativeListPage screenId="agrar/duenger-liste" testId="screen-agrar/duenger-liste" />
}
