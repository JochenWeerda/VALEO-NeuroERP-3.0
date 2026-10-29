import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Zahlungslaeufe aus der ScreenDefinition `fibu/zahlungslaeufe-liste`. */
export default function FibuZahlungslaeufeTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="fibu/zahlungslaeufe-liste" testId="screen-fibu/zahlungslaeufe-liste" />
  )
}
