import type { ReactNode } from 'react'
import type { DecisionView } from '@/policy/decision-view'

interface ProcessStatusPanelProps {
  view: DecisionView
  title?: string
  className?: string
  children?: ReactNode
}

export function ProcessStatusPanel({ view, title, className, children }: ProcessStatusPanelProps): JSX.Element {
  return (
    <div className={`rounded-md border px-3 py-2 ${view.statusClassName}${className ? ` ${className}` : ''}`}>
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
      {children}
    </div>
  )
}
