import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder'

export default function MischfuttermittelNativePage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="futtermittel/mischfuttermittel" entityId={id} testId="futtermittel-mischfuttermittel" />
}
