import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Verkaufschancen aus der ScreenDefinition `crm/opportunities-liste`; Zeilen oeffnen die native Objektmaske. */
export default function OpportunitiesListePage(): JSX.Element {
  return <NativeListPage screenId="crm/opportunities-liste" testId="screen-crm/opportunities-liste" />
}
