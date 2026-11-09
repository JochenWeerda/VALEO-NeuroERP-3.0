import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Webshop-Bestellungen: Studio-Liste; "Als Auftrag anlegen" legt den DocFlow-Auftragsentwurf an. */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="admin/webshop-bestellungen" testId="screen-admin-webshop-bestellungen" />
}
