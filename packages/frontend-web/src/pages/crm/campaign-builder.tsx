import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

/** Kampagne anlegen: Neuanlage ueber den creation-Block der Studio-Maske `crm/campaign`. */
export default function CampaignBuilderPage(): JSX.Element {
  return <UniversalNativeDetailPage screenId="crm/campaign" entityId="neu" testId="crm-campaign-neu" />
}
