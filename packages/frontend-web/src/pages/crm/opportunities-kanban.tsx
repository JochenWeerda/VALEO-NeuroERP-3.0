import { NativeListPage } from '@/components/mask-builder/NativeListPage'

/** Verkaufschancen: Studio-Liste `crm/opportunities-liste` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <NativeListPage screenId="crm/opportunities-liste" testId="screen-crm/opportunities-liste" />
}
