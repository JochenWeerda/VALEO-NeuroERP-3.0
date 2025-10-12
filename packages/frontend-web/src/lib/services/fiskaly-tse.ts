/**
 * fiskaly Cloud-TSE Integration
 * KassenSichV-zertifizierte Technische Sicherheitseinrichtung
 * Basiert auf: https://github.com/fiskaly/fiskaly-sdk-java
 */

import axios, { type AxiosInstance } from 'axios'
import { v4 as uuidv4 } from 'uuid'

export type TSEState = 'UNINITIALIZED' | 'INITIALIZED' | 'DISABLED'
export type TransactionState = 'ACTIVE' | 'FINISHED' | 'CANCELLED'
export type PaymentType = 'CASH' | 'NON_CASH' | 'INTERNAL'

export interface FiskalyConfig {
  apiKey: string
  apiSecret: string
  tssId: string
  clientId: string
  baseUrl?: string
  enabled: boolean
}

export interface TSESignature {
  value: string           // ECDSA-Signatur (Base64)
  counter: number         // Fortlaufender Signaturzähler
  algorithm: string       // ecdsa-plain-SHA256
}

export interface TSETransaction {
  txId: string
  number: number
  time_start: number
  time_end?: number
  signature?: TSESignature
  qr_code_data?: string
  state: TransactionState
}

export class FiskalyTSE {
  private client: AxiosInstance
  private apiKey: string
  private apiSecret: string
  private tssId: string
  private clientId: string
  private accessToken: string | null = null
  private enabled: boolean

  constructor(config: FiskalyConfig) {
    this.apiKey = config.apiKey
    this.apiSecret = config.apiSecret
    this.tssId = config.tssId
    this.clientId = config.clientId
    this.enabled = config.enabled

    this.client = axios.create({
      baseURL: config.baseUrl ?? 'https://kassensichv.io/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    })

    // Request Interceptor (Auto-Token-Injection)
    this.client.interceptors.request.use(
      async (config) => {
        if (!this.accessToken) {
          await this.authenticate()
        }
        config.headers.Authorization = `Bearer ${this.accessToken}`
        return config
      },
      (error) => Promise.reject(error),
    )

    // Response Interceptor (Auto-Refresh bei 401)
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401 && error.config && !error.config._retry) {
          error.config._retry = true
          await this.authenticate()
          return this.client.request(error.config)
        }
        return Promise.reject(error)
      },
    )
  }

  /**
   * Authentifizierung mit API-Key/Secret
   * Liefert JWT-Token mit 24h Gültigkeit
   */
  private async authenticate(): Promise<void> {
    if (!this.enabled) {
      console.warn('⚠️ fiskaly TSE disabled - using mock')
      return
    }

    try {
      const response = await axios.post('https://kassensichv.io/api/v1/auth', {
        api_key: this.apiKey,
        api_secret: this.apiSecret,
      })
      
      this.accessToken = response.data.access_token
      console.log('✅ fiskaly TSE authenticated')
    } catch (error) {
      console.error('❌ fiskaly TSE auth failed:', error)
      throw error
    }
  }

  /**
   * TSS initialisieren (einmalig beim Setup)
   */
  async initializeTSS(): Promise<void> {
    if (!this.enabled) return

    await this.client.put(`/tss/${this.tssId}`, {
      state: 'INITIALIZED',
      description: 'VALERO POS-Terminal Haus & Gartenmarkt',
    })
  }

  /**
   * Client registrieren (einmalig pro Kasse)
   */
  async registerClient(): Promise<void> {
    if (!this.enabled) return

    await this.client.put(`/tss/${this.tssId}/client/${this.clientId}`, {
      serial_number: this.clientId,
    })
    
    console.log(`✅ TSE Client ${this.clientId} registriert`)
  }

  /**
   * Transaction starten (beim Warenkorb-Start)
   */
  async startTransaction(_processData: string, _processType = 'Kassenbeleg-V1'): Promise<TSETransaction> {
    if (!this.enabled) {
      // Mock für Development
      return {
        txId: uuidv4(),
        number: Math.floor(Math.random() * 10000),
        time_start: Math.floor(Date.now() / 1000),
        state: 'ACTIVE',
      }
    }

    const txId = uuidv4()
    
    const response = await this.client.put(`/tss/${this.tssId}/tx/${txId}`, {
      state: 'ACTIVE',
      client_id: this.clientId,
    })
    
    return {
      txId,
      number: response.data.number,
      time_start: response.data.time_start,
      state: 'ACTIVE',
    }
  }

  /**
   * Transaction aktualisieren (Artikel hinzufügen/ändern)
   */
  async updateTransaction(
    txId: string,
    cart: Array<{ bezeichnung: string; preis: number; menge: number }>,
  ): Promise<void> {
    if (!this.enabled) return

    const total = cart.reduce((sum, item) => sum + item.preis * item.menge, 0)
    const netto = total / 1.19 // Annahme: 19% MwSt
    
    await this.client.put(`/tss/${this.tssId}/tx/${txId}`, {
      state: 'ACTIVE',
      client_id: this.clientId,
      schema: {
        standard_v1: {
          receipt: {
            receipt_type: 'RECEIPT',
            amounts_per_vat_rate: [
              { vat_rate: 19, amount: netto.toFixed(2) },
            ],
          },
        },
      },
    })
  }

  /**
   * Transaction beenden & signieren (bei Zahlung)
   */
  async finishTransaction(
    txId: string,
    paymentType: PaymentType,
    amount: number,
  ): Promise<TSETransaction> {
    if (!this.enabled) {
      // Mock für Development
      return {
        txId,
        number: Math.floor(Math.random() * 10000),
        time_start: Math.floor(Date.now() / 1000),
        time_end: Math.floor(Date.now() / 1000) + 30,
        state: 'FINISHED',
        signature: {
          value: `MOCK_SIG_${  Date.now()}`,
          counter: Math.floor(Math.random() * 1000),
          algorithm: 'ecdsa-plain-SHA256',
        },
        qr_code_data: `V0;VALERO-POS;Kassenbeleg-V1;Beleg^0.00_0.00_0.00_0.00_${amount.toFixed(2)}^${amount.toFixed(2)}:Bar;${Math.floor(Math.random() * 10000)};${Math.floor(Math.random() * 1000)};${Math.floor(Date.now() / 1000)};${Math.floor(Date.now() / 1000) + 30};ecdsa-plain-SHA256;unixTime;MOCK_SIG;MOCK_PUB;TSS-MOCK`,
      }
    }

    const response = await this.client.put(`/tss/${this.tssId}/tx/${txId}`, {
      state: 'FINISHED',
      client_id: this.clientId,
      schema: {
        standard_v1: {
          receipt: {
            receipt_type: 'RECEIPT',
            amounts_per_payment_type: [
              {
                payment_type: paymentType,
                amount: amount.toFixed(2),
              },
            ],
          },
        },
      },
    })

    return {
      txId,
      number: response.data.number,
      time_start: response.data.time_start,
      time_end: response.data.time_end,
      state: 'FINISHED',
      signature: response.data.signature,
      qr_code_data: response.data.qr_code_data,
    }
  }

  /**
   * Transaction abbrechen (bei Storno)
   */
  async cancelTransaction(txId: string): Promise<void> {
    if (!this.enabled) return

    await this.client.put(`/tss/${this.tssId}/tx/${txId}`, {
      state: 'CANCELLED',
      client_id: this.clientId,
    })
  }

  /**
   * DSFinV-K Export (DATEV-Format)
   */
  async exportDSFinVK(startDate: string, endDate: string): Promise<Blob> {
    if (!this.enabled) {
      // Mock-Export
      const mockData = { message: 'Mock DSFinV-K Export' }
      return new Blob([JSON.stringify(mockData)], { type: 'application/json' })
    }

    const response = await this.client.get(`/tss/${this.tssId}/export`, {
      params: {
        start_date: startDate,
        end_date: endDate,
      },
      responseType: 'blob',
    })
    
    return response.data
  }

  /**
   * TSS-Status abrufen
   */
  async getTSSStatus(): Promise<{
    state: TSEState
    serial_number: string
    signature_counter: number
    transaction_counter: number
  }> {
    if (!this.enabled) {
      return {
        state: 'INITIALIZED',
        serial_number: 'MOCK-TSS-12345',
        signature_counter: 1234,
        transaction_counter: 567,
      }
    }

    const response = await this.client.get(`/tss/${this.tssId}`)
    return response.data
  }
}

