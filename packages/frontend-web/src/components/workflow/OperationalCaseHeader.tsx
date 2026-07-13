import { AlertTriangle, ArrowRightCircle, ShieldCheck, UserCircle2 } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { Card, CardContent } from '@/components/ui/card'
import { operationalStatusLabel, operationalStatusVariant, type OperationalStatus } from '@/lib/operational-status'

type OperationalCaseHeaderProps = {
  title: string
  description?: string
  status: OperationalStatus
  owner?: string
  blocker?: string | null
  nextAction?: string
  caseLabel?: string
  tags?: string[]
}

export function OperationalCaseHeader({
  title,
  description,
  status,
  owner,
  blocker,
  nextAction,
  caseLabel,
  tags = [],
}: OperationalCaseHeaderProps): JSX.Element {
  return (
    <Card className="border-slate-200/80 bg-linear-to-r from-slate-50 to-white">
      <CardContent className="space-y-4 pt-6">
        <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div className="space-y-2">
            <div className="flex flex-wrap items-center gap-2">
              {caseLabel ? (
                <Badge variant="outline">{caseLabel}</Badge>
              ) : null}
              <Badge variant={operationalStatusVariant(status)}>{operationalStatusLabel(status)}</Badge>
              {tags.map((tag) => (
                <Badge key={tag} variant="secondary">
                  {tag}
                </Badge>
              ))}
            </div>
            <div>
              <h2 className="text-2xl font-semibold tracking-tight text-slate-950">{title}</h2>
              {description ? <p className="mt-1 text-sm text-slate-600">{description}</p> : null}
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            <div className="rounded-xl border bg-white px-4 py-3">
              <div className="mb-1 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                <UserCircle2 className="h-3.5 w-3.5" />
                Owner
              </div>
              <div className="text-sm font-medium text-slate-900">{owner || 'Noch nicht eindeutig zugewiesen'}</div>
            </div>
            <div className="rounded-xl border bg-white px-4 py-3">
              <div className="mb-1 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                <AlertTriangle className="h-3.5 w-3.5" />
                Blocker
              </div>
              <div className="text-sm font-medium text-slate-900">{blocker || 'Kein akuter Blocker'}</div>
            </div>
            <div className="rounded-xl border bg-white px-4 py-3">
              <div className="mb-1 flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-500">
                <ArrowRightCircle className="h-3.5 w-3.5" />
                Naechste Aktion
              </div>
              <div className="text-sm font-medium text-slate-900">{nextAction || 'Keine Folgeaktion hinterlegt'}</div>
            </div>
          </div>
        </div>
        {blocker ? (
          <div className="flex items-start gap-2 rounded-xl border border-amber-200 bg-amber-50 px-4 py-3 text-sm text-amber-900">
            <ShieldCheck className="mt-0.5 h-4 w-4 shrink-0" />
            <span>{blocker}</span>
          </div>
        ) : null}
      </CardContent>
    </Card>
  )
}
