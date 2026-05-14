import {
  AlertTriangle,
  ArrowRight,
  Check,
  CheckCircle2,
  ClipboardCheck,
  ExternalLink,
  FileText,
  History,
  ShieldAlert,
  X,
  type LucideIcon,
} from 'lucide-react'
import { Button } from '@/components/ui/button'

type Tone = 'neutral' | 'blue' | 'emerald' | 'amber' | 'red'

const toneClasses: Record<Tone, { border: string; bg: string; text: string; dot: string }> = {
  neutral: { border: 'border-gray-200', bg: 'bg-white', text: 'text-gray-700', dot: 'bg-gray-400' },
  blue: { border: 'border-blue-200', bg: 'bg-blue-50', text: 'text-blue-800', dot: 'bg-blue-600' },
  emerald: { border: 'border-emerald-200', bg: 'bg-emerald-50', text: 'text-emerald-800', dot: 'bg-emerald-600' },
  amber: { border: 'border-amber-200', bg: 'bg-amber-50', text: 'text-amber-800', dot: 'bg-amber-500' },
  red: { border: 'border-red-200', bg: 'bg-red-50', text: 'text-red-800', dot: 'bg-red-600' },
}

export type UxRoleOption<T extends string = string> = {
  id: T
  label: string
  description: string
}

type RoleFocusBarProps<T extends string = string> = {
  roles: Array<UxRoleOption<T>>
  value: T
  onChange: (value: T) => void
  visibleCount?: number
  totalCount?: number
  title?: string
}

export function RoleFocusBar<T extends string = string>({
  roles,
  value,
  onChange,
  visibleCount,
  totalCount,
  title = 'Rollenfokus',
}: RoleFocusBarProps<T>): JSX.Element {
  const selected = roles.find((role) => role.id === value) ?? roles[0]
  return (
    <section className="rounded border border-gray-200 bg-white p-4 shadow-sm">
      <div className="mb-3 flex flex-col gap-1 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-base font-bold text-gray-900">
            <ClipboardCheck className="h-4 w-4 text-[#005ca5]" />
            {title}
          </h2>
          <p className="text-[12px] text-gray-500">{selected?.description}</p>
        </div>
        {typeof visibleCount === 'number' && typeof totalCount === 'number' ? (
          <span className="text-[11px] font-bold uppercase tracking-wide text-gray-400">
            {visibleCount} von {totalCount} sichtbar
          </span>
        ) : null}
      </div>
      <div className="flex flex-wrap gap-2">
        {roles.map((role) => (
          <button
            key={role.id}
            type="button"
            onClick={() => onChange(role.id)}
            className={`rounded border px-3 py-1.5 text-xs font-bold transition ${
              value === role.id ? 'border-[#005ca5] bg-blue-50 text-[#005ca5]' : 'border-gray-200 bg-white text-gray-600 hover:bg-gray-50'
            }`}
            title={role.description}
          >
            {role.label}
          </button>
        ))}
      </div>
    </section>
  )
}

export type UxTaskItem = {
  label: string
  done: boolean
  hint: string
}

