import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `crm/kampagnen-liste`; Spalten und Aktionen stehen in der Definition. */
export default function KampagnenListePage(): JSX.Element {
  return <NativeListPage screenId="crm/kampagnen-liste" testId="screen-crm/kampagnen-liste" />
}
