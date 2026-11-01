import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useScreenDefinition } from '@/lib/api/masks'
import { useScreenPermissions } from '@/components/mask-builder/runtime/screen-permissions'

export default function RationsEditorPage(): JSX.Element {
  const schema = useScreenDefinition('futtermittel/rationseditor')
  const permissions = useScreenPermissions(schema.data)
  return <UniversalNativeCockpitPage screenId="futtermittel/rationseditor" testId="feed-ration-editor" permissions={permissions} />
}
