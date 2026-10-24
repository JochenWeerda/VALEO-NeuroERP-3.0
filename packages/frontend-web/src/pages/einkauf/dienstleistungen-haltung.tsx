import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Dienstleistungen Haltung aus der ScreenDefinition `einkauf/dienstleistungen-haltung-liste`. */
export default function EinkaufDienstleistungenHaltungTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="einkauf/dienstleistungen-haltung-liste" testId="screen-einkauf/dienstleistungen-haltung-liste" />
  )
}
