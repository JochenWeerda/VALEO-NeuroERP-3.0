import { useQuery } from '@tanstack/react-query'
import { useLocation } from '@/app/routing/typed-router'
import { Badge } from '@/components/ui/badge'
import { RationEditor } from '@/features/feed-advice/RationEditor'
import { listRations } from '@/lib/api/rations-lifecycle'
import { getAxiosErrorMessage } from '@/lib/api-client'

const STATUS_LABEL: Record<string, string> = {
  draft: 'Entwurf',
  in_review: 'In Prüfung',
  approved: 'Freigegeben',
  scheduled: 'Geplant',
  active: 'Aktiv',
  retired: 'Abgelöst',
  archived: 'Archiviert',
}

/** Rationsliste als Einstieg: eine Ration öffnen lädt den Editor (?ration_id=…). */
function RationWorklist(): JSX.Element {
  const rations = useQuery({ queryKey: ['rations-worklist'], queryFn: () => listRations() })

  if (rations.isLoading) {
    return <div className="h-48 animate-pulse rounded-lg bg-muted/40" aria-hidden data-testid="ration-worklist-loading" />
  }
  if (rations.isError) {
    return (
      <div className="rounded-lg border bg-muted/30 p-4 text-sm" role="alert">
        <p className="font-medium text-status-error">Die Rationsliste konnte nicht geladen werden.</p>
        <p className="mt-1 text-muted-foreground">{getAxiosErrorMessage(rations.error)}</p>
      </div>
    )
  }
  const rows = rations.data ?? []
  return (
    <section className="space-y-4">
      <header>
        <h1 className="text-lg font-semibold">Rationseditor</h1>
        <p className="text-sm text-muted-foreground">
          Eine Ration öffnen, um Komponenten zu bearbeiten und gegen das Bedarfsprofil zu bewerten.
          Neue Rationen entstehen über die Rationsoptimierung.
        </p>
      </header>
      {rows.length === 0 ? (
        <div className="rounded-lg border bg-muted/30 p-4 text-sm text-muted-foreground" role="status">
          Noch keine Rationen vorhanden — zuerst in der{' '}
          <a className="underline" href="/futtermittel/rationsoptimierung">Rationsoptimierung</a>{' '}
          eine Ration erstellen und einreichen.
        </div>
      ) : (
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b text-left text-muted-foreground">
              <th className="py-1.5 pr-2 font-medium">Ration</th>
              <th className="py-1.5 pr-2 font-medium">Gruppe</th>
              <th className="py-1.5 pr-2 font-medium text-right">Version</th>
              <th className="py-1.5 pr-2 font-medium">Status</th>
              <th className="py-1.5 pr-2 font-medium">Geändert</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((ration) => (
              <tr key={ration.id} className="border-b last:border-b-0 hover:bg-muted/40">
                <td className="py-2 pr-2">
                  <a className="font-medium underline-offset-2 hover:underline"
                     href={`/futtermittel/rationseditor?ration_id=${encodeURIComponent(ration.id)}`}>
                    {ration.name}
                  </a>
                </td>
                <td className="py-2 pr-2">{ration.group_name}</td>
                <td className="py-2 pr-2 text-right tabular-nums">v{ration.version_no}</td>
                <td className="py-2 pr-2">
                  <Badge variant={ration.status === 'active' ? 'default' : 'secondary'}>
                    {STATUS_LABEL[ration.status] ?? ration.status}
                  </Badge>
                </td>
                <td className="py-2 pr-2 text-muted-foreground">
                  {new Date(ration.updated_at).toLocaleString('de-DE')}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </section>
  )
}

/** Rationseditor-Route (FEED-EDITOR-021/FEED-NAV-050): mit ?ration_id=… oeffnet
 * der Editor die Ration; ohne Parameter dient die Rationsliste als Einstieg. */
export default function RationsEditorPage(): JSX.Element {
  const location = useLocation()
  const rationId = new URLSearchParams(location.search).get('ration_id')

  return (
    <div className="p-6">
      {rationId ? <RationEditor rationId={rationId} /> : <RationWorklist />}
    </div>
  )
}
