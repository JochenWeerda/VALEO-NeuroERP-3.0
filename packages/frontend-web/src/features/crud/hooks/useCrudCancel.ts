/**
 * useCrudCancel Hook
 * Hook for cancel operations with reason requirement
 */

import { useState } from 'react';

export interface UseCrudCancelOptions {
  onCancel: (id: string, reason: string) => Promise<void>;
  entityType?: string;
}

export interface UseCrudCancelReturn {
  cancelDialogOpen: boolean;
  setCancelDialogOpen: (open: boolean) => void;
  handleCancel: (id: string, entityName?: string) => void;
  handleConfirmCancel: (reason: string) => Promise<void>;
  isCancelling: boolean;
  entityToCancel: { id: string; name?: string } | null;
}

export function useCrudCancel({
  onCancel,
  entityType = 'Entity',
}: UseCrudCancelOptions): UseCrudCancelReturn {
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [isCancelling, setIsCancelling] = useState(false);
  const [entityToCancel, setEntityToCancel] = useState<{
    id: string;
    name?: string;
  } | null>(null);

  const handleCancel = (id: string, entityName?: string) => {
    setEntityToCancel({ id, name: entityName });
    setCancelDialogOpen(true);
  };

  const handleConfirmCancel = async (reason: string) => {
    if (!entityToCancel) {
      throw new Error('No entity selected for cancellation');
    }

    setIsCancelling(true);
    try {
      await onCancel(entityToCancel.id, reason);
      setEntityToCancel(null);
      setCancelDialogOpen(false);
    } catch (error) {
      throw error;
    } finally {
      setIsCancelling(false);
    }
  };

  return {
    cancelDialogOpen,
    setCancelDialogOpen,
    handleCancel,
    handleConfirmCancel,
    isCancelling,
    entityToCancel,
  };
}

