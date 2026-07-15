import { useState } from 'react'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { createFeedingBusiness } from '@/lib/api/feeding-business'
import { getAxiosErrorMessage } from '@/lib/api-client'

export function FeedingBusinessWorklist(): JSX.Element {
  const [open, setOpen] = useState(false)
  const [name, setName] = useState('')
  const [productionType, setProductionType] = useState('')
  const [feedingSystem, setFeedingSystem] = useState('')
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  async function save(): Promise<void> {
    if (!name.trim()) return
    setSaving(true)
    setFeedback(null)
    try {
      await createFeedingBusiness({
        name: name.trim(),
        production_type: productionType.trim() || null,
        feeding_system: feedingSystem.trim() || null,
      })
      setName('')
      setProductionType('')
      setFeedingSystem('')
      setOpen(false)
      setRefreshKey((value) => value + 1)
      setFeedback('Fuetterungsbetrieb wurde angelegt.')
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div data-testid="feeding-business-list">
      {feedback ? <p className="mb-3 rounded-md border bg-muted px-3 py-2 text-sm" role="status">{feedback}</p> : null}
      <UniversalNativeCockpitPage
        key={refreshKey}
        screenId="agrar/feeding-businesses"
        testId="native-feeding-businesses"
        permissions={['futtermittel.rations.update']}
        onAction={(actionKey) => { if (actionKey === 'create_business') setOpen(true) }}
      />
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Fuetterungsbetrieb anlegen</DialogTitle>
            <DialogDescription>Betriebsscope fuer Standorte, Herden, Gruppen und Beratung.</DialogDescription>
          </DialogHeader>
          <div className="grid gap-4 py-2">
            <div className="grid gap-2">
              <Label htmlFor="feeding-business-name">Betriebsname</Label>
              <Input id="feeding-business-name" value={name} onChange={(event) => setName(event.target.value)} autoFocus />
            </div>
            <div className="grid gap-2 sm:grid-cols-2">
              <div className="grid gap-2">
                <Label htmlFor="feeding-business-production">Produktionsrichtung</Label>
                <Input id="feeding-business-production" value={productionType} onChange={(event) => setProductionType(event.target.value)} />
              </div>
              <div className="grid gap-2">
                <Label htmlFor="feeding-business-system">Fuetterungssystem</Label>
                <Input id="feeding-business-system" value={feedingSystem} onChange={(event) => setFeedingSystem(event.target.value)} />
              </div>
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setOpen(false)}>Abbrechen</Button>
            <Button disabled={saving || !name.trim()} onClick={() => { void save() }}>
              {saving ? 'Speichert...' : 'Betrieb anlegen'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
