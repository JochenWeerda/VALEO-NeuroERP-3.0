import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Intrastat-Meldung aus der ScreenDefinition `export/intrastat-meldung-liste`. */
export default function ExportIntrastatMeldungTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="export/intrastat-meldung-liste" testId="screen-export/intrastat-meldung-liste" />
  )
}
