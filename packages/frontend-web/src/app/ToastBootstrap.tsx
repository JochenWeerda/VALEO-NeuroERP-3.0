import { type ReactNode } from 'react'
import { ToastProvider } from '@/components/ui/toast-provider'
import { Toaster } from '@/components/ui/toaster'

export default function ToastBootstrap({ children }: { children: ReactNode }): JSX.Element {
  // Zwei Toast-Systeme koexistieren: der Legacy-push()-Provider und der
  // shadcn-Toaster (@/hooks/use-toast), den ~250 Seiten nutzen. Letzterer war
  // nie global gemountet — sämtliche toast()-Aufrufe blieben unsichtbar.
  return (
    <ToastProvider>
      {children}
      <Toaster />
    </ToastProvider>
  )
}
