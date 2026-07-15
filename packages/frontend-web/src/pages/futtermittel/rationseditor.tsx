import { useLocation } from '@/app/routing/typed-router'
import { RationEditor } from '@/features/feed-advice/RationEditor'

/** Rationseditor-Route (FEED-EDITOR-021): erwartet ?ration_id=… aus Worklist/Lifecycle. */
export default function RationsEditorPage(): JSX.Element {
  const location = useLocation()
  const rationId = new URLSearchParams(location.search).get('ration_id')

  if (!rationId) {
    return (
      <div className="p-6">
        <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground" role="status">
          Keine Ration gewählt. Bitte aus der Rationsliste eine Ration öffnen
          (Aufruf mit <code>?ration_id=…</code>).
        </div>
      </div>
    )
  }

  return (
    <div className="p-6">
      <RationEditor rationId={rationId} />
    </div>
  )
}
