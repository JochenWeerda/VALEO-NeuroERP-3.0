import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { cn } from '@/lib/utils'
import { CheckCircle2, ExternalLink, ShieldCheck, Sparkles } from 'lucide-react'

export type AgentUxSource = {
  label: string
  href: string
  description: string
}

export type AgentUxAction = {
  label: string
  href: string
  description: string
}

export type AgentUxPanelProps = {
  title?: string
  summary: string
  confidence: number
  confidenceLabel?: string
  sources: AgentUxSource[]
  action: AgentUxAction
  className?: string
}

function clampConfidence(value: number): number {
  if (!Number.isFinite(value)) {
    return 0
  }
  return Math.min(100, Math.max(0, Math.round(value)))
}

export function AgentUxPanel({
  title = 'Agent UX Panel',
  summary,
  confidence,
  confidenceLabel = 'Confidence',
  sources,
  action,
  className,
}: AgentUxPanelProps): JSX.Element {
  const safeConfidence = clampConfidence(confidence)
  return (
    <Card className={cn('border-slate-200 bg-gradient-to-br from-slate-50 to-white', className)}>
      <CardHeader className="space-y-2">
        <CardTitle className="flex items-center gap-2 text-xl">
          <Sparkles className="h-5 w-5 text-slate-700" />
          {title}
        </CardTitle>
        <CardDescription>{summary}</CardDescription>
      </CardHeader>
      <CardContent className="space-y-5">
        <div className="grid gap-3 md:grid-cols-[1.2fr_0.8fr]">
          <div className="space-y-2 rounded-lg border bg-white p-4 shadow-sm">
            <div className="flex items-center justify-between gap-3">
              <div>
                <p className="text-xs uppercase tracking-wide text-muted-foreground">{confidenceLabel}</p>
                <p className="text-3xl font-bold">{safeConfidence}%</p>
              </div>
              <Badge variant={safeConfidence >= 80 ? 'default' : safeConfidence >= 60 ? 'secondary' : 'outline'}>
                <CheckCircle2 className="mr-1 h-3.5 w-3.5" />
                {safeConfidence >= 80 ? 'bereit' : safeConfidence >= 60 ? 'beobachten' : 'prüfen'}
              </Badge>
            </div>
            <Progress value={safeConfidence} className="h-2" />
            <p className="text-sm text-muted-foreground">
              Der Score verdichtet Wissensquellen, agentenfähige Commands und Idempotenz-Abdeckung zu einem UX-Nachweis.
            </p>
          </div>

          <div className="rounded-lg border bg-slate-900 p-4 text-slate-50 shadow-sm">
            <div className="flex items-center gap-2 text-sm font-medium text-slate-200">
              <ShieldCheck className="h-4 w-4" />
              Aktion
            </div>
            <p className="mt-2 text-sm text-slate-200">{action.description}</p>
            <Button asChild className="mt-4 w-full gap-2 bg-white text-slate-900 hover:bg-slate-100">
              <a href={action.href} target="_self" rel="noreferrer">
                {action.label}
                <ExternalLink className="h-4 w-4" />
              </a>
            </Button>
          </div>
        </div>

        <div className="space-y-3">
          <div className="flex items-center gap-2 text-sm font-medium">
            <ExternalLink className="h-4 w-4" />
            Quellen
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            {sources.map((source) => (
              <a
                key={source.label}
                href={source.href}
                target="_blank"
                rel="noreferrer"
                className="rounded-lg border bg-white p-4 transition-colors hover:border-slate-400 hover:bg-slate-50"
              >
                <div className="flex items-center justify-between gap-2">
                  <span className="font-medium">{source.label}</span>
                  <Badge variant="outline">Quelle</Badge>
                </div>
                <p className="mt-2 text-sm text-muted-foreground">{source.description}</p>
                <p className="mt-3 break-all font-mono text-xs text-slate-500">{source.href}</p>
              </a>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
