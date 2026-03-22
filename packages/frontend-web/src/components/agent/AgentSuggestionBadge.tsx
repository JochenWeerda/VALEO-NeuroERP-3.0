/**
 * AgentSuggestionBadge — Inline agent suggestion panel for Wizard steps.
 *
 * Renders a compact violet card inside any Wizard step. The agent is triggered
 * on demand (or auto-triggered). When a suggestion is ready, the user can
 * accept it (fills form fields) or dismiss it.
 *
 * Usage:
 *   <AgentSuggestionBadge
 *     capabilityKey="rohware_annahme_assistant"
 *     parameters={{ lieferant: form.lieferant }}
 *     renderSuggestion={(s) => <span>{s.artikel}</span>}
 *     onAccept={(s) => updateField('artikel', s.artikel)}
 *   />
 */
import { useState } from 'react'
import { Badge } from '@/components/ui/badge'
import { Button } from '@/components/ui/button'
import { Sparkles, Check, X, ChevronDown, ChevronUp, Loader2, AlertCircle } from 'lucide-react'
import { useAgentSuggestion } from '@/hooks/useAgentSuggestion'
import { getCapabilityByKey } from '@/lib/agentCapabilities'
import { cn } from '@/lib/utils'

interface AgentSuggestionBadgeProps<T = Record<string, unknown>> {
  capabilityKey: string
  parameters: Record<string, unknown>
  renderSuggestion: (suggestion: T) => React.ReactNode
  onAccept: (suggestion: T) => void
  /** Label override; defaults to capability title */
  label?: string
  className?: string
  /** Automatically trigger when component mounts */
  autoTrigger?: boolean
  extractSuggestion?: (result: unknown) => T | null
}

export function AgentSuggestionBadge<T = Record<string, unknown>>({
  capabilityKey,
  parameters,
  renderSuggestion,
  onAccept,
  label,
  className,
  extractSuggestion,
}: AgentSuggestionBadgeProps<T>): JSX.Element | null {
  const [expanded, setExpanded] = useState(true)
  const capability = getCapabilityByKey(capabilityKey)
  const agent = useAgentSuggestion<T>(capabilityKey, parameters, { extractSuggestion })

  const displayLabel = label ?? capability?.title ?? 'Agent'

  const handleAccept = (): void => {
    if (agent.suggestion) {
      onAccept(agent.suggestion)
      agent.accept()
    }
  }

  if (agent.status === 'accepted' || agent.status === 'dismissed') return null

  return (
    <div
      className={cn(
        'rounded-lg border border-violet-200 bg-violet-50 p-3 text-sm',
        className,
      )}
    >
      {/* Header row */}
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <Sparkles className="h-4 w-4 text-violet-600 shrink-0" />
          <span className="font-medium text-violet-900 truncate">{displayLabel}</span>
          {agent.isLoading && <Loader2 className="h-3 w-3 animate-spin text-violet-500 shrink-0" />}
          {agent.status === 'ready' && (
            <Badge variant="outline" className="text-xs text-violet-700 border-violet-300 shrink-0">
              Vorschlag bereit
            </Badge>
          )}
          {agent.status === 'error' && (
            <AlertCircle className="h-3 w-3 text-red-500 shrink-0" />
          )}
        </div>

        <div className="flex items-center gap-1 shrink-0">
          {agent.status === 'idle' && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs text-violet-700 hover:bg-violet-100"
              onClick={agent.trigger}
            >
              Analysieren
            </Button>
          )}
          {agent.status === 'error' && (
            <Button
              variant="ghost"
              size="sm"
              className="h-7 text-xs text-slate-500 hover:bg-slate-100"
              onClick={agent.reset}
            >
              Erneut versuchen
            </Button>
          )}
          {agent.status === 'ready' && expanded && (
            <>
              <Button
                variant="ghost"
                size="sm"
                className="h-7 text-xs text-violet-700 hover:bg-violet-100 gap-1"
                onClick={handleAccept}
              >
                <Check className="h-3 w-3" />
                Übernehmen
              </Button>
              <Button
                variant="ghost"
                size="icon"
                className="h-7 w-7 text-slate-400 hover:bg-slate-100"
                onClick={agent.dismiss}
                title="Vorschlag verwerfen"
              >
                <X className="h-3 w-3" />
              </Button>
            </>
          )}
          {agent.status === 'ready' && (
            <Button
              variant="ghost"
              size="icon"
              className="h-7 w-7 text-slate-400"
              onClick={() => setExpanded((e) => !e)}
            >
              {expanded ? <ChevronUp className="h-3 w-3" /> : <ChevronDown className="h-3 w-3" />}
            </Button>
          )}
        </div>
      </div>

      {/* Suggestion content */}
      {agent.status === 'ready' && expanded && agent.suggestion != null && (
        <div className="mt-2 pt-2 border-t border-violet-200">
          {renderSuggestion(agent.suggestion)}
        </div>
      )}

      {/* Loading hint */}
      {agent.isLoading && (
        <p className="mt-1 text-xs text-violet-600">
          {capability?.description ?? 'Agent analysiert Prozesskontext…'}
        </p>
      )}
    </div>
  )
}