// Singleton-Instanz
const fiskalyConfig: FiskalyConfig = {
  apiKey: import.meta.env.VITE_FISKALY_API_KEY || '',
  apiSecret: import.meta.env.VITE_FISKALY_API_SECRET || '',
  tssId: import.meta.env.VITE_FISKALY_TSS_ID || '',
  clientId: import.meta.env.VITE_FISKALY_CLIENT_ID || 'POS-001',
  baseUrl: import.meta.env.VITE_FISKALY_BASE_URL || 'https://kassensichv.io/api/v1',
  enabled: import.meta.env.VITE_FISKALY_ENABLED === 'true',
}

export const fiskalyTSE = new FiskalyTSE(fiskalyConfig)

/**
 * React Hook für fiskaly TSE
 */
import { useEffect, useState } from 'react'

export function useFiskalyTSE() {
  const [tssStatus, setTSSStatus] = useState<TSEState>('UNINITIALIZED')
  const [isInitialized, setIsInitialized] = useState(false)

  useEffect(() => {
    async function checkStatus() {
      try {
        const status = await fiskalyTSE.getTSSStatus()
        setTSSStatus(status.state)
        setIsInitialized(status.state === 'INITIALIZED')
      } catch (error) {
        console.error('TSE Status check failed:', error)
      }
    }

    checkStatus()
    const interval = setInterval(checkStatus, 60000) // Alle 60s prüfen

    return () => clearInterval(interval)
  }, [])

  return {
    tssStatus,
    isInitialized,
    startTransaction: (processData: string, processType?: string) =>
      fiskalyTSE.startTransaction(processData, processType),
    updateTransaction: (txId: string, cart: Array<{ bezeichnung: string; preis: number; menge: number }>) =>
      fiskalyTSE.updateTransaction(txId, cart),
    finishTransaction: (txId: string, paymentType: PaymentType, amount: number) =>
      fiskalyTSE.finishTransaction(txId, paymentType, amount),
    cancelTransaction: (txId: string) => fiskalyTSE.cancelTransaction(txId),
    exportDSFinVK: (startDate: string, endDate: string) => fiskalyTSE.exportDSFinVK(startDate, endDate),
  }
}
