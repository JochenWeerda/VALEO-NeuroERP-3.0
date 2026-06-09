/**
 * Provider-neutral POS fiscalization client.
 *
 * The historic export name remains for source compatibility. Provider secrets
 * never reach the browser; fiskaly and Swissbit are selected on the backend.
 */
import { useEffect, useMemo, useState } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { apiClient } from '@/lib/api-client'

export type TSEState = 'UNINITIALIZED' | 'INITIALIZED' | 'DISABLED'
export type TransactionState = 'ACTIVE' | 'FINISHED' | 'CANCELLED'
export type PaymentType = 'CASH' | 'NON_CASH' | 'INTERNAL'

export interface TSESignature {
  value: string
  counter: number
  algorithm: string
}

export interface TSETransaction {
  txId: string
  number: number
  time_start: number
  time_end?: number
  signature?: TSESignature
  qr_code_data?: string
  state: TransactionState
  provider?: string
  simulated?: boolean
}

type CartLine = { bezeichnung: string; preis: number; menge: number; vatRate?: number }
export type FiscalProviderName = 'fiskaly' | 'swissbit_cloud' | 'swissbit_gateway' | 'simulation'
export type FiscalConfig = {
  configured: boolean
  provider: FiscalProviderName
  dsfinvk_provider: 'fiskaly' | 'simulation'
  cash_register_id?: string
  client_id?: string
  simulation_allowed: boolean
  settings?: { terminal_id?: string }
}
type FiscalResult = {
  provider: string
  transaction_id: string
  state: TransactionState
  signature?: string
  signature_counter?: number
  qr_code_data?: string
  started_at?: string
  finished_at?: string
  simulated?: boolean
}
export type FiscalProviderReadiness = {
  provider: FiscalProviderName
  ready: boolean
  live: boolean
  blockers: string[]
  capabilities: string[]
  details: Record<string, unknown>
}
export type FiscalProductReadiness = {
  product: 'submit_de' | 'receipt' | 'safe'
  label: string
  ready: boolean
  blockers: string[]
  details: {
    contract_version?: string | null
    documentation_url?: string
    execution_enabled?: boolean
    execution_note?: string
  }
}
export type FiscalReadiness = {
  configured: boolean
  ready: boolean
  config_blockers: string[]
  sign: FiscalProviderReadiness
  dsfinvk: FiscalProviderReadiness
  products: FiscalProductReadiness[]
}

const drafts = new Map<string, CartLine[]>()

export async function getFiscalConfig(): Promise<FiscalConfig> {
  return (await apiClient.get<FiscalConfig>('/api/v1/pos/fiscalization/config')).data
}

export async function saveFiscalConfig(config: Omit<FiscalConfig, 'configured'>): Promise<FiscalConfig> {
  return (await apiClient.put<FiscalConfig>('/api/v1/pos/fiscalization/config', config)).data
}

export async function getFiscalReadiness(): Promise<FiscalReadiness> {
  return (await apiClient.get<FiscalReadiness>('/api/v1/pos/fiscalization/readiness')).data
}

function toTransaction(result: FiscalResult): TSETransaction {
  const counter = result.signature_counter ?? 0
  return {
    txId: result.transaction_id,
    number: counter,
    time_start: result.started_at ? Math.floor(new Date(result.started_at).getTime() / 1000) : Math.floor(Date.now() / 1000),
    time_end: result.finished_at ? Math.floor(new Date(result.finished_at).getTime() / 1000) : undefined,
    signature: result.signature
      ? { value: result.signature, counter, algorithm: 'provider-managed' }
      : undefined,
    qr_code_data: result.qr_code_data,
    state: result.state,
    provider: result.provider,
    simulated: result.simulated,
  }
}

export function useFiskalyTSE() {
  const [readiness, setReadiness] = useState<FiscalReadiness | null>(null)

  useEffect(() => {
    let active = true
    const check = async () => {
      try {
        const response = await apiClient.get<FiscalReadiness>('/api/v1/pos/fiscalization/readiness')
        if (active) setReadiness(response.data)
      } catch {
        if (active) setReadiness(null)
      }
    }
    void check()
    const interval = window.setInterval(check, 60_000)
    return () => {
      active = false
      window.clearInterval(interval)
    }
  }, [])

  return useMemo(() => ({
    tssStatus: readiness?.sign.ready ? 'INITIALIZED' as const : 'UNINITIALIZED' as const,
    isInitialized: Boolean(readiness?.ready && readiness.sign.live),
    readiness,
    startTransaction: async (_processData: string, _processType = 'Kassenbeleg-V1'): Promise<TSETransaction> => {
      const config = await getFiscalConfig()
      if (!config.configured || !config.cash_register_id || !config.client_id) {
        throw new Error('Fiskalisierungsprovider ist nicht konfiguriert')
      }
      const txId = uuidv4()
      drafts.set(txId, [])
      const response = await apiClient.post<FiscalResult>('/api/v1/pos/fiscalization/transactions/start', {
        terminal_id: config.settings?.terminal_id ?? config.client_id,
        cash_register_id: config.cash_register_id,
        client_id: config.client_id,
        transaction_id: txId,
        transaction_type: 'RECEIPT',
        lines: [],
        payments: [],
      })
      return toTransaction(response.data)
    },
    updateTransaction: async (txId: string, cart: CartLine[]): Promise<void> => {
      drafts.set(txId, cart)
    },
    finishTransaction: async (
      txId: string,
      paymentType: PaymentType,
      amount: number,
      paymentLines?: Array<{ method: string; amount: number }>,
    ): Promise<TSETransaction> => {
      const config = await getFiscalConfig()
      if (!config.cash_register_id || !config.client_id) {
        throw new Error('Fiskalisierungsprovider ist nicht konfiguriert')
      }
      const cart = drafts.get(txId) ?? []
      const response = await apiClient.post<FiscalResult>('/api/v1/pos/fiscalization/transactions/finish', {
        terminal_id: config.settings?.terminal_id ?? config.client_id,
        cash_register_id: config.cash_register_id,
        client_id: config.client_id,
        transaction_id: txId,
        transaction_type: 'RECEIPT',
        lines: cart.map((line) => ({
          text: line.bezeichnung,
          quantity: line.menge,
          gross_amount: line.preis * line.menge,
          vat_rate: line.vatRate ?? 19,
        })),
        payments: paymentLines?.length ? paymentLines : [{ method: paymentType, amount }],
      })
      drafts.delete(txId)
      return toTransaction(response.data)
    },
    cancelTransaction: async (): Promise<void> => {
      throw new Error('Abbruch muss als signierter Storno-/Abbruchvorgang umgesetzt werden')
    },
    exportDSFinVK: async (): Promise<never> => {
      throw new Error('DSFinV-K-Export erfolgt getrennt ueber /pos/fiscalization/exports')
    },
  }), [readiness])
}
