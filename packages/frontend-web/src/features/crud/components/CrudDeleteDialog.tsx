/**
 * CrudDeleteDialog Component
 * Dialog for deleting entities with required reason field
 */

import React, { useState } from 'react';
import { useTranslation } from 'react-i18next';
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
} from '@/components/ui/alert-dialog';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { getEntityTypeLabel } from '@/features/crud/utils/i18n-helpers';

export interface CrudDeleteDialogProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onConfirm: (reason: string) => void | Promise<void>;
  entityName?: string;
  entityType?: string;
  isLoading?: boolean;
}

export function CrudDeleteDialog({
  open,
  onOpenChange,
  onConfirm,
  entityName,
  entityType = 'Entity',
  isLoading = false,
}: CrudDeleteDialogProps) {
  const { t } = useTranslation();
  const [reason, setReason] = useState('');
  const [error, setError] = useState('');

  // Get entity type translation
  const entityTypeTranslated = getEntityTypeLabel(t, entityType, entityType);

  const handleConfirm = async () => {
    if (!reason || reason.trim().length === 0) {
      setError(t('crud.dialogs.delete.errorRequired'));
      return;
    }

    if (reason.trim().length < 10) {
      setError(t('crud.dialogs.delete.errorMinLength'));
      return;
    }

    setError('');
    await onConfirm(reason.trim());
    setReason('');
    onOpenChange(false);
  };

  const handleCancel = () => {
    setReason('');
    setError('');
    onOpenChange(false);
  };

  return (
    <AlertDialog open={open} onOpenChange={onOpenChange}>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>
            {t('crud.dialogs.delete.title', { entityType: entityTypeTranslated })}
          </AlertDialogTitle>
          <AlertDialogDescription>
            {entityName ? (
              <>
                {t('crud.dialogs.delete.description', {
                  entityName: <strong key="name">{entityName}</strong>,
                })}
              </>
            ) : (
              t('crud.dialogs.delete.descriptionGeneric', { entityType: entityTypeTranslated })
            )}
            <br />
            <br />
            {t('crud.dialogs.delete.warning')}
          </AlertDialogDescription>
        </AlertDialogHeader>
        <div className="space-y-4 py-4">
          <div className="space-y-2">
            <Label htmlFor="delete-reason">
              {t('crud.dialogs.delete.reasonRequired')}
            </Label>
            <Textarea
              id="delete-reason"
              value={reason}
              onChange={(e) => {
                setReason(e.target.value);
                setError('');
              }}
              placeholder={t('crud.dialogs.delete.reasonPlaceholder')}
              rows={4}
              className={error ? 'border-red-500' : ''}
            />
            {error && (
              <p className="text-sm text-red-500">{error}</p>
            )}
            <p className="text-xs text-muted-foreground">
              {t('crud.dialogs.delete.reasonMinLength')}
            </p>
          </div>
        </div>
        <AlertDialogFooter>
          <AlertDialogCancel onClick={handleCancel} disabled={isLoading}>
            {t('crud.dialogs.delete.cancelButton')}
          </AlertDialogCancel>
          <AlertDialogAction
            onClick={handleConfirm}
            disabled={isLoading || !reason || reason.trim().length < 10}
            className="bg-red-600 hover:bg-red-700"
          >
            {isLoading ? t('crud.dialogs.delete.confirming') : t('crud.dialogs.delete.confirmButton')}
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  );
}

