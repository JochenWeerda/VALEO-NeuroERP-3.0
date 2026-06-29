import { useParams } from '@/app/routing/typed-router'
import { UniversalNativeDetailPage } from '@/components/mask-builder'

export default function AuftragsbestaetigungNativePage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  return <UniversalNativeDetailPage screenId="einkauf/auftragsbestaetigung" entityId={id} testId="einkauf-auftragsbestaetigung" />
}
