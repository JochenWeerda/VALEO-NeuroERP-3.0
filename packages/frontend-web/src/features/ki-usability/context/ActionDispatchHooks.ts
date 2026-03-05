import { useContext } from 'react'
import { ActionDispatchContext, type ActionDispatchContextValue } from './ActionDispatchContext'

export function useActionDispatch(): ActionDispatchContextValue {
  const ctx = useContext(ActionDispatchContext)
  if (!ctx) {
    throw new Error('useActionDispatch must be used within ActionDispatchProvider')
  }
  return ctx
}

export function useActionDispatchOptional(): ActionDispatchContextValue | null {
  return useContext(ActionDispatchContext)
}
