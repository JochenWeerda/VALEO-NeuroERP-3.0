import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

/** Native admin_workbench: ScreenDefinition admin/control-center/superglue (Batch 28/59). */
export default function AdminControlCenterSupergluePage(): JSX.Element {
  const schema = useScreenDefinition('admin/control-center/superglue')
  const permissions = useScreenPermissions(schema.data)
  return (
    <UniversalNativeCockpitPage
      screenId="admin/control-center/superglue"
      testId="native-cockpit-admin-control-center-superglue"
      permissions={permissions}
    />
  )
}
