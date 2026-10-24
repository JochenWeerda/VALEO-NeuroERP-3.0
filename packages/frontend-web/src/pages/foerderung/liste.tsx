import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Foerderantraege aus der ScreenDefinition `foerderung/liste`; Aktionen und Spalten stehen in der Definition. */
export default function FoerderungListePage(): JSX.Element {
  return <NativeListPage screenId="foerderung/liste" testId="screen-foerderung/liste" />
}
