import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { AdaptiveWorkspaceLayer } from '@/workspace/AdaptiveWorkspaceLayer'

export default function Page(): JSX.Element {
  return (
    <div className="flex flex-col gap-6" data-testid="adaptive-workspace-home">
      <AdaptiveWorkspaceLayer />
      <section aria-label="Rollen-Cockpit">
        <UniversalNativeCockpitPage
          screenId="start-dashboard"
          testId="start-dashboard"
        />
      </section>
    </div>
  )
}
