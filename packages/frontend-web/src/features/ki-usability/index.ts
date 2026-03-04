/**
 * KI Usability feature: PageToolbar + Sprachsteuerung + Tastaturkürzel (einheitlich)
 */

export { ActionDispatchProvider, useActionDispatch, useActionDispatchOptional } from './context/ActionDispatchContext'
export { VoiceButton } from './components/VoiceButton'
export { VoiceFeedback } from './components/VoiceFeedback'
export { useVoiceIntent } from './hooks/useVoiceIntent'
export { useActionsForMask } from './hooks/useActionsForMask'
export { useGlobalShortcutsWithVoice } from './hooks/useGlobalShortcutsWithVoice'
export { fetchActions, fetchAction } from './api/actions'
export type { Action, ActionListResponse } from './api/actions'
export { resolveVoice } from './api/voice'
export type { VoiceResolveRequest, VoiceResolveResponse } from './api/voice'
