import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Laborproben aus der ScreenDefinition `labor/proben-liste`; Aktionen und Spalten stehen in der Definition. */
export default function LaborProbenListePage(): JSX.Element {
  return <NativeListPage screenId="labor/proben-liste" testId="screen-labor/proben-liste" />
}
