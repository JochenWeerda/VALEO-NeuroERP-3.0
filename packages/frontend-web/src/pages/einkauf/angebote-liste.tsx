import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Angebote aus der ScreenDefinition `einkauf/angebote`; Aktionen und Spalten stehen in der Definition. */
export default function AngeboteListePage(): JSX.Element {
  return <NativeListPage screenId="einkauf/angebote" testId="screen-einkauf/angebote" />
}
