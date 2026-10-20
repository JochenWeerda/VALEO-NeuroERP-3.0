import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Anfragen aus der ScreenDefinition `einkauf/anfragen`; Aktionen und Spalten stehen in der Definition. */
export default function AnfragenListePage(): JSX.Element {
  return <NativeListPage screenId="einkauf/anfragen" testId="screen-einkauf/anfragen" />
}
