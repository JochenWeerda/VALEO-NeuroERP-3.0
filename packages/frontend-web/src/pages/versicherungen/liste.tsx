import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Versicherungen aus der ScreenDefinition `versicherungen/liste`; Aktionen und Spalten stehen in der Definition. */
export default function VersicherungenListePage(): JSX.Element {
  return <NativeListPage screenId="versicherungen/liste" testId="screen-versicherungen/liste" />
}
