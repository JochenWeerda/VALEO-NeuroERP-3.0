import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

/** Native Cockpit + pricing_workbench: ScreenDefinition konditionen/konditionssystem */
export default function KonditionssystemPage(): JSX.Element {
  const schema = useScreenDefinition('konditionen/konditionssystem')
  const permissions = useScreenPermissions(schema.data)
  return (
    <UniversalNativeCockpitPage
      screenId="konditionen/konditionssystem"
      testId="screen-konditionen/konditionssystem"
      permissions={permissions}
    />
  )
}
