import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** USt-Voranmeldung aus der ScreenDefinition `export/umsatzsteuer-voranmeldung-liste`. */
export default function ExportUmsatzsteuerVoranmeldungTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="export/umsatzsteuer-voranmeldung-liste" testId="screen-export/umsatzsteuer-voranmeldung-liste" />
  )
}
