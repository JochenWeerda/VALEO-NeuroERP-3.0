/**
 * Attestierungs-Dialog für gebuchte Lieferscheine
 * Erforderlich für GoBD-konforme Änderungen an gebuchten Dokumenten
 */

import { useState } from 'react'
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
  DialogFooter,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'

type AttestationAction = 'print' | 'modify' | 'cancel' | 'post' | 'reopen'

type AttestationDialogProps = {
  open: boolean
  onClose: () => void
  onConfirm: (reason: string, action: AttestationAction) => void
  action: AttestationAction
  entityType: string
  entityNumber: string
}

export function AttestationDialog({
  open,
  onClose,
  onConfirm,
  action,
  entityType,
  entityNumber,
}: AttestationDialogProps): JSX.Element {
  const [reason, setReason] = useState('')
  const [error, setError] = useState('')

  const actionLabels: Record<AttestationAction, string> = {
    print: 'Nachträglicher Druck',
    modify: 'Korrektur',
    cancel: 'Stornierung',
    post: 'Buchung',
    reopen: 'Wiedereröffnung',
  }

  const handleConfirm = (): void => {
    if (!reason.trim()) {
      setError('Begründung ist erforderlich')
      return
    }

    if (reason.trim().length < 10) {
      setError('Begründung muss mindestens 10 Zeichen lang sein')
      return
    }

    setError('')
    onConfirm(reason.trim(), action)
    setReason('')
  }

  const handleClose = (): void => {
    setReason('')
    setError('')
    onClose()
  }

  return (
    <Dialog open={open} onOpenChange={handleClose}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>Attestierung erforderlich</DialogTitle>
        </DialogHeader>

        <div className="space-y-4 py-4">
          <div>
            <Label className="text-sm font-medium">
              Dokument: {entityType} {entityNumber}
            </Label>
          </div>

          <div>
            <Label className="text-sm font-medium">
              Aktion: {actionLabels[action]}
            </Label>
          </div>

          <div className="space-y-2">
            <Label htmlFor="reason" className="text-sm font-medium">
              Begründung <span className="text-red-500">*</span>
            </Label>
            <Textarea
              id="reason"
              value={reason}
              onChange={(e) => {
                setReason(e.target.value)
                setError('')
              }}
              placeholder="Bitte geben Sie eine detaillierte Begründung für diese Aktion ein..."
              rows={4}
              className={error ? 'border-red-500' : ''}
            />
            {error && (
              <p className="text-sm text-red-500">{error}</p>
            )}
            <p className="text-xs text-muted-foreground">
              Mindestens 10 Zeichen erforderlich. Diese Begründung wird im Audit-Log gespeichert.
            </p>
          </div>
        </div>

        <DialogFooter>
          <Button variant="outline" onClick={handleClose}>
            Abbrechen
          </Button>
          <Button onClick={handleConfirm} disabled={!reason.trim() || reason.trim().length < 10}>
            Bestätigen
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

