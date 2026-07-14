import { useState } from 'react'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { createFeedingGroup } from '@/lib/api/rations-lifecycle'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useNavigate } from '@/app/routing/typed-router'

export function RationLifecycleWorklist(): JSX.Element {
  const navigate = useNavigate()
  const [groupOpen, setGroupOpen] = useState(false)
  const [name, setName] = useState('')
  const [animalCount, setAnimalCount] = useState('')
  const [location, setLocation] = useState('')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)

  async function saveGroup(): Promise<void> {
    if (!name.trim() || Number(animalCount) < 0 || animalCount.trim() === '') return
    setSaving(true)
    setFeedback(null)
    try {
      await createFeedingGroup({
        name: name.trim(),
        animal_count: Number(animalCount),
        feeding_system: 'TMR',
        location: location.trim() || null,
      })
      setGroupOpen(false)
      setName('')
      setAnimalCount('')
      setLocation('')
      setFeedback('Tiergruppe wurde angelegt und steht im Planungswerkzeug bereit.')
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div data-testid="ration-lifecycle-worklist">
      {feedback ? (
        <p className="mb-3 rounded-md border bg-muted px-3 py-2 text-sm" role="status">{feedback}</p>
      ) : null}
      <UniversalNativeCockpitPage
        screenId="agrar/rations-lifecycle"
        testId="native-ration-lifecycle"
        permissions={['futtermittel.rations.update']}
        onAction={(actionKey) => {
          if (actionKey === 'plan_ration') navigate('/portal/rationsoptimierung?mode=expert')
          if (actionKey === 'create_group') setGroupOpen(true)
        }}
      />

      <Dialog open={groupOpen} onOpenChange={setGroupOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Tiergruppe anlegen</DialogTitle>
            <DialogDescription>Stammdaten fuer Bedarf, Versionen und Fuetterungsbeginn.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="grid gap-2">
              <Label htmlFor="feeding-group-name">Bezeichnung</Label>
              <Input id="feeding-group-name" value={name} onChange={(event) => setName(event.target.value)} autoFocus />
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              <div className="grid gap-2">
                <Label htmlFor="feeding-group-count">Tierzahl</Label>
                <Input id="feeding-group-count" type="number" min="0" value={animalCount} onChange={(event) => setAnimalCount(event.target.value)} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="feeding-group-location">Stall / Ort</Label>
                <Input id="feeding-group-location" value={location} onChange={(event) => setLocation(event.target.value)} />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setGroupOpen(false)}>Abbrechen</Button>
            <Button disabled={saving || !name.trim() || !animalCount.trim()} onClick={() => { void saveGroup() }}>
              {saving ? 'Speichert…' : 'Tiergruppe anlegen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
