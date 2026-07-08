/**
 * Prozessband-Compiler (UIX-091) — rein & testbar.
 *
 * Leitet aus einer deklarativen Prozesskette + aktuellem Schritt ein
 * navigierbares Band ab. v1: Zustand nur 'current' (aus stepKey) vs. neutral
 * ('upcoming'); 'done'/'upcoming'-Differenzierung folgt mit Instanz-Kontext (v2).
 * Unbekannte chainId → kein Ribbon + Warnung (nie ein Fehler).
 */
export interface ProcessChainStep {
  key: string
  label: string
  screenId: string
}

export interface ProcessChain {
  label: string
  steps: ProcessChainStep[]
}

export type ProcessStepState = 'done' | 'current' | 'upcoming'

export interface ProcessRibbonStep {
  key: string
  label: string
  screenId: string
  routePath: string
  state: ProcessStepState
}

export interface ProcessRibbon {
  chainId: string
  label: string
  steps: ProcessRibbonStep[]
}

export interface CompileRibbonResult {
  ribbon: ProcessRibbon | null
  warnings: string[]
}

export function compileProcessRibbon(
  chainId: string,
  stepKey: string | undefined,
  chains: Record<string, ProcessChain>,
  resolveRoute: (_screenId: string) => string | undefined,
): CompileRibbonResult {
  const chain = chains[chainId]
  if (!chain) {
    return { ribbon: null, warnings: [`unknown_chain:${chainId}`] }
  }

  const warnings: string[] = []
  const hasCurrent = stepKey !== undefined && chain.steps.some((s) => s.key === stepKey)
  if (stepKey !== undefined && !hasCurrent) {
    warnings.push(`unknown_step:${chainId}:${stepKey}`)
  }

  const steps: ProcessRibbonStep[] = chain.steps.map((step) => {
    const routePath = resolveRoute(step.screenId) ?? ''
    if (!routePath) warnings.push(`unresolved_route:${step.screenId}`)
    return {
      key: step.key,
      label: step.label,
      screenId: step.screenId,
      routePath,
      // v1: nur der getroffene Schritt ist 'current', der Rest neutral.
      state: step.key === stepKey ? 'current' : 'upcoming',
    }
  })

  return { ribbon: { chainId, label: chain.label, steps }, warnings }
}
