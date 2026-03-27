import { type ReactNode, useMemo, useState } from 'react'
import { PageToolbar, type ToolbarAction } from '@/components/navigation/PageToolbar'
import { Button } from '@/components/ui/button'
import { cn } from '@/lib/utils'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'
import { Check, Loader2 } from 'lucide-react'
import { buildToolbarActionsFromRegistry, useActionsForMask, useActionDispatchOptional } from '@/features/ki-usability'
import { auth } from '@/lib/auth'
import { resolveRoleDensityProfile } from '@/features/role-density'
import { useTenant } from '@/hooks/useTenant'
import { useUIDensityManifest } from '@/lib/api/ui-density-manifest'
import { PageSection, PageSurface } from '@/components/patterns/PageSurface'

interface WizardLabels {
  back: string
  next: string
  finish: string
  cancel: string
}

export interface WizardStep {
  id: string
  title: string
  description?: string
  content: ReactNode
  optional?: boolean
}

export interface WizardProps {
  title: string
  subtitle?: string
  steps: WizardStep[]
  initialStepId?: string
  onStepChange?: (_stepId: string) => void
  onCancel?: () => void
  onFinish?: () => void
  onNextStep?: (_currentStepId: string) => void
  onPreviousStep?: (_currentStepId: string) => void
  getStepValidationError?: (_currentStepId: string) => string | null | Promise<string | null>
  onStepValidationError?: (_currentStepId: string, _message: string) => void
  labels?: Partial<WizardLabels>
  loading?: boolean
  allowStepNavigation?: boolean
  primaryActions?: ToolbarAction[]
  overflowActions?: ToolbarAction[]
  mcpContext?: {
    process: string
    entityType?: string
    currentDocument?: string
  }
}

export const wizardMCP = createMCPMetadata('Wizard', 'process', {
  accessibility: {
    role: 'application',
    ariaLabel: 'Multi-step wizard',
  },
  intent: {
    purpose: 'Guide users through multi-step processes',
    userActions: ['next-step', 'previous-step', 'cancel', 'finish'],
    dataContext: ['current-step', 'process'],
  },
  mcpHints: {
    explainable: true,
    contextAware: true,
    testable: true,
  },
})

const DEFAULT_LABELS: WizardLabels = {
  back: 'Zurueck',
  next: 'Weiter',
  finish: 'Abschliessen',
  cancel: 'Abbrechen',
}

