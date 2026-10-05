import { Suspense, lazy, useEffect, useState } from 'react'
import { UniversalNativeCockpitPage } from '@/components/mask-builder/UniversalNativeCockpitPage'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { fetchFeedingGroups, type FeedingGroup } from '@/lib/api/rations-lifecycle'
import { recordDailyFeedingObservation } from '@/lib/api/feed-controlling'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { FeedingActualPage } from '@/features/feed-advice/FeedingActualPage'

const FeedControllingTrends = lazy(() =>
  import('@/features/feed-advice/FeedControllingTrends').then((module) => ({ default: module.FeedControllingTrends })),
)

const today = new Date().toISOString().slice(0, 10)

export function FeedControllingPage(): JSX.Element {
  const [open, setOpen] = useState(false)
  const [groups, setGroups] = useState<FeedingGroup[]>([])
  const [groupId, setGroupId] = useState('')
  const [date, setDate] = useState(today)
  const [values, setValues] = useState({ dmi: '', cost: '', milk: '', milkPrice: '', fat: '', protein: '', feedN: '', methane: '' })
  const [saving, setSaving] = useState(false)
  const [feedback, setFeedback] = useState<string | null>(null)
  const [refreshKey, setRefreshKey] = useState(0)

  useEffect(() => {
    if (!open) return
    void fetchFeedingGroups().then((items) => {
      setGroups(items)
      setGroupId((current) => current || items[0]?.id || '')
    }).catch((error) => setFeedback(getAxiosErrorMessage(error)))
  }, [open])

  function optionalNumber(value: string): number | undefined {
    return value.trim() === '' ? undefined : Number(value)
  }

  async function save(): Promise<void> {
    if (!groupId || !date) return
    setSaving(true)
    setFeedback(null)
    try {
      await recordDailyFeedingObservation({
        group_id: groupId, observation_date: date, source: 'manual', source_ref: 'daily-entry',
        actual_dmi_kg_cow: optionalNumber(values.dmi), actual_cost_eur_cow: optionalNumber(values.cost),
        milk_price_eur_kg: optionalNumber(values.milkPrice),
        actual_milk_kg_cow: optionalNumber(values.milk), actual_fat_pct: optionalNumber(values.fat),
        actual_protein_pct: optionalNumber(values.protein), feed_n_kg_cow: optionalNumber(values.feedN),
        actual_methane_kg_cow: optionalNumber(values.methane), methane_estimated: false,
      })
      setOpen(false)
      setRefreshKey((key) => key + 1)
      setFeedback('Tageswerte wurden idempotent gespeichert und Soll-Ist-Kennzahlen aktualisiert.')
    } catch (error) {
      setFeedback(getAxiosErrorMessage(error))
    } finally {
      setSaving(false)
    }
  }

  return (
    <div data-testid="feed-controlling-page">
      {feedback ? <p className="mb-3 rounded-md border bg-muted px-3 py-2 text-sm" role="status">{feedback}</p> : null}
      <Tabs defaultValue="tagesliste">
        <TabsList className="mb-3">
          <TabsTrigger value="tagesliste">Tagesliste</TabsTrigger>
          <TabsTrigger value="trends">Langfristtrends</TabsTrigger>
          <TabsTrigger value="components">Komponenten</TabsTrigger>
        </TabsList>
        <TabsContent value="tagesliste">
          <UniversalNativeCockpitPage key={refreshKey} screenId="agrar/feed-controlling" testId="feed-controlling-worklist"
            permissions={['futtermittel.rations.update']} onAction={(key) => { if (key === 'record_observation') setOpen(true) }} />
        </TabsContent>
        <TabsContent value="trends">
          <Suspense fallback={<div className="h-64 animate-pulse rounded-lg bg-muted/40" aria-hidden />}>
            <FeedControllingTrends />
          </Suspense>
        </TabsContent>
        <TabsContent value="components"><FeedingActualPage /></TabsContent>
      </Tabs>
      <Dialog open={open} onOpenChange={setOpen}>
        <DialogContent className="max-w-2xl">
          <DialogHeader><DialogTitle>Tageswerte erfassen</DialogTitle><DialogDescription>Istwerte pro Kuh; leere Felder bleiben fachlich unbekannt.</DialogDescription></DialogHeader>
          <div className="grid gap-3 sm:grid-cols-2">
            <div className="grid gap-2"><Label htmlFor="ctrl-group">Tiergruppe</Label><select id="ctrl-group" className="h-10 rounded-md border bg-background px-3" value={groupId} onChange={(e) => setGroupId(e.target.value)}>{groups.map((group) => <option key={group.id} value={group.id}>{group.name}</option>)}</select></div>
            <div className="grid gap-2"><Label htmlFor="ctrl-date">Tag</Label><Input id="ctrl-date" type="date" value={date} onChange={(e) => setDate(e.target.value)} /></div>
            {[
              ['dmi', 'TM-Aufnahme kg'], ['cost', 'Futterkosten EUR'], ['milk', 'Milch kg'], ['milkPrice', 'Milchpreis EUR/kg'],
              ['fat', 'Fett %'], ['protein', 'Eiweiss %'], ['feedN', 'Futter-N kg'], ['methane', 'Methan kg'],
            ].map(([key, label]) => <div className="grid gap-2" key={key}><Label htmlFor={`ctrl-${key}`}>{label}</Label><Input id={`ctrl-${key}`} type="number" min="0" step="0.001" value={values[key as keyof typeof values]} onChange={(e) => setValues((state) => ({ ...state, [key]: e.target.value }))} /></div>)}
          </div>
          <DialogFooter><Button variant="outline" onClick={() => setOpen(false)}>Abbrechen</Button><Button disabled={saving || !groupId} onClick={() => { void save() }}>{saving ? 'Speichert…' : 'Tageswerte speichern'}</Button></DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}
