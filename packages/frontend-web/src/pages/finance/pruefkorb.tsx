import { useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { Button } from '@/components/ui/button'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { apiClient } from '@/lib/api-client'
import { useToast } from '@/hooks/use-toast'

const SCREEN_ID = 'finance/pruefkorb'
const MIN_BEWERTUNG = 3

type Befund = { id: string; art: string; hinweis: string }

function serverGrund(error: unknown): string {
  const detail = (error as { response?: { data?: { detail?: unknown } } })?.response?.data?.detail
  if (typeof detail === 'string' && detail) return detail
  return error instanceof Error ? error.message : 'Unbekannter Fehler'
}

/**
 * Prüfkorb des Controllers (FIN-CONTROL-002): Arbeitsliste aus der ScreenDefinition; bewertet wird
 * über den Kommandoweg des Servers, der Rolle und Funktionstrennung prüft.
 */
export default function PruefkorbPage(): JSX.Element {
  const queryClient = useQueryClient()
  const { toast } = useToast()
  const [befund, setBefund] = useState<Befund | null>(null)
  const [bewertung, setBewertung] = useState('')
  const [saving, setSaving] = useState(false)

  function handleAction(actionKey: string, row: Record<string, unknown>): void {
    if (actionKey === 'open_source') {
      const route = String(row.source_route ?? '')
      if (route.startsWith('/')) window.location.assign(route)
      else toast({ title: 'Zu diesem Vorgang gibt es keine Belegmaske' })
      return
    }
    if (actionKey === 'pruefen' && row.id) {
      setBewertung('')
      setBefund({ id: String(row.id), art: String(row.art ?? ''), hinweis: String(row.hinweis ?? '') })
    }
  }

  async function handleBewerten(): Promise<void> {
    if (!befund || saving || bewertung.trim().length < MIN_BEWERTUNG) return
    setSaving(true)
    try {
      await apiClient.post(`/api/v1/kontrolle/befunde/${encodeURIComponent(befund.id)}/pruefung`, {
        note: bewertung.trim(),
      })
      await queryClient.invalidateQueries({ queryKey: [SCREEN_ID] })
      toast({ title: 'Befund bewertet' })
      setBefund(null)
    } catch (error) {
      toast({ title: 'Bewertung nicht gespeichert', description: serverGrund(error), variant: 'destructive' })
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <UniversalNativeCockpitPage screenId={SCREEN_ID} testId="finanz-pruefkorb" onAction={handleAction} />
      <Dialog open={befund !== null} onOpenChange={(open) => { if (!open && !saving) setBefund(null) }}>
        <DialogContent data-testid="pruefkorb-bewertung">
          <DialogHeader>
            <DialogTitle>Befund bewerten</DialogTitle>
            <DialogDescription>
              {befund?.art}
              {befund?.hinweis ? ` — ${befund.hinweis}` : ''}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-2">
            <Label htmlFor="pruefkorb-bewertung-text">Bewertung</Label>
            <Textarea
              id="pruefkorb-bewertung-text"
              value={bewertung}
              onChange={(event) => setBewertung(event.target.value)}
              maxLength={500}
              rows={4}
              placeholder="Was wurde geprüft, und mit welchem Ergebnis?"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setBefund(null)} disabled={saving}>
              Abbrechen
            </Button>
            <Button
              onClick={() => { void handleBewerten() }}
              disabled={saving || bewertung.trim().length < MIN_BEWERTUNG}
              data-testid="pruefkorb-bewertung-speichern"
            >
              {saving ? 'Speichert…' : 'Als geprüft festhalten'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}
