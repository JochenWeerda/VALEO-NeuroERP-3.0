import { createContext, useContext } from 'react'
import type { LookupBinding } from './types'

export const LookupBindingContext = createContext<Record<string, LookupBinding>>({})

export function useLookupBindingContext(): Record<string, LookupBinding> {
  return useContext(LookupBindingContext)
}
