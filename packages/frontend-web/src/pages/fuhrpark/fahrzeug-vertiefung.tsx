import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

/** Native Cockpit + fleet_workbench: ScreenDefinition fuhrpark/fahrzeug-vertiefung */
export default function FahrzeugVertiefungPage(): JSX.Element {
  const schema = useScreenDefinition('fuhrpark/fahrzeug-vertiefung')
  const permissions = useScreenPermissions(schema.data)
  return (
    <UniversalNativeCockpitPage
      screenId="fuhrpark/fahrzeug-vertiefung"
      testId="screen-fuhrpark/fahrzeug-vertiefung"
      permissions={permissions}
    />
  )
}
