/**
 * Generic API Hook für alle verbleibenden Seiten mit Mock-Daten
 * Bietet einheitliche Schnittstelle für CRUD-Operationen
 */

import { useState, useEffect, useCallback } from 'react';

// Generic API Client Integration
const useGenericApi = <T>(
  endpoint: string,
  options: {
    mockData?: T[];
    enabled?: boolean;
    autoRefresh?: boolean;
    refreshInterval?: number;
  } = {}
) => {
  const {
    mockData = [],
    enabled = true,
    autoRefresh = false,
    refreshInterval = 30000, // 30 Sekunden
  } = options;

  const [data, setData] = useState<T[]>(mockData);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastUpdated, setLastUpdated] = useState<Date | null>(null);

  // Fetch Funktion
  const fetchData = useCallback(async () => {
    if (!enabled) return;

    setLoading(true);
    setError(null);

    try {
      // Versuche echte API
      const response = await fetch(endpoint);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();

      // Handle verschiedene Response-Formate
      const items = result.items || result.data || (Array.isArray(result) ? result : [result]);

      setData(items);
      setLastUpdated(new Date());
    } catch (err) {
      // Fallback auf Mock-Daten
      console.warn(`API fetch failed for ${endpoint}, using mock data`);
      setError(err instanceof Error ? err.message : 'Unknown error');

      // Mock-Daten nur verwenden wenn vorhanden
      if (mockData.length > 0) {
        setData(mockData);
      }
    } finally {
      setLoading(false);
    }
  }, [endpoint, enabled, mockData]);

  // Initial Load + Auto-Refresh
  useEffect(() => {
    if (enabled) {
      fetchData();

      if (autoRefresh) {
        const interval = setInterval(fetchData, refreshInterval);
        return () => clearInterval(interval);
      }
    }
  }, [fetchData, enabled, autoRefresh, refreshInterval]);

  // CRUD Operations
  const create = async (item: Partial<T>): Promise<T | null> => {
    setLoading(true);
    try {
      const response = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(item),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const created = await response.json();
      setData(prev => [...prev, created]);
      return created;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Create failed');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const update = async (id: string, updates: Partial<T>): Promise<T | null> => {
    setLoading(true);
    try {
      const response = await fetch(`${endpoint}/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(updates),
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      const updated = await response.json();
      setData(prev => prev.map(item => (item as any).id === id ? updated : item));
      return updated;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Update failed');
      return null;
    } finally {
      setLoading(false);
    }
  };

  const remove = async (id: string): Promise<boolean> => {
    setLoading(true);
    try {
      const response = await fetch(`${endpoint}/${id}`, {
        method: 'DELETE',
      });

      if (!response.ok) throw new Error(`HTTP ${response.status}`);

      setData(prev => prev.filter(item => (item as any).id !== id));
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
      return false;
    } finally {
      setLoading(false);
    }
  };

  return {
    data,
    loading,
    error,
    lastUpdated,
    refetch: fetchData,
    create,
    update,
    remove,
    isEmpty: data.length === 0,
    count: data.length,
  };
};

// Convenience Hooks für häufige Use-Cases
export const useListPage = <T>(
  endpoint: string,
  mockData: T[] = []
) => useGenericApi<T>(endpoint, { mockData, autoRefresh: true });

export const useDetailPage = <T>(
  endpoint: string,
  id: string,
  mockData?: T
) => {
  const { data, ...rest } = useGenericApi<T>(`${endpoint}/${id}`, {
    mockData: mockData ? [mockData] : [],
  });

  return {
    item: data[0] || null,
    ...rest,
  };
};

export const useSearchableList = <T>(
  endpoint: string,
  mockData: T[] = []
) => {
  const [search, setSearch] = useState('');
  const { data, loading, refetch } = useGenericApi<T>(endpoint, { mockData });

  const filtered = data.filter(item =>
    JSON.stringify(item).toLowerCase().includes(search.toLowerCase())
  );

  return {
    data: filtered,
    loading,
    search,
    setSearch,
    refetch,
  };
};

export default useGenericApi;
