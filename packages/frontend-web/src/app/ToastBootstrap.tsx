import { type ReactNode } from 'react'
import { ToastProvider } from '@/components/ui/toast-provider'

export default function ToastBootstrap({ children }: { children: ReactNode }): JSX.Element {
  return <ToastProvider>{children}</ToastProvider>
}
