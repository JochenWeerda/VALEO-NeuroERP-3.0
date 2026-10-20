import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `foerderung/liste`; Spalten und Aktionen stehen in der Definition. */
export default function FoerderAntraegeListePage(): JSX.Element {
  return <NativeListPage screenId="foerderung/liste" testId="screen-foerderung/liste" />
}
