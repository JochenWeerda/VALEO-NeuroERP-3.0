import { useParams, useSearchParams } from '@/app/routing/typed-router'
import { UniversalNativeCreatePage } from '@/components/mask-builder/UniversalNativeCreatePage'
import { isStammCreationEntityId } from '@/components/mask-builder'
import PartyNativePage from '@/pages/crm/party-native'

/** Lead Detail native; Anlage ueber ScreenDefinition ``crm/lead``.creation (Studio-made). */
export default function LeadDetailPage(): JSX.Element {
  const { id: routeId } = useParams<{ id?: string }>()
  const [searchParams] = useSearchParams()
  const entityId = routeId ?? searchParams.get('id') ?? undefined

  if (isStammCreationEntityId(entityId)) {
    return <UniversalNativeCreatePage screenId="crm/lead" testId="crm-lead-create" />
  }

  return <PartyNativePage kind="lead" entityId={entityId} />
}
