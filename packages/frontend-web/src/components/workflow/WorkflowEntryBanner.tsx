import { Link2, Sparkles, Workflow } from 'lucide-react'
import { Alert, AlertDescription, AlertTitle } from '@/components/ui/alert'

export type WorkflowEntryContext = {
  process: string
  instanceId: string
  caseNumber: string
  label: string
  partnerName: string
  subject: string
  entryMode: string
}

export function readWorkflowEntryContext(searchParams: URLSearchParams): WorkflowEntryContext | null {
  const process = searchParams.get('workflowProcess') || ''
  const instanceId = searchParams.get('workflowInstanceId') || ''
  const caseNumber = searchParams.get('workflowCase') || ''
  const label = searchParams.get('workflowLabel') || ''
  const partnerName = searchParams.get('partnerName') || searchParams.get('customerName') || ''
  const subject = searchParams.get('subject') || ''
  const entryMode = searchParams.get('entryMode') || ''

  if (!process && !instanceId && !caseNumber) {
    return null
  }

  return {
    process,
    instanceId,
    caseNumber,
    label,
    partnerName,
    subject,
    entryMode,
  }
}

type WorkflowEntryBannerProps = {
  context: WorkflowEntryContext
  title?: string
  description?: string
}

export function WorkflowEntryBanner({
  context,
  title = 'Workflow-Handover aktiv',
  description = 'Du arbeitest aus einem Flow-Spine-Vorgang heraus. Die Fachdaten werden in dieser Standardmaske gepflegt, der Prozessfall bleibt dabei referenziert.',
}: WorkflowEntryBannerProps): JSX.Element {
  const parts = [
    context.caseNumber ? `Vorgang ${context.caseNumber}` : '',
    context.entryMode || '',
    context.partnerName || '',
    context.subject || '',
  ].filter(Boolean)

  return (
    <Alert className="border-indigo-400/30 bg-indigo-500/10 text-slate-100">
      <Workflow className="h-4 w-4 text-indigo-200" />
      <AlertTitle className="flex items-center gap-2 text-indigo-50">
        {title}
        <span className="inline-flex items-center gap-1 rounded-full border border-indigo-300/20 bg-indigo-400/10 px-2 py-0.5 text-[11px] font-medium text-indigo-100">
          <Sparkles className="h-3 w-3" />
          Flow Spine
        </span>
      </AlertTitle>
      <AlertDescription className="mt-2 space-y-2 text-slate-200">
        <div>{description}</div>
        {parts.length > 0 ? (
          <div className="flex flex-wrap items-center gap-2 text-xs text-indigo-100/90">
            {parts.map((part) => (
              <span key={part} className="rounded-full border border-white/10 bg-white/5 px-2.5 py-1">
                {part}
              </span>
            ))}
          </div>
        ) : null}
        {context.label ? (
          <div className="flex items-center gap-2 text-xs text-slate-300">
            <Link2 className="h-3.5 w-3.5 text-slate-400" />
            Interne Referenz: {context.label}
          </div>
        ) : null}
      </AlertDescription>
    </Alert>
  )
}
