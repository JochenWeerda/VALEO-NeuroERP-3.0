import { createContext, useContext } from 'react'
import type { UniversalFormState } from './FormState'

export const FormStateContext = createContext<UniversalFormState | undefined>(undefined)

export function useFormStateContext(): UniversalFormState | undefined {
  return useContext(FormStateContext)
}
