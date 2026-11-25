import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

/** Native Cockpit + agrar_workbench: ScreenDefinition agrar/kunden-schlagkartei */
export default function KundenSchlagkarteiPage(): JSX.Element {
  const schema = useScreenDefinition('agrar/kunden-schlagkartei')
  const permissions = useScreenPermissions(schema.data)
  return (
    <UniversalNativeCockpitPage
      screenId="agrar/kunden-schlagkartei"
      testId="screen-agrar/kunden-schlagkartei"
      permissions={permissions}
    />
  )
}
