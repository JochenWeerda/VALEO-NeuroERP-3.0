import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

/** Native Cockpit + lager_workbench: ScreenDefinition lager/materialfluss */
export default function MaterialflussPage(): JSX.Element {
  const schema = useScreenDefinition('lager/materialfluss')
  const permissions = useScreenPermissions(schema.data)
  return (
    <UniversalNativeCockpitPage
      screenId="lager/materialfluss"
      testId="screen-lager/materialfluss"
      permissions={permissions}
    />
  )
}
