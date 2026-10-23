import { useParams, useSearchParams } from '@/app/routing/typed-router'
import PartyNativePage, { readQueryParam, resolvePartySectionKey } from '@/pages/crm/party-native'

export default function LeadNativePage(): JSX.Element {
  const { id } = useParams<{ id?: string }>()
  const [searchParams] = useSearchParams()
  return (
    <PartyNativePage
      kind="lead"
      entityId={id ?? readQueryParam(searchParams, 'id') ?? undefined}
      requestedSectionKey={resolvePartySectionKey(readQueryParam(searchParams, 'tab'))}
    />
  )
}
