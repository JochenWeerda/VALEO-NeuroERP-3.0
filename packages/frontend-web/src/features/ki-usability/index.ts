/**
 * KI Usability feature: PageToolbar + Sprachsteuerung + Tastaturkürzel (einheitlich)
 */

export { ActionDispatchProvider } from './context/ActionDispatchContext'
export { useActionDispatch, useActionDispatchOptional } from './context/ActionDispatchHooks'
export { VoiceButton } from './components/VoiceButton'
export { VoiceFeedback } from './components/VoiceFeedback'
export { VoiceWhisperBarHost } from './components/VoiceWhisperBarHost'
export { useVoiceIntent } from './hooks/useVoiceIntent'
export { useVoicePlayback } from './hooks/useVoicePlayback'
export { useWhisperBarShortcuts } from './hooks/useWhisperBarShortcuts'
export { useActionsForMask } from './hooks/useActionsForMask'
export { useGlobalShortcutsWithVoice } from './hooks/useGlobalShortcutsWithVoice'
export { fetchActions, fetchAction } from './api/actions'
export type { Action, ActionListResponse } from './api/actions'
export { buildToolbarActionsFromRegistry } from './toolbar-actions'
export { resolveVoice, polishVoice, summarizeVoice, synthesizeVoice, runVoicePipeline } from './api/voice'
export type {
  VoiceResolveRequest,
  VoiceResolveResponse,
  VoicePolishRequest,
  VoicePolishResponse,
  VoiceSummaryRequest,
  VoiceSummaryResponse,
  VoiceSynthesizeRequest,
  VoiceSynthesizeResponse,
  VoicePipelineRequest,
  VoicePipelineResponse,
} from './api/voice'
export {
  limitItemsForDensity,
  limitProcessDetails,
  mergeToolbarActionsForDensity,
  resolveRoleDensityProfile,
} from '@/features/role-density'
export type { InformationDensity, RoleDensityProfile } from '@/features/role-density'

