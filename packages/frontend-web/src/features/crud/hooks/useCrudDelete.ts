/**
 * useCrudDelete Hook
 * Hook for delete operations with reason requirement
 */

import { useState } from 'react';

export interface UseCrudDeleteOptions {
  onDelete: (id: string, reason: string) => Promise<void>;
  entityType?: string;
}

export interface UseCrudDeleteReturn {
  deleteDialogOpen: boolean;
  setDeleteDialogOpen: (open: boolean) => void;
  handleDelete: (id: string, entityName?: string) => void;
  handleConfirmDelete: (reason: string) => Promise<void>;
  isDeleting: boolean;
  entityToDelete: { id: string; name?: string } | null;
}

export function useCrudDelete({
  onDelete,
  entityType = 'Entity',
}: UseCrudDeleteOptions): UseCrudDeleteReturn {
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [entityToDelete, setEntityToDelete] = useState<{
    id: string;
    name?: string;
  } | null>(null);

  const handleDelete = (id: string, entityName?: string) => {
    setEntityToDelete({ id, name: entityName });
    setDeleteDialogOpen(true);
  };

  const handleConfirmDelete = async (reason: string) => {
    if (!entityToDelete) {
      throw new Error('No entity selected for deletion');
    }

    setIsDeleting(true);
    try {
      await onDelete(entityToDelete.id, reason);
      setEntityToDelete(null);
      setDeleteDialogOpen(false);
    } catch (error) {
      throw error;
    } finally {
      setIsDeleting(false);
    }
  };

  return {
    deleteDialogOpen,
    setDeleteDialogOpen,
    handleDelete,
    handleConfirmDelete,
    isDeleting,
    entityToDelete,
  };
}

