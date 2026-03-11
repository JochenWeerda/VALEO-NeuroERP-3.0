import * as Toast from '@radix-ui/react-toast'

type ToastHostProps = {
  open: boolean
  message: string
  onOpenChange: (open: boolean) => void
}

export default function ToastHost({ open, message, onOpenChange }: ToastHostProps): JSX.Element {
  return (
    <Toast.Provider swipeDirection="right">
      <Toast.Root open={open} onOpenChange={onOpenChange} className="rounded-xl border bg-background p-3 shadow">
        <Toast.Title className="font-medium">Notification</Toast.Title>
        <Toast.Description className="opacity-80">{message}</Toast.Description>
      </Toast.Root>
      <Toast.Viewport className="fixed bottom-4 right-4 w-96" />
    </Toast.Provider>
  )
}
