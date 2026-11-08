import { useId } from 'react'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import type { ScreenDefinition } from '@/components/mask-builder/schema'
import { presentationEntries, renamePresentation } from './studio-presentation'

export function StudioVariantPresentation({ definition, disabled, onChange }: {
  definition: ScreenDefinition; disabled: boolean; onChange: (next: ScreenDefinition) => void
}): JSX.Element | null {
  const prefix = useId()
  if (!definition.documentVariant) return null
  return <details className="rounded border p-3">
    <summary className="cursor-pointer font-medium">Darstellung dieser Belegvariante bearbeiten</summary>
    <p className="my-2 text-sm text-muted-foreground">Beschriftungen ändern, ohne technische Feldnamen zu kennen. Änderungen gelten für diesen Entwurf. Datenbindung, Fachregeln und Rechte bleiben bestehen; Speichern und Freigabe erfolgen wie bisher.</p>
    <fieldset disabled={disabled} className="max-h-80 space-y-3 overflow-auto">
      <legend className="sr-only">Beschriftungen der Belegvariante</legend>
      {presentationEntries(definition).map(entry => <div key={entry.id}>
        <Label htmlFor={`${prefix}-${entry.id}`}>{entry.group} · {entry.label}</Label>
        <Input id={`${prefix}-${entry.id}`} defaultValue={entry.label} key={`${definition.id}:${entry.label}`}
          maxLength={160} onBlur={event => {
            const next = renamePresentation(definition, entry.id, event.target.value)
            if (next !== definition) onChange(next)
            else event.target.value = entry.label
          }} />
      </div>)}
    </fieldset>
  </details>
}
