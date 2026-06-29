// VALEO Mask Builder Framework
// Wiederverwendbare Komponenten für schnelle Masken-Erstellung

export { default as ObjectPage } from './ObjectPage'
export { default as ListReport } from './ListReport'
export { default as Wizard } from './Wizard'
export { default as Worklist } from './Worklist'
export { default as OverviewPage } from './OverviewPage'
export { UniversalMaskRenderer } from './UniversalMaskRenderer'
export * from './renderers'
export * from './schema'
export * from './render-plan'
export { adaptMaskConfigToScreenDefinition } from './adapters/mask-config-adapter'

// export * from './fields' // Not implemented yet
// export * from './layouts' // Not implemented yet
export * from './hooks'
export * from './utils'
// Runtime layer (Phase 020-025)
export type { DataBindingPlan, TableQueryState, FilterPlan, FilterValue, FilterOperator, LookupBinding } from './runtime/types'
export type { UniversalFormState, ValidationPlan, ValidationRule, FieldError, DirtyState, SubmitState } from './runtime/FormState'
export { useUniversalMaskRuntime } from './runtime/useUniversalMaskRuntime'
export { useUniversalFormState } from './runtime/useUniversalFormState'
export { compileDataBindingPlan } from './runtime/compile-data-binding-plan'
export type { ActionRequest, ActionResult, ActionExecutionMode, ActionPolicy } from './runtime/ActionRuntime'
export { buildActionPolicy, checkActionPolicy } from './runtime/ActionRuntime'
export { useActionRuntime, useHumanActionDispatch, useAgentActionDispatch } from './runtime/useActionRuntime'
export type { WorkflowState, WorkflowStatusInfo, NextAllowedAction, BlockingReason, AuditTrailEntry, PolicyHint } from './runtime/WorkflowRuntime'
export { buildWorkflowState } from './runtime/WorkflowRuntime'
export { useWorkflowState } from './runtime/useWorkflowState'
// Phase 029 — AgentMaskContract
export { generateAgentMaskContract } from './runtime/generateAgentMaskContract'
export { useAgentMaskContract, useLocalAgentMaskContract } from './runtime/useAgentMaskContract'
// Phase 030 — Generator Readiness Gates
export { checkGeneratorReadiness } from './runtime/generatorReadiness'
export type { GeneratorReadinessReport, GateResult, ReadinessGate, GateSeverity } from './runtime/generatorReadiness'