export function OperationalTaskPlan({ title = 'Arbeitsplan', items }: { title?: string; items: UxTaskItem[] }): JSX.Element {
  return (
    <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
      <h4 className="mb-4 flex items-center gap-2 border-b pb-2 text-xs font-bold uppercase text-gray-700">
        <ClipboardCheck className="h-3.5 w-3.5 text-[#005ca5]" />
        {title}
      </h4>
      <div className="space-y-3">
        {items.map((item, index) => (
          <div key={item.label} className="flex items-start gap-3">
            <div className={`mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-[11px] font-black ${item.done ? 'border-emerald-500 bg-emerald-50 text-emerald-700' : 'border-gray-300 bg-gray-50 text-gray-500'}`}>
              {item.done ? <Check className="h-3.5 w-3.5" /> : index + 1}
            </div>
            <div className="min-w-0">
              <p className="text-[13px] font-bold text-gray-800">{item.label}</p>
              <p className="text-[12px] leading-relaxed text-gray-500">{item.hint}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export function NextActionPanel({ title = 'Empfohlene naechste Aktion', action, tone = 'blue' }: { title?: string; action: string; tone?: Tone }): JSX.Element {
  const classes = toneClasses[tone]
  return (
    <div className={`flex items-start gap-3 rounded-lg border p-4 ${classes.border} ${classes.bg}`}>
      <ArrowRight className={`mt-0.5 h-4.5 w-4.5 shrink-0 ${classes.text}`} />
      <div>
        <h5 className={`mb-0.5 text-[13px] font-bold ${classes.text}`}>{title}</h5>
        <p className={`text-[13px] ${classes.text}`}>{action}</p>
      </div>
    </div>
  )
}

export type EvidenceLink = {
  label: string
  href: string
}

export function EvidenceTemplateLink({ link }: { link: EvidenceLink }): JSX.Element {
  return (
    <a
      href={link.href}
      target="_blank"
      rel="noreferrer"
      className="flex items-center justify-between rounded border border-blue-200 bg-blue-50 px-3 py-2 text-xs font-bold text-blue-800 hover:bg-blue-100"
    >
      <span className="flex items-center gap-2">
        <FileText className="h-4 w-4" />
        Vorlage oeffnen: {link.label}
      </span>
      <ExternalLink className="h-3.5 w-3.5" />
    </a>
  )
}

export type AuditTimelineEntry = {
  label: string
  detail: string
  tone?: Tone
}

export function AuditTimeline({ title = 'Audit-Zeitleiste', entries }: { title?: string; entries: AuditTimelineEntry[] }): JSX.Element {
  return (
    <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
      <h4 className="mb-4 flex items-center gap-2 border-b pb-2 text-xs font-bold uppercase text-gray-700">
        <History className="h-3.5 w-3.5 text-[#005ca5]" />
        {title}
      </h4>
      {entries.length > 0 ? (
        <div className="space-y-3">
          {entries.map((entry) => {
            const tone = entry.tone ?? 'neutral'
            return (
              <div key={`${entry.label}-${entry.detail}`} className="flex gap-3">
                <span className={`mt-1.5 h-2.5 w-2.5 shrink-0 rounded-full ${toneClasses[tone].dot}`} />
                <div className="min-w-0">
                  <p className="text-[13px] font-bold text-gray-800">{entry.label}</p>
                  <p className="break-words text-[12px] text-gray-500">{entry.detail}</p>
                </div>
              </div>
            )
          })}
        </div>
      ) : (
        <p className="text-[13px] text-gray-500">Noch keine Nachweise, Tests oder Entscheidungen protokolliert.</p>
      )}
    </div>
  )
}

export type ManagementDecision = {
  allowed: boolean
  allowedLabel?: string
  blockedLabel?: string
  summary: string
  blockerCount?: number
  nextFocus?: string
  template?: EvidenceLink
}

export function ManagementDecisionPanel({ decision }: { decision: ManagementDecision }): JSX.Element {
  const tone = decision.allowed ? 'emerald' : 'red'
  const classes = toneClasses[tone]
  const Icon = decision.allowed ? Check : X
  return (
    <section className="overflow-hidden rounded border border-gray-300 border-t-4 border-t-[#005ca5] bg-white shadow-sm">
      <div className="flex items-center justify-between border-b border-gray-200 bg-gray-50/50 px-6 py-4">
        <div className="flex items-center gap-2.5">
          {decision.allowed ? <CheckCircle2 className="h-5 w-5 text-emerald-700" /> : <ShieldAlert className="h-5 w-5 text-red-700" />}
          <h2 className="text-base font-bold text-gray-900">Darf der Prozess abgeschlossen werden?</h2>
        </div>
        <span className="text-[10px] font-bold uppercase tracking-widest text-gray-400">Entscheidung</span>
      </div>
      <div className="flex flex-wrap items-start gap-8 p-6 lg:flex-nowrap lg:gap-12">
        <div className="flex-1 space-y-4">
          <p className="max-w-3xl text-sm leading-relaxed text-gray-600">{decision.summary}</p>
          {typeof decision.blockerCount === 'number' && decision.blockerCount > 0 ? (
            <div className="inline-flex items-center gap-2 rounded border border-red-200 bg-red-50 px-3 py-1.5 text-[11px] font-bold uppercase tracking-wide text-red-700">
              <AlertTriangle className="h-3.5 w-3.5" />
              {decision.blockerCount} aktive Stopper
            </div>
          ) : null}
        </div>
        <div className={`flex min-w-full flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed p-8 text-center sm:min-w-[320px] ${classes.border} ${classes.bg}`}>
          <div className={`flex h-12 w-12 items-center justify-center rounded-full ${classes.dot}`}>
            <Icon className="h-7 w-7 text-white" strokeWidth={3} />
          </div>
          <h4 className={`text-xl font-black uppercase tracking-tight ${classes.text}`}>
            {decision.allowed ? decision.allowedLabel ?? 'Freigabe erteilt' : decision.blockedLabel ?? 'Keine Freigabe'}
          </h4>
          <p className="text-xs font-medium text-gray-500">
            {decision.allowed ? 'Alle kritischen Anforderungen wurden erfuellt.' : `${decision.blockerCount ?? 0} kritische Punkte verhindern aktuell den Abschluss.`}
          </p>
        </div>
      </div>
      <div className="grid border-t border-gray-100 bg-gray-50/60 md:grid-cols-2">
        <div className="border-b border-gray-100 p-4 md:border-b-0 md:border-r">
          <p className="text-[10px] font-bold uppercase tracking-wide text-gray-400">Naechster Fokus</p>
          <p className="mt-1 text-sm font-bold text-gray-800">{decision.nextFocus ?? 'Regelpruefung terminieren'}</p>
        </div>
        <div className="p-4">
          <p className="text-[10px] font-bold uppercase tracking-wide text-gray-400">Vorlage Entscheidung</p>
          {decision.template ? (
            <a href={decision.template.href} target="_blank" rel="noreferrer" className="mt-1 inline-flex items-center gap-1 text-sm font-bold text-[#005ca5] hover:underline">
              {decision.template.label}
              <ExternalLink className="h-3.5 w-3.5" />
            </a>
          ) : (
            <p className="mt-1 text-sm text-gray-500">Keine Vorlage verknuepft.</p>
          )}
        </div>
      </div>
    </section>
  )
}

export type CrudCapability = {
  key: string
  label: string
  available: boolean
  hint: string
  icon?: LucideIcon
}

export function CrudCapabilityChecklist({ capabilities }: { capabilities: CrudCapability[] }): JSX.Element {
  return (
    <div className="rounded border border-gray-200 bg-white p-4 shadow-sm">
      <h4 className="mb-4 border-b pb-2 text-xs font-bold uppercase text-gray-700">CRUD-Abdeckung</h4>
      <div className="grid gap-2 sm:grid-cols-2">
        {capabilities.map((capability) => {
          const Icon = capability.icon
          return (
            <div key={capability.key} className={`rounded border px-3 py-2 ${capability.available ? 'border-emerald-200 bg-emerald-50' : 'border-amber-200 bg-amber-50'}`}>
              <div className="flex items-center gap-2">
                {Icon ? <Icon className={`h-3.5 w-3.5 ${capability.available ? 'text-emerald-700' : 'text-amber-700'}`} /> : null}
                <span className={`text-[12px] font-bold ${capability.available ? 'text-emerald-800' : 'text-amber-800'}`}>{capability.label}</span>
              </div>
              <p className="mt-1 text-[11px] text-gray-600">{capability.hint}</p>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export function EmptyStateWithAction({
  title,
  description,
  actionLabel,
  onAction,
}: {
  title: string
  description: string
  actionLabel?: string
  onAction?: () => void
}): JSX.Element {
  return (
    <div className="rounded border border-dashed border-gray-300 bg-white p-8 text-center">
      <p className="text-base font-bold text-gray-900">{title}</p>
      <p className="mx-auto mt-2 max-w-md text-sm text-gray-500">{description}</p>
      {actionLabel && onAction ? (
        <Button type="button" className="mt-4" onClick={onAction}>
          {actionLabel}
        </Button>
      ) : null}
    </div>
  )
}

