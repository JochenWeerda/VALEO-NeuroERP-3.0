import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Schadenmeldungen aus der ScreenDefinition `schaeden/liste`; Aktionen und Spalten stehen in der Definition. */
export default function SchaedenListePage(): JSX.Element {
  return <NativeListPage screenId="schaeden/liste" testId="screen-schaeden/liste" />
}
