/**
 * useCrudAuditTrail Hook
 * Hook for fetching and managing audit trail
 */

import { useState, useEffect } from 'react';
import { ChangeLog } from '../components/CrudAuditTrailPanel';

export interface UseCrudAuditTrailOptions {
  entityType: string;
  entityId: string | null;
  fetchAuditTrail: (entityType: string, entityId: string) => Promise<ChangeLog[]>;
  enabled?: boolean;
}

export interface UseCrudAuditTrailReturn {
  changeLogs: ChangeLog[];
  isLoading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

export function useCrudAuditTrail({
  entityType,
  entityId,
  fetchAuditTrail,
  enabled = true,
}: UseCrudAuditTrailOptions): UseCrudAuditTrailReturn {
  const [changeLogs, setChangeLogs] = useState<ChangeLog[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const loadAuditTrail = async () => {
    if (!entityId || !enabled) {
      setChangeLogs([]);
      return;
    }

    setIsLoading(true);
    setError(null);
    try {
      const logs = await fetchAuditTrail(entityType, entityId);
      setChangeLogs(logs);
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load audit trail'));
      setChangeLogs([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadAuditTrail();
  }, [entityType, entityId, enabled]);

  return {
    changeLogs,
    isLoading,
    error,
    refetch: loadAuditTrail,
  };
}