export function Wizard({
  title,
  subtitle,
  steps,
  initialStepId,
  onStepChange,
  onCancel,
  onFinish,
  onNextStep,
  onPreviousStep,
  getStepValidationError,
  onStepValidationError,
  labels,
  loading = false,
  allowStepNavigation = true,
  primaryActions,
  overflowActions,
  mcpContext,
}: WizardProps): JSX.Element {
  const actionDispatch = useActionDispatchOptional()
  const { tenantId } = useTenant()
  const { data: actionResponse } = useActionsForMask(mcpContext?.process, mcpContext?.entityType)
  const mergedLabels = { ...DEFAULT_LABELS, ...labels }
  const densityManifestQuery = useUIDensityManifest(mcpContext?.process)
  const roleDensityProfile = useMemo(
    () =>
      resolveRoleDensityProfile(auth.getUser()?.roles, {
        tenantId,
        pageDomain: mcpContext?.process,
        availableActionIds: actionResponse?.actions?.map((action) => action.id) ?? [],
        backendDensity: densityManifestQuery.data?.entry?.recommended_density,
      }),
    [actionResponse?.actions, densityManifestQuery.data?.entry?.recommended_density, mcpContext?.process, tenantId],
  )

  const safeSteps = useMemo(() => steps.filter((step) => step != null), [steps])

  const fallbackStepId = safeSteps[0]?.id ?? ''

  const resolveInitialStep = (): string => {
    if (typeof initialStepId === 'string') {
      const exists = safeSteps.some((step) => step.id === initialStepId)
      if (exists) {
        return initialStepId
      }
    }
    return fallbackStepId
  }

  const [activeStepId, setActiveStepId] = useState<string>(resolveInitialStep)

  const activeIndex = useMemo(() => {
    return Math.max(0, safeSteps.findIndex((step) => step.id === activeStepId))
  }, [activeStepId, safeSteps])

  const activeStep = safeSteps[activeIndex]
  const contextualToolbarActions = useMemo(
    () => buildToolbarActionsFromRegistry(actionResponse?.actions, actionDispatch),
    [actionDispatch, actionResponse?.actions],
  )

  const mergedPrimaryActions = useMemo<ToolbarAction[]>(() => {
    if (Array.isArray(primaryActions) && primaryActions.length > 0) {
      return primaryActions
    }
    return contextualToolbarActions.primary
  }, [contextualToolbarActions.primary, primaryActions])

  const mergedOverflowActions = useMemo<ToolbarAction[]>(() => {
    const fromProps = overflowActions ?? []
    const hasPrimaryFromProps = Array.isArray(primaryActions) && primaryActions.length > 0
    const quickOverflow = hasPrimaryFromProps ? contextualToolbarActions.overflow : contextualToolbarActions.overflow
    const byId = new Map<string, ToolbarAction>()
    for (const action of [...fromProps, ...quickOverflow]) {
      byId.set(action.id, action)
    }
    return Array.from(byId.values())
  }, [contextualToolbarActions.overflow, overflowActions, primaryActions])

  const validateActiveStep = async (): Promise<boolean> => {
    if (typeof getStepValidationError !== 'function') {
      return true
    }
    const validationError = await getStepValidationError(activeStepId)
    if (!validationError) {
      return true
    }
    onStepValidationError?.(activeStepId, validationError)
    return false
  }

  const handleGoToStep = async (stepId: string, index: number): Promise<void> => {
    if (allowStepNavigation === false && index > activeIndex) {
      return
    }
    if (index > activeIndex) {
      const canProceed = await validateActiveStep()
      if (!canProceed) {
        return
      }
    }
    setActiveStepId(stepId)
    onStepChange?.(stepId)
  }

  const handleBack = (): void => {
    if (activeIndex === 0) {
      return
    }
    const prevStep = safeSteps[activeIndex - 1]
    setActiveStepId(prevStep.id)
    onPreviousStep?.(activeStepId)
    onStepChange?.(prevStep.id)
  }

  const handleNext = async (): Promise<void> => {
    const canProceed = await validateActiveStep()
    if (!canProceed) {
      return
    }
    if (activeIndex === safeSteps.length - 1) {
      onFinish?.()
      return
    }
    const nextStep = safeSteps[activeIndex + 1]
    setActiveStepId(nextStep.id)
    onNextStep?.(activeStepId)
    onStepChange?.(nextStep.id)
  }

  return (
    <div
      className="flex h-full flex-col"
      data-mcp-pattern="wizard"
      data-mcp-process={mcpContext?.process}
      data-mcp-entity={mcpContext?.entityType}
    >
      <PageToolbar
        title={title}
        subtitle={subtitle}
        primaryActions={mergedPrimaryActions}
        overflowActions={mergedOverflowActions}
        densityProfileOverride={roleDensityProfile}
        mcpContext={
          mcpContext
            ? {
                pageDomain: mcpContext.process,
                currentDocument: mcpContext.currentDocument,
                availableActions: [
                  ...mergedPrimaryActions.map((action) => action.id),
                  ...mergedOverflowActions.map((action) => action.id),
                ],
              }
            : undefined
        }
      />

      <PageSurface data-page-surface="wizard-pattern" contentClassName="space-y-6">
        <nav aria-label="Wizard steps">
          <ol className="flex flex-wrap items-center gap-3">
            {safeSteps.map((step, index) => {
              const isCompleted = index < activeIndex
              const isActive = index === activeIndex
              const StepIcon = isCompleted ? Check : undefined

              return (
                <li key={step.id}>
                  <button
                    type="button"
                    onClick={() => void handleGoToStep(step.id, index)}
                    className={cn(
                      'flex items-center gap-2 rounded-full border px-4 py-2 text-sm transition-colors',
                      isActive && 'border-primary bg-primary/10 text-primary',
                      !isActive && isCompleted && 'border-primary/50 bg-primary/5 text-primary',
                      !isActive && !isCompleted && 'border-muted bg-muted/40 text-muted-foreground',
                      allowStepNavigation === false && index > activeIndex && 'cursor-not-allowed opacity-60',
                    )}
                    disabled={allowStepNavigation === false && index > activeIndex}
                  >
                    {StepIcon ? <StepIcon className="h-4 w-4" /> : <span className="text-xs">{index + 1}</span>}
                    <span>{step.title}</span>
                    {step.optional === true ? <span className="text-xs text-muted-foreground">(optional)</span> : null}
                  </button>
                </li>
              )
            })}
          </ol>
        </nav>

        <div className="h-px bg-border" role="presentation" />

        <PageSection
          title={activeStep?.title}
          description={roleDensityProfile.density !== 'focused' ? activeStep?.description : undefined}
          className="shadow-sm shadow-primary/5"
        >
          <div className="min-h-touch" data-mcp-step={activeStep?.id}>
            {activeStep?.content ?? (
              <p className="text-sm text-muted-foreground">Kein Inhalt fuer diesen Schritt vorhanden.</p>
            )}
          </div>
        </PageSection>
      </PageSurface>

      <footer className="border-t bg-muted/40 px-6 py-4">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-2">
            {typeof onCancel === 'function' ? (
              <Button variant="ghost" onClick={onCancel} disabled={loading}>
                {mergedLabels.cancel}
              </Button>
            ) : (
              <span className="text-xs text-muted-foreground">
                Schritt {activeIndex + 1} von {safeSteps.length}
              </span>
            )}
          </div>

          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={handleBack} disabled={activeIndex === 0 || loading}>
              {mergedLabels.back}
            </Button>
            <Button onClick={() => void handleNext()} disabled={loading}>
              {loading ? (
                <>
                  <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                  {mergedLabels.next}
                </>
              ) : activeIndex === safeSteps.length - 1 ? (
                mergedLabels.finish
              ) : (
                mergedLabels.next
              )}
            </Button>
          </div>
        </div>
      </footer>
    </div>
  )
}
