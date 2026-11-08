import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Leads aus der ScreenDefinition `crm/leads-liste`. */
export default function CrmLeadDetailTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="crm/leads-liste" testId="screen-crm/leads-liste" />
  )
}
