import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `crm/segmente-liste`; Spalten und Aktionen stehen in der Definition. */
export default function SegmenteListePage(): JSX.Element {
  return <NativeListPage screenId="crm/segmente-liste" testId="screen-crm/segmente-liste" />
}
