import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `projekte/liste`; Spalten und Aktionen stehen in der Definition. */
export default function ProjekteListePage(): JSX.Element {
  return <NativeListPage screenId="projekte/liste" testId="screen-projekte/liste" />
}
