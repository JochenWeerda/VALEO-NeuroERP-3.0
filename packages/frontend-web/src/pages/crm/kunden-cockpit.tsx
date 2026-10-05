import { useEffect } from 'react'
import { useNavigate, useSearchParams } from '@/app/routing/typed-router'
import { Loader2 } from 'lucide-react'
import { readQueryParam } from '@/pages/crm/party-native'

/**
 * Alte Links auf `/crm/kunden-cockpit` landen in der nativen Kundenakte
 * bzw. in der Kundenliste, wenn keine Id mitkommt.
 */
export default function KundenCockpitRedirect(): JSX.Element {
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()
  const customerId = readQueryParam(searchParams, 'id')
    ?? readQueryParam(searchParams, 'customer')
    ?? readQueryParam(searchParams, 'customerId')
    ?? readQueryParam(searchParams, 'customer_id')
    ?? readQueryParam(searchParams, 'kunden_nr')
  const tab = readQueryParam(searchParams, 'tab')
  const tabQuery = tab ? `?tab=${encodeURIComponent(tab)}` : ''
  const target = customerId
    ? `/crm/kunden/${encodeURIComponent(customerId)}${tabQuery}`
    : '/verkauf/kunden-liste'

  useEffect(() => {
    navigate(target, { replace: true })
  }, [navigate, target])

  return (
    <div className="flex h-full min-h-[40vh] flex-col items-center justify-center gap-3 p-8 text-center text-muted-foreground">
      <Loader2 className="h-6 w-6 animate-spin text-primary" />
      <h2 className="text-base font-semibold text-foreground">Kunden-Cockpit wurde abgelöst</h2>
      <p className="max-w-md text-sm">
        Das klassische Kunden-Cockpit wurde durch die native Kundenakte ersetzt. Du wirst
        automatisch weitergeleitet.
      </p>
      <a href={target} className="text-sm font-medium text-primary underline underline-offset-2">
        Weiter zur Kundenakte
      </a>
    </div>
  )
}
