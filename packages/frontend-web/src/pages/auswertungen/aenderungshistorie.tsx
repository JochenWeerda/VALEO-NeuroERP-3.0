import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'auswertungen/aenderungshistorie'

export default function AenderungshistoriePage(): JSX.Element {
  const { toast } = useToast()

  async function handleAction(actionKey: string): Promise<void> {
    if (actionKey !== 'validate_chain') return
    const result = await apiClient.get<{ valid: boolean; checked: number }>('/api/v1/audit/trail/validate')
    toast({
      title: result.valid ? 'Audit-Kette gueltig' : 'Audit-Kette fehlerhaft',
      description: `${result.checked} Eintraege geprueft.`,
      variant: result.valid ? 'default' : 'destructive',
    })
  }

  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="aenderungshistorie"
      permissions={['audit.read']}
      onAction={handleAction}
    />
  )
}
