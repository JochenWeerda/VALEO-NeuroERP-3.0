import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Marketingkampagnen fuehrt das CRM (domain_crm.crm_campaigns, Nutzerentscheidung 04.11.2026). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="crm/kampagnen-liste" testId="screen-marketing/kampagnen" />
}
