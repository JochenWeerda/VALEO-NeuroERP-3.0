import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Warengruppen aus der ScreenDefinition `einkauf/warengruppen`; Aktionen und Spalten stehen in der Definition. */
export default function WarengruppenPage(): JSX.Element {
  return <NativeListPage screenId="einkauf/warengruppen" testId="screen-einkauf/warengruppen" />
}
