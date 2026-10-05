import { useState } from 'react'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { createFeedingGroup } from '@/lib/api/rations-lifecycle'
import { fetchFeedingBusinesses, type FeedingBusiness } from '@/lib/api/feeding-business'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { useNavigate } from '@/app/routing/typed-router'

export function RationLifecycleWorklist(): JSX.Element {
  const navigate = useNavigate()
  const [groupOpen, setGroupOpen] = useState(false)
  const [name, setName] = useState('')
  const [animalCount, setAnimalCount] = useState('')
  const [location, setLocation] = useState('')
  const [businesses, setBusinesses] = useState<FeedingBusiness[]>([])
  const [businessId, setBusinessId] = useState('')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)

  async function saveGroup(): Promise<void> {
    if (!name.trim() || Number(animalCount) < 0 || animalCount.trim() === '') return
    setSaving(true)
    setFeedback(null)
    try {
      await createFeedingGroup({
        business_id: businessId,
        name: name.trim(),
        animal_count: Number(animalCount),
        feeding_system: 'TMR',
        location: location.trim() || null,
      })
      setGroupOpen(false)
      setName('')
      setAnimalCount('')
      setLocation('')
      setBusinessId('')
      setFeedback('Tiergruppe wurde angelegt und steht im Planungswerkzeug bereit.')
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  async function openGroupDialog(): Promise<void> {
    setFeedback(null)
    try {
      const rows = await fetchFeedingBusinesses()
      setBusinesses(rows)
      setBusinessId((current) => current || rows[0]?.id || '')
      setGroupOpen(true)
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
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
          if (actionKey === 'create_group') void openGroupDialog()
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
              <Label htmlFor="feeding-group-business">Fuetterungsbetrieb</Label>
              <select id="feeding-group-business" className="h-10 rounded-md border bg-background px-3 text-sm" value={businessId} onChange={(event) => setBusinessId(event.target.value)}>
                {businesses.map((business) => <option key={business.id} value={business.id}>{business.name}</option>)}
              </select>
              {businesses.length === 0 ? <p className="text-sm text-muted-foreground">Zuerst einen Fuetterungsbetrieb anlegen.</p> : null}
            </div>
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
            <Button disabled={saving || !businessId || !name.trim() || !animalCount.trim()} onClick={() => { void saveGroup() }}>
              {saving ? 'Speichert…' : 'Tiergruppe anlegen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
