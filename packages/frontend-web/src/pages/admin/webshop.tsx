import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Webshop-Anbindungen: Studio-Liste mit Anbinden und Entfernen als Kommandowege. */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="admin/webshop" testId="screen-admin-webshop" />
}
