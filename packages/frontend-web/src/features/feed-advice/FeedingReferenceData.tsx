import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'

/**
 * Thin route adapter only. Data loading, responsive states and table behavior
 * remain governed by the native ScreenDefinition runtime.
 */
export function FeedingReferenceData(): JSX.Element {
  return (
    <UniversalNativeCockpitPage
      screenId="agrar/feeding-reference-data"
      testId="feeding-reference-data"
      permissions={['futtermittel.rations.update']}
    />
  )
}
