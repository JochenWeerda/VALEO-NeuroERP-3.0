import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { useToast } from '@/hooks/use-toast'
import { apiClient } from '@/lib/api-client'

export function SanktionsScopePage({
  scope,
  subjectLabel,
}: {
  scope: 'personal' | 'customers'
  subjectLabel: string
}): JSX.Element {
  const screenId = `auswertungen/sanktionspruefung-${scope === 'customers' ? 'kunden' : 'personal'}`
  const queryClient = useQueryClient()
  const { toast } = useToast()

  async function handleAction(actionKey: string): Promise<void> {
    if (actionKey !== 'check') return
    const name = window.prompt(`${subjectLabel}: Name fuer die Terrorschutzpruefung`)?.trim()
    if (!name) return
    const entityRef = window.prompt(`${subjectLabel}-Nummer (optional)`)?.trim() || null
    try {
      const result = await apiClient.post<{ status: string; empfehlung: string }>(
        '/api/v1/compliance/sanctions/pruefen',
        { name, entity_ref: entityRef, scope },
      )
      await queryClient.invalidateQueries({ queryKey: [screenId] })
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
      screenId={screenId}
      testId={`${scope}-sanctions-check`}
      permissions={['compliance.sanctions.check']}
      onAction={handleAction}
    />
  )
}
