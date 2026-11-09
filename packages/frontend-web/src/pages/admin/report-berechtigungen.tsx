import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Report-Berechtigungen: Studio-Liste mit Anlegen, Aendern und Entfernen als Admin-Kommandowege. */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="admin/report-berechtigungen" testId="screen-admin-report-berechtigungen" />
}
