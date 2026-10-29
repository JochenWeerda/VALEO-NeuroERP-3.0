import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Lieferanten aus der ScreenDefinition `crm/lieferanten-liste`. */
export default function CrmLieferantenListeTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="crm/lieferanten-liste" testId="screen-crm/lieferanten-liste" />
  )
}
