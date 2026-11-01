import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder/UniversalNativeDetailPage'

export default function AktivitaetDetailPage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="crm/aktivitaet" entityId={id || 'neu'} testId="crm-aktivitaet-detail" />
}
