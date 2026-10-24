import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Kontakt-Management aus der ScreenDefinition `crm/kontakt-management-liste`. */
export default function CrmKontaktManagementTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="crm/kontakt-management-liste" testId="screen-crm/kontakt-management-liste" />
  )
}
