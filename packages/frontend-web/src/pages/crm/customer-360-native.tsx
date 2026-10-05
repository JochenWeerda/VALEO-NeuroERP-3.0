import { useParams, useSearchParams } from '@/app/routing/typed-router'
import PartyNativePage, { readQueryParam, resolvePartyKind, resolvePartySectionKey } from '@/pages/crm/party-native'

export default function Customer360NativePage(): JSX.Element {
  const { id: routeId } = useParams<{ id?: string }>()
  const [searchParams] = useSearchParams()
  const id = routeId ?? readQueryParam(searchParams, 'id') ?? undefined
  return (
    <PartyNativePage
      kind={resolvePartyKind(readQueryParam(searchParams, 'kind'))}
      entityId={id}
      requestedSectionKey={resolvePartySectionKey(readQueryParam(searchParams, 'tab'))}
    />
  )
}
