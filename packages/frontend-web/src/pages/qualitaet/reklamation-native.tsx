import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder'

export default function ReklamationNativePage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="qualitaet/reklamation" entityId={id} testId="qualitaet-reklamation" />
}
