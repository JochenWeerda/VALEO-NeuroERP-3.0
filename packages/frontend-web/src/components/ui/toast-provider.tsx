import { type ReactNode, createContext, useContext } from 'react'
import { toast as sonnerToast } from 'sonner'

// Toast-Konsolidierung (DESIGN-GAPS-FOLLOWUP-013): Der Legacy-push()-
// Vertrag (42 Aufrufer) bleibt erhalten, rendert aber ueber sonner statt
// ueber den frueheren lazy ToastHost (ein einzelner, nicht stapelbarer Toast).
type Ctx = { push: (_msg: string) => void }
const ToastCtx = createContext<Ctx>({ push: (message): void => { sonnerToast(message) } })
export const useToast = (): Ctx => useContext(ToastCtx)

export function ToastProvider({ children }: { children: ReactNode }): JSX.Element {
  return <>{children}</>
}
