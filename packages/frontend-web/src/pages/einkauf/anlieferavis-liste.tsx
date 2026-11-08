import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Anlieferavis aus der ScreenDefinition `einkauf/anlieferavis-liste`; Aktionen und Spalten stehen in der Definition. */
export default function AnlieferavisListePage(): JSX.Element {
  return <NativeListPage screenId="einkauf/anlieferavis-liste" testId="screen-einkauf/anlieferavis-liste" />
}
