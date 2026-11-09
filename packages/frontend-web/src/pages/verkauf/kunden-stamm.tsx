import { useEffect } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate, useParams, useSearchParams } from '@/app/routing/typed-router'
import { Loader2 } from 'lucide-react'
import { apiClient, getAxiosErrorMessage } from '@/lib/api-client'
import { readQueryParam } from '@/pages/crm/party-native'

/**
 * Alter Kundenstamm (`/verkauf/kunde/:id`, `/verkauf/kunden-stamm/:id`) -> Studio-Kundenakte `crm/customer-360`.
 *
 * Die Pflege von Anschriften, Ansprechpartnern, CPD-Konten, Rabatten, Preisen und Chef-Anweisungen laeuft seit
 * 09.11.2026 in der Kundenakte selbst (Kommandowege fuer Maske, CLI und MCP). Alte Links tragen die
 * Geschaeftspartner-ID; der Server loest sie auf die Kunden-ID auf.
 */
export default function KundenStammRedirect(): JSX.Element {
  const navigate = useNavigate()
  const { id } = useParams<{ id?: string }>()
  const [suche] = useSearchParams()
  const neu = !id || id === 'neu' || id === 'new'
  const kunde = useQuery({
    queryKey: ['kunden-stamm-redirect', id],
    enabled: !neu,
    queryFn: async () => (await apiClient.get<{ id: string }>(`/api/v1/crm/customers/${encodeURIComponent(id ?? '')}`)).data,
  })
  const tab = readQueryParam(suche, 'tab')
  const ziel = neu ? '/crm/kunden/neu' : kunde.data?.id
    ? `/crm/kunden/${encodeURIComponent(kunde.data.id)}${tab ? `?tab=${encodeURIComponent(tab)}` : ''}`
    : null

  useEffect(() => {
    if (ziel) navigate(ziel, { replace: true })
  }, [navigate, ziel])

  if (kunde.isError) {
    return <p role="alert" className="p-8 text-sm">Kunde nicht gefunden: {getAxiosErrorMessage(kunde.error)}</p>
  }
  return (
    <div className="flex h-full min-h-[40vh] flex-col items-center justify-center gap-3 p-8 text-center text-muted-foreground">
      <Loader2 className="h-6 w-6 animate-spin text-primary" />
      <h1 className="text-base font-semibold text-foreground">Weiter zur Kundenakte</h1>
    </div>
  )
}
