import type { DecisionView } from '@/policy/decision-view'

interface ProcessStatusPanelProps {
  view: DecisionView
  title?: string
}

export function ProcessStatusPanel({ view, title }: ProcessStatusPanelProps): JSX.Element {
  return (
    <div className={`rounded-md border px-3 py-2 ${view.statusClassName}`}>
      {title ? <div className="mb-1 text-xs uppercase opacity-70">{title}</div> : null}
      <div className="text-sm font-semibold">{view.statusLabel}</div>
      <p className="mt-1 text-sm">{view.summary}</p>
      {view.details.length > 0 ? (
        <ul className="mt-2 list-disc pl-4 text-xs">
          {view.details.map((detail) => (
            <li key={detail}>{detail}</li>
          ))}
        </ul>
      ) : null}
    </div>
  )
}
