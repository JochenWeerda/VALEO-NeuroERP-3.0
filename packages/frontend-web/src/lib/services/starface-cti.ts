/**
 * Starface TAPI/CTI Integration
 * Computer Telephony Integration für Click-to-Call aus Kundenstamm
 */

export type CallDirection = 'inbound' | 'outbound'
export type CallState = 'ringing' | 'connected' | 'held' | 'disconnected'

export interface StarfaceCall {
  callId: string
  direction: CallDirection
  state: CallState
  phoneNumber: string
  contactName?: string
  customerId?: string
  startTime: string
  duration?: number
}

export interface StarfaceConfig {
  serverUrl: string
  apiKey: string
  extension: string // Nebenstelle
  enabled: boolean
}

class StarfaceCTIService {
  private config: StarfaceConfig
  private ws: WebSocket | null = null
  private reconnectTimeout = 5000
  private eventCallbacks: Map<string, ((data: unknown) => void)[]> = new Map()

  constructor(config: StarfaceConfig) {
    this.config = config
    if (config.enabled) {
      this.connect()
    }
  }

  /**
   * WebSocket-Verbindung zur Starface CTI-API
   */
  private connect(): void {
    try {
      this.ws = new WebSocket(`${this.config.serverUrl}/ws/cti`)

      this.ws.onopen = () => {
        console.log('✅ Starface CTI verbunden')
        this.authenticate()
      }

      this.ws.onmessage = (event) => {
        const data = JSON.parse(event.data)
        this.handleEvent(data)
      }

      this.ws.onerror = (error) => {
        console.error('❌ Starface CTI Fehler:', error)
      }

      this.ws.onclose = () => {
        console.log('🔌 Starface CTI getrennt - Reconnect in', this.reconnectTimeout, 'ms')
        setTimeout(() => this.connect(), this.reconnectTimeout)
      }
    } catch (error) {
      console.error('Starface CTI Verbindung fehlgeschlagen:', error)
    }
  }

  /**
   * Authentifizierung mit API-Key
   */
  private authenticate(): void {
    this.send({
      action: 'authenticate',
      apiKey: this.config.apiKey,
      extension: this.config.extension,
    })
  }

  /**
   * Nachricht an Starface senden
   */
  private send(data: unknown): void {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(data))
    }
  }

  /**
   * Event-Handler
   */
  private handleEvent(data: { event: string; payload: unknown }): void {
    const callbacks = this.eventCallbacks.get(data.event) ?? []
    callbacks.forEach((cb) => cb(data.payload))
  }

  /**
   * Event-Listener registrieren
   */
  on(event: string, callback: (data: unknown) => void): void {
    const callbacks = this.eventCallbacks.get(event) ?? []
    callbacks.push(callback)
    this.eventCallbacks.set(event, callbacks)
  }

  /**
   * Click-to-Call (aus Kundenstamm/CRM)
   */
  async makeCall(phoneNumber: string, customerId?: string, customerName?: string): Promise<void> {
    this.send({
      action: 'makeCall',
      phoneNumber: this.normalizePhoneNumber(phoneNumber),
      customerId,
      customerName,
    })

    console.log('📞 Anruf gestartet:', phoneNumber, customerName)
  }

  /**
   * Anruf entgegennehmen
   */
  async answerCall(callId: string): Promise<void> {
    this.send({
      action: 'answerCall',
      callId,
    })
  }

  /**
   * Anruf beenden
   */
  async hangupCall(callId: string): Promise<void> {
    this.send({
      action: 'hangupCall',
      callId,
    })
  }

  /**
   * Anruf weiterleiten
   */
  async transferCall(callId: string, extension: string): Promise<void> {
    this.send({
      action: 'transferCall',
      callId,
      extension,
    })
  }

  /**
   * Anruf halten
   */
  async holdCall(callId: string): Promise<void> {
    this.send({
      action: 'holdCall',
      callId,
    })
  }

  /**
   * Telefonnummer normalisieren (E.164)
   */
  private normalizePhoneNumber(phone: string): string {
    // Entferne alle Nicht-Ziffern außer +
    let normalized = phone.replace(/[^\d+]/g, '')
    
    // Deutsche Vorwahl ergänzen falls fehlt
    if (!normalized.startsWith('+') && !normalized.startsWith('00')) {
      normalized = `+49${  normalized.replace(/^0/, '')}`
    }
    
    return normalized
  }

  /**
   * Verbindung trennen
   */
  disconnect(): void {
    this.ws?.close()
    this.ws = null
  }
}

// Singleton-Instanz
const starfaceConfig: StarfaceConfig = {
  serverUrl: import.meta.env.VITE_STARFACE_SERVER_URL || 'ws://localhost:8080',
  apiKey: import.meta.env.VITE_STARFACE_API_KEY || '',
  extension: import.meta.env.VITE_STARFACE_EXTENSION || '100',
  enabled: import.meta.env.VITE_STARFACE_ENABLED === 'true',
}

export const starfaceCTI = new StarfaceCTIService(starfaceConfig)

/**
 * React Hook für Starface CTI
 */
import { useEffect, useState } from 'react'

export function useStarfaceCTI() {
  const [activeCall, setActiveCall] = useState<StarfaceCall | null>(null)
  const [isConnected, setIsConnected] = useState(false)

  useEffect(() => {
    starfaceCTI.on('connected', () => setIsConnected(true))
    starfaceCTI.on('disconnected', () => setIsConnected(false))
    
    starfaceCTI.on('incomingCall', (data) => {
      setActiveCall(data as StarfaceCall)
    })
    
    starfaceCTI.on('callConnected', (data) => {
      setActiveCall(data as StarfaceCall)
    })
    
    starfaceCTI.on('callDisconnected', () => {
      setActiveCall(null)
    })
  }, [])

  return {
    isConnected,
    activeCall,
    makeCall: (phone: string, customerId?: string, customerName?: string) =>
      starfaceCTI.makeCall(phone, customerId, customerName),
    answerCall: (callId: string) => starfaceCTI.answerCall(callId),
    hangupCall: (callId: string) => starfaceCTI.hangupCall(callId),
    transferCall: (callId: string, extension: string) => starfaceCTI.transferCall(callId, extension),
    holdCall: (callId: string) => starfaceCTI.holdCall(callId),
  }
}
