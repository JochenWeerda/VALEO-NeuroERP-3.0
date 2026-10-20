import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `crm/einwilligungen-liste`; Spalten und Aktionen stehen in der Definition. */
export default function EinwilligungenListePage(): JSX.Element {
  return <NativeListPage screenId="crm/einwilligungen-liste" testId="screen-crm/einwilligungen-liste" />
}
