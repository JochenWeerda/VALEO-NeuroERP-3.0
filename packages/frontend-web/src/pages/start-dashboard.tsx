import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { AdaptiveWorkspaceLayer } from '@/workspace/AdaptiveWorkspaceLayer'

export default function Page(): JSX.Element {
  const [rolesOpen, setRolesOpen] = useState(false)
  return (
    <div className="flex flex-col gap-6" data-testid="adaptive-workspace-home">
      <AdaptiveWorkspaceLayer />
      <section aria-label="Rollen-Cockpit" className="rounded-lg border border-border bg-card p-4">
        <Button variant="ghost" aria-expanded={rolesOpen} aria-controls="role-workspace-content" onClick={() => setRolesOpen(value => !value)}>
          Weitere Rollen-Arbeitsbereiche {rolesOpen ? 'schließen' : 'öffnen'}
        </Button>
        {rolesOpen ? <div id="role-workspace-content" className="mt-3">
        <UniversalNativeCockpitPage
          screenId="start-dashboard"
          testId="start-dashboard"
        />
        </div> : null}
      </section>
    </div>
  )
}
