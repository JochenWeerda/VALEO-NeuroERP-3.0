import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Chargen aus der ScreenDefinition `charge/liste`; Aktionen und Spalten stehen in der Definition. */
export default function ChargenListePage(): JSX.Element {
  return <NativeListPage screenId="charge/liste" testId="screen-charge/liste" />
}
