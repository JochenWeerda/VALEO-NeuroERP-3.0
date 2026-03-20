import * as React from 'react'
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

interface DetailDrawerProps {
  title: string
  open: boolean
  onClose?: () => void
  onOpenChange?: (_open: boolean) => void
  children: React.ReactNode
}

export function DetailDrawer({ title, open, onClose, onOpenChange, children }: DetailDrawerProps): JSX.Element {
  const handleOpenChange = (nextOpen: boolean): void => {
    if (typeof onOpenChange === 'function') {
      onOpenChange(nextOpen)
      return
    }
    if (!nextOpen) {
      onClose?.()
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogContent className="max-w-2xl">
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
        </DialogHeader>
        <div className="space-y-3">{children}</div>
        <div className="flex justify-end pt-4">
          <Button onClick={() => onClose?.()}>Close</Button>
        </div>
      </DialogContent>
    </Dialog>
  )
}
