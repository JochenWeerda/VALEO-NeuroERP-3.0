import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Rechnungseingaenge aus der ScreenDefinition `einkauf/rechnungseingaenge-liste`. */
export default function EinkaufRechnungseingaengeListeTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="einkauf/rechnungseingaenge-liste" testId="screen-einkauf/rechnungseingaenge-liste" />
  )
}
