import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Mitarbeitende aus der ScreenDefinition `personal/mitarbeiter-liste`; Aktionen und Spalten stehen in der Definition. */
export default function MitarbeiterListePage(): JSX.Element {
  return <NativeListPage screenId="personal/mitarbeiter-liste" testId="screen-personal/mitarbeiter-liste" />
}
