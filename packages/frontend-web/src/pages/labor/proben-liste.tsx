import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `labor/proben-liste`; Spalten und Aktionen stehen in der Definition. */
export default function LaborProbenListePage(): JSX.Element {
  return <NativeListPage screenId="labor/proben-liste" testId="screen-labor/proben-liste" />
}
