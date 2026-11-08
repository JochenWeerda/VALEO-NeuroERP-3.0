import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { getAxiosErrorMessage } from '@/lib/api-client'
import { saveStudioMigrationPlan, type StudioSavedMigrationPlan } from '@/lib/api/studio'

interface Props {
  draftId?: string
  revision?: string
  disabled: boolean
  onPrepared: (plan: StudioSavedMigrationPlan) => void
}

export function StudioMigrationPlan({ draftId, revision, disabled, onPrepared }: Props) {
  const [busy, setBusy] = useState(false)
  const [plan, setPlan] = useState<StudioSavedMigrationPlan>()
  const [error, setError] = useState<string>()
  const current = plan && plan.draft_id === draftId && plan.candidate_revision === revision ? plan : undefined
  async function prepare() {
    if (!draftId || !revision || busy || disabled) return
    setBusy(true)
    setError(undefined)
    try {
      const saved = await saveStudioMigrationPlan(draftId, revision)
      setPlan(saved)
      onPrepared(saved)
    } catch (failure) { setError(getAxiosErrorMessage(failure)) }
    finally { setBusy(false) }
  }
  return <section aria-label="Änderungsplan" className="space-y-2 rounded border border-border bg-card p-3 text-card-foreground">
    <p className="text-sm">Änderungsplan für die gespeicherte Fassung prüfen und festhalten.</p>
    <Button type="button" variant="outline" disabled={disabled || busy || !draftId || !revision} onClick={() => void prepare()}>
      {busy ? 'Änderungsplan wird geprüft…' : 'Änderungsplan festhalten'}
    </Button>
    {current && <p role="status" className="text-sm">
      {current.requires_definition_update ? 'Die vorgeschlagenen Bindungen müssen zuerst in einer neuen Fassung gespeichert werden.'
        : current.schema_changes.length ? 'Die vorgeschlagenen Datenbankänderungen benötigen noch einen geprüften Bereitstellungsnachweis.'
          : 'Änderungsplan für diese Fassung festgehalten. Freigabe und Simulation werden zusätzlich geprüft.'}
    </p>}
    {error && <p role="alert" className="text-sm text-destructive">{error}</p>}
  </section>
}
