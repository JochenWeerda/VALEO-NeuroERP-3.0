import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

/** Native Cockpit + agrar_workbench: ScreenDefinition agrar/ernte-annahme-erfassung */
export default function ErnteAnnahmeErfassungPage(): JSX.Element {
  const schema = useScreenDefinition('agrar/ernte-annahme-erfassung')
  const permissions = useScreenPermissions(schema.data)
  return (
    <UniversalNativeCockpitPage
      screenId="agrar/ernte-annahme-erfassung"
      testId="screen-agrar/ernte-annahme-erfassung"
      permissions={permissions}
    />
  )
}
