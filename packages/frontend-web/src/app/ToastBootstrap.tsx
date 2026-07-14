import { type ReactNode } from 'react'
import { Toaster as SonnerToaster } from 'sonner'
import { ToastProvider } from '@/components/ui/toast-provider'
import { Toaster } from '@/components/ui/toaster'

export default function ToastBootstrap({ children }: { children: ReactNode }): JSX.Element {
  // Drei Toast-Systeme koexistieren: der Legacy-push()-Provider, der
  // shadcn-Toaster (@/hooks/use-toast, ~250 Seiten) und sonner (40+ Seiten,
  // v. a. Fibu/Stammdaten). shadcn war bis zur Gesamtsimulation 2026-07-02 nie
  // gemountet; dasselbe galt für sonner bis 2026-07-14 — dessen toast()-Aufrufe
  // blieben unsichtbar. Konsolidierung auf ein System ist Folgearbeit.
  return (
    <ToastProvider>
      {children}
      <Toaster />
      <SonnerToaster richColors closeButton />
    </ToastProvider>
  )
}
