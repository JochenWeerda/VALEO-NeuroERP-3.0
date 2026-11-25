import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

/** Native admin_workbench: ScreenDefinition admin/control-center/agent-ops (Batch 28/59). */
export default function AdminControlCenterAgentOpsPage(): JSX.Element {
  const schema = useScreenDefinition('admin/control-center/agent-ops')
  const permissions = useScreenPermissions(schema.data)
  return (
    <UniversalNativeCockpitPage
      screenId="admin/control-center/agent-ops"
      testId="native-cockpit-admin-control-center-agent-ops"
      permissions={permissions}
    />
  )
}
