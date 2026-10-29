import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Kunden aus der ScreenDefinition `crm/kunden-liste`. */
export default function CrmKundenListeTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="crm/kunden-liste" testId="screen-crm/kunden-liste" />
  )
}
