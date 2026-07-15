import { type ReactNode } from 'react'
import { Toaster as SonnerToaster } from 'sonner'

export default function ToastBootstrap({ children }: { children: ReactNode }): JSX.Element {
  // Toast-Konsolidierung (DESIGN-GAPS-FOLLOWUP-013): sonner ist der
  // einzige Toast-Renderer. Die frueheren Parallel-Systeme delegieren nur noch:
  // @/hooks/use-toast (shadcn-API, 255 Aufrufer) und der Legacy-push()-Vertrag
  // (@/components/ui/toast-provider, 42 Aufrufer) rufen intern sonner auf.
  return (
    <>
      {children}
      <SonnerToaster richColors closeButton />
    </>
  )
}
