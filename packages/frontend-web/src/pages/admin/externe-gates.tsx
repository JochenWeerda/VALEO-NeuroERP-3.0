import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

/** Native Cockpit: ScreenDefinition admin/externe-gates (Batch 28). */
export default function ExterneGatesPage(): JSX.Element {
  const schema = useScreenDefinition('admin/externe-gates')
  const permissions = useScreenPermissions(schema.data)
  return (
    <UniversalNativeCockpitPage
      screenId="admin/externe-gates"
      testId="screen-admin/externe-gates"
      permissions={permissions}
    />
  )
}
