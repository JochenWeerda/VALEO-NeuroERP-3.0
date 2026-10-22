import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

const SCREEN_ID = 'auswertungen/sanktionspruefung-kunden'

export default function SanktionspruefungKundenPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string): Promise<void> {
    if (actionKey !== 'check') return
    const name = window.prompt('Kunde: Name fuer die Terrorschutzpruefung')?.trim()
    if (!name) return
    const entityRef = window.prompt('Kunden-Nummer (optional)')?.trim() || null
    try {
      const result = await apiClient.post<{ status: string; empfehlung: string }>(
        '/api/v1/compliance/sanctions/pruefen',
        { name, entity_ref: entityRef, scope: 'customers' },
      )
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: `Pruefergebnis: ${result.data.status}`, description: result.data.empfehlung })
    } catch (error) {
      toast({
        title: 'Terrorschutzpruefung fehlgeschlagen',
        description: error instanceof Error ? error.message : 'Unbekannter Fehler',
        variant: 'destructive',
      })
    }
  }

  return (
    <UniversalNativeCockpitPage
      screenId={SCREEN_ID}
      testId="customers-sanctions-check"
      permissions={['compliance.sanctions.check']}
      onAction={handleAction}
    />
  )
}
