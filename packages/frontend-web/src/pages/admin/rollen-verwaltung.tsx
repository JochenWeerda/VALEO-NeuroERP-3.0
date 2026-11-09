import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Rollen: Studio-Liste mit Anlegen, Aendern und Entfernen; auch der alte Einstieg /admin/rolle/neu landet hier. */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="admin/rollen-verwaltung" testId="screen-admin-rollen-verwaltung" />
}
