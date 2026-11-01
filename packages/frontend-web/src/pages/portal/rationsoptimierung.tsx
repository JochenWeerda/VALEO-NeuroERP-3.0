import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

export default function PortalFeedAdvicePage(): JSX.Element {
  const schema = useScreenDefinition('portal/rationsoptimierung')
  const permissions = useScreenPermissions(schema.data)
  return <UniversalNativeCockpitPage screenId="portal/rationsoptimierung" testId="portal-feed-advice" permissions={permissions} />
}
