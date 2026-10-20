import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `artikel/liste`; Spalten und Aktionen stehen in der Definition. */
export default function ArtikelListePage(): JSX.Element {
  return <NativeListPage screenId="artikel/liste" testId="screen-artikel/liste" />
}
