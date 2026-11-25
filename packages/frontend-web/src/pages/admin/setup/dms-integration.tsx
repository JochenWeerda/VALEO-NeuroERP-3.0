import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

/** Native admin_workbench: ScreenDefinition admin/setup/dms-integration (Batch 28b/57). */
export default function Page(): JSX.Element {
  const schema = useScreenDefinition('admin/setup/dms-integration')
  const permissions = useScreenPermissions(schema.data)
  return (
    <UniversalNativeCockpitPage
      screenId="admin/setup/dms-integration"
      testId="native-cockpit-admin-setup-dms-integration"
      permissions={permissions}
    />
  )
}
