import { AlertTriangle } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'
import { useCustomerSalesEligibility } from '@/hooks/useCustomerSalesEligibility'

export type BelegModus = 'auftrag' | 'lieferschein' | 'rechnung'

export function CustomerSalesEligibilityBanner({
  crmCustomerId,
  modus,
}: {
  crmCustomerId: string | undefined | null
  modus: BelegModus
}): JSX.Element | null {
  const { data, isLoading } = useCustomerSalesEligibility(crmCustomerId)

  if (!crmCustomerId || isLoading || !data) return null

  const blocked =
    modus === 'auftrag'
      ? !data.allowed_order
      : modus === 'lieferschein'
        ? !data.allowed_delivery
        : !data.allowed_invoice

  if (!blocked || data.reasons.length === 0) return null

  return (
    <Alert variant="destructive" className="mb-4 border-red-800">
      <AlertTriangle className="h-4 w-4" />
      <AlertTitle>Stammdaten — Freigabe fehlt</AlertTitle>
      <AlertDescription>
        <ul className="list-disc pl-5 space-y-1">
          {data.reasons.map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
        <p className="mt-2 text-sm">Speichern wird serverseitig abgelehnt, bis der Kunde im Stammdatensatz freigegeben ist.</p>
      </AlertDescription>
    </Alert>
  )
}
