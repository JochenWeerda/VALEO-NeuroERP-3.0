import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `crm/dsgvo-anfragen-liste`; Spalten und Aktionen stehen in der Definition. */
export default function DsgvoAnfragenListePage(): JSX.Element {
  return <NativeListPage screenId="crm/dsgvo-anfragen-liste" testId="screen-crm/dsgvo-anfragen-liste" />
}
