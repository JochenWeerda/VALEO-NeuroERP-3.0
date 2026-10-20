import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Liste aus der ScreenDefinition `charge/liste`; Spalten und Aktionen stehen in der Definition. */
export default function ChargenListePage(): JSX.Element {
  return <NativeListPage screenId="charge/liste" testId="screen-charge/liste" />
}
