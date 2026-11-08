import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Projekte aus der ScreenDefinition `projekte/liste`; Aktionen und Spalten stehen in der Definition. */
export default function ProjekteListePage(): JSX.Element {
  return <NativeListPage screenId="projekte/liste" testId="screen-projekte/liste" />
}
