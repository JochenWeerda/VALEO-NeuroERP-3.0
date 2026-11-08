import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

export default function MobileFeedingPage(): JSX.Element {
  const schema = useScreenDefinition('futtermittel/fuetterungsdokumentation-mobil')
  const permissions = useScreenPermissions(schema.data)
  return <UniversalNativeCockpitPage screenId="futtermittel/fuetterungsdokumentation-mobil" testId="feed-mobile-documentation" permissions={permissions} />
}
