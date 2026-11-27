import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

/** Native Cockpit + agrar_workbench: ScreenDefinition agrar/milchvieh-karte */
export default function MilchviehKartePage(): JSX.Element {
  const schema = useScreenDefinition('agrar/milchvieh-karte')
  const permissions = useScreenPermissions(schema.data)
  return (
    <UniversalNativeCockpitPage
      screenId="agrar/milchvieh-karte"
      testId="screen-agrar/milchvieh-karte"
      permissions={permissions}
    />
  )
}
