import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

/** Kampagnen-Performance: Studio-Maske `crm/campaign-performance` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <UniversalNativeCockpitPage screenId="crm/campaign-performance" testId="screen-crm/campaign-performance" />
}
