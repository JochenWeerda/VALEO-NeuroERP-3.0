import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Kontakte aus der ScreenDefinition `crm/contact-detail-liste`. */
export default function CrmContactDetailTsxPage(): JSX.Element {
  return (
    <NativeListPage screenId="crm/contact-detail-liste" testId="screen-crm/contact-detail-liste" />
  )
}
