import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Kontrakte Service aus der ScreenDefinition `einkauf/kontrakte-service-liste`. */
export default function EinkaufKontrakteServiceTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="einkauf/kontrakte-service-liste" testId="screen-einkauf/kontrakte-service-liste" />
  )
}
