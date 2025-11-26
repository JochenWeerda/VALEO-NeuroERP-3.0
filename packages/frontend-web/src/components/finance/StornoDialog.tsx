/**
 * Storno Dialog Component
 * Dialog for reversing/storno journal entries with reason input
 */

import { useState } from 'react'
import { useTranslation } from 'react-i18next'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { AlertCircle } from 'lucide-react'

interface StornoDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onConfirm: (reason: string) => Promise<void>
  entryNumber?: string
  entryDate?: string
  isLoading?: boolean
}

export function StornoDialog({
  open,
  onOpenChange,
  onConfirm,
  entryNumber,
  entryDate,
  isLoading = false,
}: StornoDialogProps): JSX.Element {
  const { t } = useTranslation()
  const [reason, setReason] = useState('')
  const [error, setError] = useState<string | null>(null)

  const handleConfirm = async () => {
    if (!reason.trim() || reason.trim().length < 10) {
      setError(t('crud.dialogs.storno.reasonMinLength'))
      return
    }

    setError(null)
    try {
      await onConfirm(reason.trim())
      setReason('')
      onOpenChange(false)
    } catch (err) {
      setError(err instanceof Error ? err.message : t('crud.messages.stornoError'))
    }
  }

  const handleCancel = () => {
    setReason('')
    setError(null)
    onOpenChange(false)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-[500px]">
        <DialogHeader>
          <DialogTitle>{t('crud.dialogs.storno.title')}</DialogTitle>
          <DialogDescription>
            {t('crud.dialogs.storno.description', {
              entryNumber: entryNumber || '',
              entryDate: entryDate || '',
            })}
          </DialogDescription>
        </DialogHeader>

        <div className="space-y-4 py-4">
          {entryNumber && (
            <div className="space-y-2">
              <Label>{t('crud.fields.documentNumber')}</Label>
              <div className="text-sm font-mono text-muted-foreground">{entryNumber}</div>
            </div>
          )}

          {entryDate && (
            <div className="space-y-2">
              <Label>{t('crud.fields.bookingDate')}</Label>
              <div className="text-sm text-muted-foreground">{entryDate}</div>
            </div>
          )}

          <div className="space-y-2">
            <Label htmlFor="storno-reason">
              {t('crud.dialogs.storno.reasonLabel')} *
            </Label>
            <Textarea
              id="storno-reason"
              value={reason}
              onChange={(e) => {
                setReason(e.target.value)
                setError(null)
              }}
              placeholder={t('crud.dialogs.storno.reasonPlaceholder')}
              rows={4}
              className="resize-none"
            />
            <p className="text-xs text-muted-foreground">
              {t('crud.dialogs.storno.reasonHint')}
            </p>
          </div>

          {error && (
            <Alert variant="destructive">
              <AlertCircle className="h-4 w-4" />
              <AlertDescription>{error}</AlertDescription>
            </Alert>
          )}

          <Alert>
            <AlertCircle className="h-4 w-4" />
            <AlertDescription>
              {t('crud.dialogs.storno.warning')}
            </AlertDescription>
          </Alert>
        </div>

        <DialogFooter>
          <Button
            type="button"
            variant="outline"
            onClick={handleCancel}
            disabled={isLoading}
          >
            {t('crud.actions.cancel')}
          </Button>
          <Button
            type="button"
            variant="destructive"
            onClick={handleConfirm}
            disabled={isLoading || !reason.trim() || reason.trim().length < 10}
          >
            {isLoading ? t('common.loading') : t('crud.actions.reverse')}
          </Button>
        </DialogFooter>
      </DialogContent>
    </Dialog>
  )
}

