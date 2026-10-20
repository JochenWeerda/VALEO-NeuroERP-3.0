import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `schaeden/liste`; Spalten und Aktionen stehen in der Definition. */
export default function SchaedenListePage(): JSX.Element {
  return <NativeListPage screenId="schaeden/liste" testId="screen-schaeden/liste" />
}
