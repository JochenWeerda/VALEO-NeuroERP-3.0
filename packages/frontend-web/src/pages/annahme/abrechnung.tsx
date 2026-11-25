import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

/** Native Cockpit + agrar_workbench: ScreenDefinition annahme/abrechnung */
export default function AnnahmeAbrechnungPage(): JSX.Element {
  const schema = useScreenDefinition('annahme/abrechnung')
  const permissions = useScreenPermissions(schema.data)
  return (
    <UniversalNativeCockpitPage
      screenId="annahme/abrechnung"
      testId="screen-annahme/abrechnung"
      permissions={permissions}
    />
  )
}
