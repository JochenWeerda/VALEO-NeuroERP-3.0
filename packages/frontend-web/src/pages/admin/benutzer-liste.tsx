import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `admin/benutzer-liste`; Spalten und Aktionen stehen in der Definition. */
export default function BenutzerListePage(): JSX.Element {
  return <NativeListPage screenId="admin/benutzer-liste" testId="screen-admin/benutzer-liste" />
}
