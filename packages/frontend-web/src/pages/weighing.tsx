import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

/** Waagen: Studio-Maske `waage/liste` (vorher eine screenId ohne ScreenDefinition). */
export default function Page(): JSX.Element {
  return <UniversalNativeCockpitPage screenId="waage/liste" testId="screen-waage/liste" />
}
