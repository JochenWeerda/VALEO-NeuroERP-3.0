import { useCallback, useEffect, useState } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useToast } from '@/hooks/use-toast'

interface OfflineQueueItem {
  id: string
  type: 'create' | 'update' | 'delete'
  entity: string
  data: any
  timestamp: number
  retryCount: number
}

interface UseOfflineSyncOptions {
  enabled?: boolean
  maxRetries?: number
  syncInterval?: number
}

export function useOfflineSync(options: UseOfflineSyncOptions = {}) {
  const {
    enabled = true,
    maxRetries = 3,
    syncInterval = 30000 // 30 seconds
  } = options

  const [isOnline, setIsOnline] = useState(navigator.onLine)
  const [isSyncing, setIsSyncing] = useState(false)
  const [queue, setQueue] = useState<OfflineQueueItem[]>([])
  const [lastSyncTime, setLastSyncTime] = useState<number | null>(null)

  const queryClient = useQueryClient()
  const { toast } = useToast()

  // Load queue from localStorage on mount
  useEffect(() => {
    const savedQueue = localStorage.getItem('offline-queue')
    if (savedQueue) {
      try {
        setQueue(JSON.parse(savedQueue))
      } catch (error) {
        console.error('Failed to load offline queue:', error)
      }
    }
  }, [])

  // Save queue to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('offline-queue', JSON.stringify(queue))
  }, [queue])

  // Monitor online/offline status
  useEffect(() => {
    const handleOnline = () => {
      setIsOnline(true)
      toast({
        title: 'Online',
        description: 'Verbindung wiederhergestellt. Synchronisiere Daten...',
      })
      syncQueue()
    }

    const handleOffline = () => {
      setIsOnline(false)
      toast({
        title: 'Offline',
        description: 'Arbeite im Offline-Modus. Änderungen werden gespeichert.',
        variant: 'destructive',
      })
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [])

  // Auto-sync when online
  useEffect(() => {
    if (!enabled || !isOnline || queue.length === 0) return

    const interval = setInterval(() => {
      syncQueue()
    }, syncInterval)

    return () => clearInterval(interval)
  }, [enabled, isOnline, queue.length, syncInterval])

  const addToQueue = useCallback((item: Omit<OfflineQueueItem, 'id' | 'timestamp' | 'retryCount'>) => {
    const queueItem: OfflineQueueItem = {
      ...item,
      id: crypto.randomUUID(),
      timestamp: Date.now(),
      retryCount: 0,
    }

    setQueue(prev => [...prev, queueItem])

    if (!isOnline) {
      toast({
        title: 'Offline gespeichert',
        description: 'Die Änderung wird synchronisiert, sobald die Verbindung wiederhergestellt ist.',
      })
    }

    return queueItem.id
  }, [isOnline, toast])

  const removeFromQueue = useCallback((id: string) => {
    setQueue(prev => prev.filter(item => item.id !== id))
  }, [])

  const syncQueue = useCallback(async () => {
    if (!isOnline || isSyncing || queue.length === 0) return

    setIsSyncing(true)

    try {
      const itemsToSync = [...queue]

      for (const item of itemsToSync) {
        try {
          await syncItem(item)
          removeFromQueue(item.id)
        } catch (error) {
          console.error(`Failed to sync item ${item.id}:`, error)

          // Increment retry count
          setQueue(prev => prev.map(q =>
            q.id === item.id
              ? { ...q, retryCount: q.retryCount + 1 }
              : q
          ))

          // Remove if max retries exceeded
          if (item.retryCount >= maxRetries) {
            removeFromQueue(item.id)
            toast({
              title: 'Synchronisation fehlgeschlagen',
              description: `Konnte ${item.type} ${item.entity} nicht synchronisieren.`,
              variant: 'destructive',
            })
          }
        }
      }

      if (itemsToSync.length > 0) {
        setLastSyncTime(Date.now())
        queryClient.invalidateQueries() // Refresh all data

        toast({
          title: 'Synchronisation abgeschlossen',
          description: `${itemsToSync.length} Änderungen erfolgreich synchronisiert.`,
        })
      }
    } finally {
      setIsSyncing(false)
    }
  }, [isOnline, isSyncing, queue, maxRetries, removeFromQueue, toast, queryClient])

  const syncItem = async (item: OfflineQueueItem) => {
    // This would be implemented based on the specific API endpoints
    // For now, it's a placeholder that simulates API calls
    switch (item.entity) {
      case 'customer':
        // await crmService.createCustomer(item.data)
        break
      case 'lead':
        // await crmService.createLead(item.data)
        break
      case 'task':
        // await taskService.createTask(item.data)
        break
      default:
        throw new Error(`Unknown entity type: ${item.entity}`)
    }

    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 500))
  }

  const clearQueue = useCallback(() => {
    setQueue([])
    localStorage.removeItem('offline-queue')
  }, [])

  return {
    isOnline,
    isSyncing,
    queue,
    lastSyncTime,
    addToQueue,
    syncQueue,
    clearQueue,
    queueLength: queue.length,
  }
}

// Hook for offline-aware mutations
export function useOfflineMutation() {
  const { isOnline, addToQueue } = useOfflineSync()

  const mutateAsync = useCallback(async (mutation: () => Promise<any>, offlineData: any) => {
    if (isOnline) {
      return await mutation()
    } else {
      // Store for later sync
      addToQueue({
        type: 'create',
        entity: offlineData.entity,
        data: offlineData,
      })
      return { id: crypto.randomUUID(), ...offlineData }
    }
  }, [isOnline, addToQueue])

  return { mutateAsync, isOnline }
}