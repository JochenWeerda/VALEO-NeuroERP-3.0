import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `personal/stundenzettel-liste`; Spalten und Aktionen stehen in der Definition. */
export default function StundenzettelListePage(): JSX.Element {
  return <NativeListPage screenId="personal/stundenzettel-liste" testId="screen-personal/stundenzettel-liste" />
}
