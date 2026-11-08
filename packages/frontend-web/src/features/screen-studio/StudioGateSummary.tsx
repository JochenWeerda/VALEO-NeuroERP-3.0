import type { StudioReport } from '@/lib/api/studio'

/** Authoring status is not a fresh authorization decision or live release proof. */
export function StudioGateSummary({ report, publishedUnchanged, readyToPublish, semanticPreview }: {
  report?: StudioReport
  publishedUnchanged: boolean
  readyToPublish: boolean
  semanticPreview: boolean
}): JSX.Element {
  const errors = (report?.readiness.errors ?? []).filter(error =>
    !(publishedUnchanged && error.startsWith('[non_temporary]')))
  return <>
    {!report ? <p role="status">Vertragsprüfung wird geladen oder ist derzeit nicht verfügbar.</p>
      : report.violations.length ? <ul className="list-disc pl-4 text-sm text-destructive">
        {report.violations.map(item => <li key={item}>{item}</li>)}
      </ul> : <p className="text-sm text-muted-foreground">Keine Studio-Verletzungen.</p>}
    <p className="text-sm">{publishedUnchanged
      ? 'Diese Fassung wurde bereits veröffentlicht. Der Laufzeitabruf prüft ihre Gültigkeit erneut; Änderungen benötigen eine neue Prüfung und Freigabe.'
      : readyToPublish ? 'Freigabe nach menschlicher Prüfung möglich.'
        : 'Freigabe gesperrt, bis Vertragsprüfung und Prozesssimulation bestanden sind.'}</p>
    {semanticPreview ? <p className="text-sm text-destructive">Diese Kalkulationsprobe besitzt noch keine freigegebene produktive Datenbindung und Prozessvariante.</p>
      : errors.map(item => <p key={item} className="text-sm text-destructive">{item}</p>)}
  </>
}
