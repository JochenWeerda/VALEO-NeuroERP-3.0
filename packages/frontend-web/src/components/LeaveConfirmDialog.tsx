'use client'

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'

export interface BlockerLike {
  state: string
  proceed: () => void
  reset: () => void
}

interface LeaveConfirmDialogProps {
  /** Blocker von useUnsavedChanges / useBlocker. Dialog wird nur bei state === 'blocked' angezeigt. */
  blocker: BlockerLike | null
  /** Beim Klick „Speichern“: wird aufgerufen; nach erfolgreichem Speichern wird proceed() ausgeführt. Kann async sein. */
  onSave?: () => void | Promise<void>
  /** Titel des Dialogs. */
  title?: string
  /** Beschreibungstext. */
  description?: string
}

export function LeaveConfirmDialog({
  blocker,
  onSave,
  title = 'Ungespeicherte Änderungen',
  description = 'Möchten Sie Ihre Änderungen speichern, bevor Sie die Seite verlassen?',
}: LeaveConfirmDialogProps): JSX.Element | null {
  const [saving, setSaving] = useState(false)

  if (!blocker || blocker.state !== 'blocked') return null

  const handleSave = async (): Promise<void> => {
    if (!onSave) {
      blocker.proceed()
      return
    }
    setSaving(true)
    try {
      await onSave()
      blocker.proceed()
    } finally {
      setSaving(false)
    }
  }

  const handleDiscard = (): void => {
    blocker.proceed()
  }

  const handleCancel = (): void => {
    blocker.reset()
  }

  return (
    <Dialog open onOpenChange={(open) => { if (!open) handleCancel() }}>
      <DialogContent className="sm:max-w-md" onPointerDownOutside={handleCancel} onEscapeKeyDown={handleCancel}>
        <DialogHeader>
          <DialogTitle>{title}</DialogTitle>
          <DialogDescription>{description}</DialogDescription>
        </DialogHeader>
        <DialogFooter className="gap-2 sm:gap-0">
          <Button variant="outline" onClick={handleCancel} disabled={saving}>
            Abbrechen
          </Button>
          <Button variant="secondary" onClick={handleDiscard} disabled={saving}>
            Verwerfen
          </Button>
          {onSave && (
            <Button onClick={handleSave} disabled={saving}>
              {saving ? 'Speichern…' : 'Speichern'}
            </Button>
          )}
          {!onSave && (
            <Button onClick={handleDiscard} disabled={saving}>
              Verlassen
            </Button>
          )}
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}
