import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `crm/kampagnenvorlagen-liste`; Spalten und Aktionen stehen in der Definition. */
export default function KampagnenvorlagenListePage(): JSX.Element {
  return <NativeListPage screenId="crm/kampagnenvorlagen-liste" testId="screen-crm/kampagnenvorlagen-liste" />
}
