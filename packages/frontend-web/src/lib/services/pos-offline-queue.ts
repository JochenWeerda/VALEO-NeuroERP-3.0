/**
 * POS Offline-Queue — IndexedDB-basierter Transaktionspuffer
 * ──────────────────────────────────────────────────────────
 * Speichert fehlgeschlagene Checkout-Transaktionen lokal und
 * synchronisiert sie automatisch wenn die Verbindung wiederhergestellt wird.
 */

import { useState, useEffect, useCallback } from 'react'

const DB_NAME = 'valeo-pos-offline'
const DB_VERSION = 1
const STORE = 'pending_transactions'

export type PendingTransaction = {
  id: string           // lokale UUID
  timestamp: string    // ISO
  cart: Array<{
    artikelnr: string
    bezeichnung: string
    ean: string
    preis: number
    menge: number
    rabatt_pct?: number
  }>
  zahlungen: Array<{
    art: string
    betrag: number
    referenz?: string
  }>
  gesamt: number
  kassierer: string
  tse_attempted: boolean
  retry_count: number
}

export type SyncResult = {
  synced: number
  failed: number
  remaining: number
}

// ── IndexedDB-Helfer ──────────────────────────────────────────────────────────

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, DB_VERSION)
    req.onupgradeneeded = (e) => {
      const db = (e.target as IDBOpenDBRequest).result
      if (!db.objectStoreNames.contains(STORE)) {
        const store = db.createObjectStore(STORE, { keyPath: 'id' })
        store.createIndex('timestamp', 'timestamp', { unique: false })
      }
    }
    req.onsuccess = (e) => resolve((e.target as IDBOpenDBRequest).result)
    req.onerror = () => reject(req.error)
  })
}

async function dbGetAll(): Promise<PendingTransaction[]> {
  const db = await openDb()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readonly')
    const req = tx.objectStore(STORE).getAll()
    req.onsuccess = () => resolve(req.result as PendingTransaction[])
    req.onerror = () => reject(req.error)
  })
}

async function dbPut(item: PendingTransaction): Promise<void> {
  const db = await openDb()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite')
    const req = tx.objectStore(STORE).put(item)
    req.onsuccess = () => resolve()
    req.onerror = () => reject(req.error)
  })
}

async function dbDelete(id: string): Promise<void> {
  const db = await openDb()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite')
    const req = tx.objectStore(STORE).delete(id)
    req.onsuccess = () => resolve()
    req.onerror = () => reject(req.error)
  })
}

async function dbCount(): Promise<number> {
  const db = await openDb()
  return new Promise((resolve, reject) => {
    const tx = db.transaction(STORE, 'readonly')
    const req = tx.objectStore(STORE).count()
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error)
  })
}

// ── Queue-Service ─────────────────────────────────────────────────────────────

let _pendingCount = 0
const _listeners = new Set<() => void>()

function notifyListeners(): void {
  _listeners.forEach((fn) => fn())
}

export const posOfflineQueue = {
  /** Transaktion in die Queue einreihen */
  async enqueue(tx: Omit<PendingTransaction, 'retry_count'>): Promise<void> {
    const item: PendingTransaction = { ...tx, retry_count: 0 }
    await dbPut(item)
    _pendingCount = await dbCount()
    notifyListeners()
  },

  /** Alle ausstehenden Transaktionen laden */
  async getAll(): Promise<PendingTransaction[]> {
    return dbGetAll()
  },

  /** Transaktion als erfolgreich markieren und entfernen */
  async remove(id: string): Promise<void> {
    await dbDelete(id)
    _pendingCount = await dbCount()
    notifyListeners()
  },

  /** Alle ausstehenden Transaktionen gegen API synchronisieren */
  async sync(
    apiCall: (tx: PendingTransaction) => Promise<void>,
  ): Promise<SyncResult> {
    const all = await dbGetAll()
    let synced = 0
    let failed = 0

    for (const tx of all) {
      try {
        await apiCall(tx)
        await dbDelete(tx.id)
        synced++
      } catch {
        const updated = { ...tx, retry_count: tx.retry_count + 1 }
        await dbPut(updated)
        failed++
      }
    }

    _pendingCount = await dbCount()
    notifyListeners()
    return { synced, failed, remaining: _pendingCount }
  },

  get pendingCount(): number {
    return _pendingCount
  },

  /** Initialisierung: Zähler aus DB laden */
  async init(): Promise<void> {
    _pendingCount = await dbCount()
    notifyListeners()
  },
}

// ── React-Hook ────────────────────────────────────────────────────────────────

export function usePosOfflineQueue() {
  const [pendingCount, setPendingCount] = useState(_pendingCount)
  const [isSyncing, setIsSyncing] = useState(false)

  useEffect(() => {
    // Init
    void posOfflineQueue.init()

    const update = () => setPendingCount(posOfflineQueue.pendingCount)
    _listeners.add(update)

    // Online-Event: automatisch synchronisieren
    const onOnline = () => { void handleSync() }
    window.addEventListener('online', onOnline)

    return () => {
      _listeners.delete(update)
      window.removeEventListener('online', onOnline)
    }
  }, [])

  const handleSync = useCallback(async () => {
    if (isSyncing || !navigator.onLine) return
    setIsSyncing(true)
    try {
      // Dynamisch importieren um circular dependency zu vermeiden
      const { apiClient } = await import('@/lib/api-client')
      await posOfflineQueue.sync(async (tx) => {
        await apiClient.post('/api/v1/pos/checkout', {
          cart: tx.cart,
          zahlungen: tx.zahlungen,
          gesamt: tx.gesamt,
          kassierer: tx.kassierer,
          offline_id: tx.id,
          timestamp: tx.timestamp,
        })
      })
    } finally {
      setIsSyncing(false)
    }
  }, [isSyncing])

  return { pendingCount, isSyncing, sync: handleSync }
}
