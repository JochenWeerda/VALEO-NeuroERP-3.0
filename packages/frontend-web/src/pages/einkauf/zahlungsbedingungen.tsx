import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Zahlungsbedingungen aus der ScreenDefinition `einkauf/zahlungsbedingungen`; Aktionen stehen in der Definition. */
export default function ZahlungsbedingungenPage(): JSX.Element {
  return <NativeListPage screenId="einkauf/zahlungsbedingungen" testId="screen-einkauf/zahlungsbedingungen" />
}
