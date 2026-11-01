import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

export default function RationsoptimierungPage(): JSX.Element {
  const schema = useScreenDefinition('futtermittel/rationsoptimierung')
  const permissions = useScreenPermissions(schema.data)
  return <UniversalNativeCockpitPage screenId="futtermittel/rationsoptimierung" testId="feed-ration-optimization" permissions={permissions} />
}
