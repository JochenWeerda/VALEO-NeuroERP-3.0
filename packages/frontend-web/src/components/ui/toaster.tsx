import type { ReactElement } from 'react'

import { type ToasterToast, useToast } from '@/hooks/use-toast'
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from '@/components/ui/toast'

export function Toaster(): ReactElement {
  const { toasts } = useToast()

  return (
    <ToastProvider>
      {toasts.map(({ id, title, description, action, ...toastProps }: ToasterToast) => {
        const hasTitle = title !== undefined && title !== null
        const hasDescription = description !== undefined && description !== null
        const resolvedAction = action ?? null

        return (
          <Toast key={id} {...toastProps}>
            <div className="grid gap-1">
              {hasTitle ? <ToastTitle>{title}</ToastTitle> : null}
              {hasDescription ? <ToastDescription>{description}</ToastDescription> : null}
            </div>
            {resolvedAction}
            <ToastClose />
          </Toast>
        )
      })}
      <ToastViewport />
    </ToastProvider>
  )
}
