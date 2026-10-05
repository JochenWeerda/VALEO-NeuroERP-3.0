// Toast-Konsolidierung (DESIGN-GAPS-FOLLOWUP-013): Dieses Modul behaelt
// die shadcn-use-toast-API (255 Aufrufer), rendert aber ueber sonner — den
// einzigen global gemounteten Toast-Renderer (app/ToastBootstrap.tsx).
// Der fruehere lokale Store + <Toaster /> (TOAST_LIMIT 1, nie sichtbar
// gestapelt) entfaellt; Tests, die '@/hooks/use-toast' mocken, bleiben gueltig.
import * as React from "react"
import { toast as sonnerToast } from "sonner"

type ToastVariant = "default" | "destructive"

interface ToastOptions {
  title?: React.ReactNode
  description?: React.ReactNode
  variant?: ToastVariant
  duration?: number
  /** Optionale Aktions-Schaltfläche im Toast (sonner rendert ReactNode direkt). */
  action?: React.ReactNode
}

type ToasterToast = ToastOptions & { id: string }

type Toast = ToastOptions

type ToastHandle = {
  id: string
  dismiss: () => void
  update: (props: Toast) => void
}

type ShortcutToastProps = Omit<Toast, "title" | "variant" | "description"> & {
  description?: string
}

type ToastFn = ((props: Toast) => ToastHandle) & {
  success: (_title: string, _descriptionOrProps?: string | ShortcutToastProps, _props?: ShortcutToastProps) => ToastHandle
  error: (_title: string, _descriptionOrProps?: string | ShortcutToastProps, _props?: ShortcutToastProps) => ToastHandle
  info: (_title: string, _descriptionOrProps?: string | ShortcutToastProps, _props?: ShortcutToastProps) => ToastHandle
  warning: (_title: string, _descriptionOrProps?: string | ShortcutToastProps, _props?: ShortcutToastProps) => ToastHandle
}

type SonnerKind = "message" | "success" | "error" | "info" | "warning"

function emit(kind: SonnerKind, props: Toast, id?: string | number): ToastHandle {
  const message = props.title ?? props.description ?? ""
  const options = {
    id,
    description: props.title !== undefined && props.title !== null ? props.description : undefined,
    duration: props.duration,
    action: props.action,
  }
  const emitter = kind === "message" ? sonnerToast : sonnerToast[kind]
  const toastId = emitter(message, options)
  return {
    id: String(toastId),
    dismiss: (): void => { sonnerToast.dismiss(toastId) },
    update: (updateProps: Toast): void => { emit(kind, updateProps, toastId) },
  }
}

function baseToast(props: Toast): ToastHandle {
  return emit(props.variant === "destructive" ? "error" : "message", props)
}

const toast = baseToast as ToastFn

const isShortcutToastProps = (value: unknown): value is ShortcutToastProps =>
  value !== null
  && typeof value === "object"
  && !Array.isArray(value)
  && React.isValidElement(value) === false

const normalizeShortcutToastProps = (
  title: string,
  descriptionOrProps?: string | ShortcutToastProps,
  props?: ShortcutToastProps,
): Toast => {
  if (isShortcutToastProps(descriptionOrProps)) {
    return { ...descriptionOrProps, title, description: descriptionOrProps.description }
  }
  return { ...(props ?? {}), title, description: descriptionOrProps }
}

toast.success = (title, descriptionOrProps, props) =>
  emit("success", normalizeShortcutToastProps(title, descriptionOrProps, props))

toast.error = (title, descriptionOrProps, props) =>
  emit("error", normalizeShortcutToastProps(title, descriptionOrProps, props))

toast.info = (title, descriptionOrProps, props) =>
  emit("info", normalizeShortcutToastProps(title, descriptionOrProps, props))

toast.warning = (title, descriptionOrProps, props) =>
  emit("warning", normalizeShortcutToastProps(title, descriptionOrProps, props))

function useToast(): {
  toasts: ToasterToast[]
  toast: typeof toast
  dismiss: (_toastId?: string) => void
} {
  // sonner haelt den Toast-Zustand selbst; `toasts` bleibt nur als leere
  // Kompatibilitaetsflaeche fuer die bisherige Hook-Signatur erhalten.
  return {
    toasts: [],
    toast,
    dismiss: (_toastId?: string): void => { sonnerToast.dismiss(_toastId) },
  }
}

export { useToast, toast }
export type { ToasterToast }
