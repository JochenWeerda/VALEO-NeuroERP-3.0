import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `versicherungen/liste`; Spalten und Aktionen stehen in der Definition. */
export default function VersicherungenListePage(): JSX.Element {
  return <NativeListPage screenId="versicherungen/liste" testId="screen-versicherungen/liste" />
}
