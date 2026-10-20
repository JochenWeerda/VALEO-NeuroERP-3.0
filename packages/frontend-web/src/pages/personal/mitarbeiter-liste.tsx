import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `personal/mitarbeiter-liste`; Spalten und Aktionen stehen in der Definition. */
export default function MitarbeiterListePage(): JSX.Element {
  return <NativeListPage screenId="personal/mitarbeiter-liste" testId="screen-personal/mitarbeiter-liste" />
}
