import { Link } from '@/app/routing/typed-router'
import { AlertCircle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { Badge } from '@/components/ui/badge'
import { useCustomerChefHints } from '@/hooks/useCustomerChefHints'
import type { Instruction } from '@/lib/services/business-partner-service'

function priorityLabel(p: Instruction['instruction_priority']): string {
  switch (p) {
    case 'critical':
      return 'Kritisch'
    case 'high':
      return 'Hoch'
    case 'low':
      return 'Niedrig'
    default:
      return 'Normal'
  }
}

function priorityBadgeClass(p: Instruction['instruction_priority']): string {
  switch (p) {
    case 'critical':
      return 'bg-red-700 text-white border-transparent'
    case 'high':
      return 'bg-amber-600 text-white border-transparent'
    case 'low':
      return 'bg-slate-500 text-white border-transparent'
    default:
      return 'bg-slate-600 text-white border-transparent'
  }
}

export type CustomerChefHintsBannerProps = {
  customerNumber: string | undefined | null
  crmCustomerId: string | undefined | null
  chefanweisungFromCustomer?: string | null
}

/**
 * Hinweise aus CRM-Chefanweisung und Kundenstamm (Chef-Anweisungen / Instructions).
 * Wird in Auftrags- und Lieferscheinerfassung verwendet — eine gemeinsame Datenlogik.
 */
export function CustomerChefHintsBanner({
  customerNumber,
  crmCustomerId,
  chefanweisungFromCustomer,
}: CustomerChefHintsBannerProps): JSX.Element | null {
  const { data, isLoading } = useCustomerChefHints({
    customerNumber,
    crmCustomerId,
    chefanweisungFromCustomer,
  })

  if (isLoading && !data) {
    return (
      <Alert className="mb-4 border-amber-200 bg-amber-50/90">
        <AlertCircle className="h-4 w-4 text-amber-800" />
        <AlertTitle className="text-amber-950">Chef-Hinweise</AlertTitle>
        <AlertDescription className="text-amber-900 text-sm">Lade Hinweise…</AlertDescription>
      </Alert>
    )
  }

  if (!data) return null

  const hasCrm = Boolean(data.crmChefanweisung)
  const hasInstr = data.instructions.length > 0
  if (!hasCrm && !hasInstr) return null

  return (
    <Alert className="mb-4 border-amber-300 bg-amber-50/95">
      <AlertCircle className="h-4 w-4 text-amber-900" />
      <AlertTitle className="text-amber-950 flex flex-wrap items-center gap-2">
        Chef-Hinweise
        {data.partnerId ? (
          <Link
            to={`/verkauf/kunden-stamm/${data.partnerId}`}
            className="text-xs font-normal text-amber-900 underline-offset-2 hover:underline"
            target="_blank"
            rel="noopener noreferrer"
          >
            Kundenstamm öffnen
          </Link>
        ) : null}
      </AlertTitle>
      <AlertDescription className="space-y-3 text-amber-950">
        {hasCrm ? (
          <div>
            <div className="text-xs font-semibold uppercase tracking-wide text-amber-900/90 mb-1">
              CRM-Chefanweisung
            </div>
            <p className="whitespace-pre-wrap text-sm">{data.crmChefanweisung}</p>
          </div>
        ) : null}
        {hasInstr ? (
          <div>
            <div className="text-xs font-semibold uppercase tracking-wide text-amber-900/90 mb-1">
              Chef-Anweisungen (Stammdaten)
            </div>
            <ul className="list-none space-y-2 pl-0">
              {data.instructions.map((row) => (
                <li key={row.id} className="rounded-md border border-amber-200/80 bg-white/60 px-3 py-2 text-sm">
                  <div className="flex flex-wrap items-center gap-2 mb-1">
                    <Badge className={priorityBadgeClass(row.instruction_priority)} variant="secondary">
                      {priorityLabel(row.instruction_priority)}
                    </Badge>
                  </div>
                  <p className="whitespace-pre-wrap">{row.instruction_text}</p>
                </li>
              ))}
            </ul>
          </div>
        ) : null}
      </AlertDescription>
    </Alert>
  )
}
