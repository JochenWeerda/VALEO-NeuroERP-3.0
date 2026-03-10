import { type ReactNode } from 'react'

type GlobalShortcutProviderProps = {
  children: ReactNode
}

export function GlobalShortcutProvider({ children }: GlobalShortcutProviderProps): JSX.Element {
  return <>{children}</>
}
