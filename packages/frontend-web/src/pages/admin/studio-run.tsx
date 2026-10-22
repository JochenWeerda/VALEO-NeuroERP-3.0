import { NativeListPage } from '@/components/mask-builder/NativeListPage'
import { useParams } from '@/app/routing/typed-router'

export default function StudioRunPage(): JSX.Element {
  const { screenId: rawScreenId } = useParams<{ screenId?: string }>()
  const screenId = (rawScreenId ?? '').replace(/__/g, '/')
  if (!screenId) {
    return <p className="p-4 text-sm text-muted-foreground">Keine Studio-Maske angegeben.</p>
  }
  return (
    <div className="p-4" data-testid="studio-run" data-screen-id={screenId}>
      <NativeListPage screenId={screenId} testId="studio-released-mask" />
    </div>
  )
}
