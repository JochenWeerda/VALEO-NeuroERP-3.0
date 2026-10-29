import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Stundenzettel aus der ScreenDefinition `personal/stundenzettel-liste`; Aktionen und Spalten stehen in der Definition. */
export default function StundenzettelListePage(): JSX.Element {
  return <NativeListPage screenId="personal/stundenzettel-liste" testId="screen-personal/stundenzettel-liste" />
}
