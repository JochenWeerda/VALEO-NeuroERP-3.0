/**
 * BonDruck-Service — ESC/POS Bondrucker-Integration
 * ──────────────────────────────────────────────────
 * Versucht in dieser Reihenfolge:
 *   1. WebUSB  (USB-Drucker direkt im Browser)
 *   2. WebSerial (serieller Drucker / COM-Port)
 *   3. window.print() (Browser-Druckdialog als Fallback)
 *
 * ESC/POS-Kompatibilität: Epson TM-Serie, Star mC-Print, Bixolon, etc.
 */

import { escapeHtml } from '@/lib/export-utils'

// ── Minimale WebUSB/WebSerial Type-Stubs (nicht im std lib.dom.d.ts enthalten) ──
type USBDevice = object
type SerialPort = object
type USB = { requestDevice(opts: { filters: { vendorId?: number }[] }): Promise<USBDevice> }
type Serial = { requestPort(opts: { filters: object[] }): Promise<SerialPort> }

// ── ESC/POS Konstanten ────────────────────────────────────────────────────────
const ESC = 0x1b
const GS  = 0x1d
const LF  = 0x0a
const CR  = 0x0d

const CMD = {
  INIT:           [ESC, 0x40],
  ALIGN_LEFT:     [ESC, 0x61, 0x00],
  ALIGN_CENTER:   [ESC, 0x61, 0x01],
  ALIGN_RIGHT:    [ESC, 0x61, 0x02],
  BOLD_ON:        [ESC, 0x45, 0x01],
  BOLD_OFF:       [ESC, 0x45, 0x00],
  DOUBLE_HEIGHT:  [ESC, 0x21, 0x10],
  NORMAL_SIZE:    [ESC, 0x21, 0x00],
  FONT_A:         [ESC, 0x4d, 0x00],
  CUT_FULL:       [GS,  0x56, 0x00],
  CUT_PARTIAL:    [GS,  0x56, 0x01],
  OPEN_DRAWER:    [ESC, 0x70, 0x00, 0x19, 0xfa],
  LINE_FEED:      [LF],
  BEEP:           [ESC, 0x42, 0x03, 0x01],
} as const

// ── Typen ─────────────────────────────────────────────────────────────────────

export type BonPosition = {
  bezeichnung: string
  menge: number
  einzelpreis: number
  gesamtpreis: number
  rabatt_pct?: number
}

export type BonZahlung = {
  art: 'bar' | 'ec' | 'paypal' | 'gift_card' | 'b2b'
  betrag: number
  wechselgeld?: number
  referenz?: string
}

export type MwstZeile = {
  satz: number   // z.B. 19
  netto: number
  mwst: number
  brutto: number
}

export type BonData = {
  bonNr: string
  datum: Date
  kassierer: string
  filiale?: string
  positionen: BonPosition[]
  zahlungen: BonZahlung[]
  gesamt: number
  mwst_zeilen: MwstZeile[]
  tseNr?: string
  tseSig?: string
  tseSerial?: string
  isRetoure?: boolean
  originalBonNr?: string
}

export type BonDruckMethod = 'usb' | 'serial' | 'browser' | 'none'

// ── Hilfsfunktionen ───────────────────────────────────────────────────────────

function encodeText(text: string): Uint8Array {
  // Latin-1 für Standard-ESC/POS-Drucker
  const bytes: number[] = []
  for (let i = 0; i < text.length; i++) {
    const code = text.charCodeAt(i)
    bytes.push(code < 256 ? code : 0x3f) // '?' für nicht-darstellbare Zeichen
  }
  return new Uint8Array(bytes)
}

function line(text: string): Uint8Array {
  return new Uint8Array([...encodeText(text), LF])
}

function pad(str: string, width: number, right = false): string {
  if (str.length >= width) return str.slice(0, width)
  const padding = ' '.repeat(width - str.length)
  return right ? padding + str : str + padding
}

function twoCol(left: string, right: string, width = 42): string {
  const maxLeft = width - right.length - 1
  return `${pad(left, maxLeft)} ${right}`
}

function separator(char = '-', width = 42): string {
  return char.repeat(width)
}

const ZAHLUNGSART: Record<BonZahlung['art'], string> = {
  bar: 'Bargeld',
  ec: 'EC-Karte',
  paypal: 'PayPal',
  gift_card: 'Geschenkkarte',
  b2b: 'B2B-Rechnung',
}

// ── Bon-Formatter ─────────────────────────────────────────────────────────────

function buildBonBytes(bon: BonData): Uint8Array {
  const chunks: Uint8Array[] = []

  const push = (...bytes: number[]) => chunks.push(new Uint8Array(bytes))
  const pushLine = (text: string) => chunks.push(line(text))
  const pushSep = (c = '-') => pushLine(separator(c))

  const fmt = (n: number) => `${n.toFixed(2).replace('.', ',')} EUR`
  const fmtDate = (d: Date) =>
    `${d.toLocaleDateString('de-DE')}  ${d.toLocaleTimeString('de-DE', { hour: '2-digit', minute: '2-digit' })}`

  // Init
  push(...CMD.INIT)
  push(...CMD.FONT_A)

  // Header
  push(...CMD.ALIGN_CENTER)
  push(...CMD.BOLD_ON)
  push(...CMD.DOUBLE_HEIGHT)
  pushLine(bon.isRetoure ? 'RETOURE' : 'KASSENBON')
  push(...CMD.NORMAL_SIZE)
  pushLine(bon.filiale ?? 'VALEO Landhandel')
  push(...CMD.BOLD_OFF)
  push(...CMD.ALIGN_LEFT)
  pushLine('')

  // Meta
  pushLine(twoCol('Bon-Nr:', bon.bonNr))
  pushLine(twoCol('Datum:', fmtDate(bon.datum)))
  pushLine(twoCol('Kassierer:', bon.kassierer))
  if (bon.isRetoure && bon.originalBonNr) {
    pushLine(twoCol('Ursprungs-Bon:', bon.originalBonNr))
  }
  pushSep()

  // Positionen
  for (const pos of bon.positionen) {
    const sign = bon.isRetoure ? '-' : ''
    if (pos.menge !== 1) {
      pushLine(`${pos.menge} x ${pos.bezeichnung}`)
      pushLine(twoCol(
        `  ${fmt(pos.einzelpreis)} x ${pos.menge}`,
        sign + fmt(pos.gesamtpreis),
      ))
    } else {
      pushLine(twoCol(pos.bezeichnung, sign + fmt(pos.gesamtpreis)))
    }
    if (pos.rabatt_pct && pos.rabatt_pct > 0) {
      pushLine(twoCol(`  Rabatt ${pos.rabatt_pct}%`, `-${fmt(pos.gesamtpreis * pos.rabatt_pct / 100)}`))
    }
  }
  pushSep()

  // Gesamt
  push(...CMD.BOLD_ON)
  const sign = bon.isRetoure ? '-' : ''
  pushLine(twoCol('GESAMT', sign + fmt(bon.gesamt)))
  push(...CMD.BOLD_OFF)
  pushLine('')

  // MwSt-Aufschlüsselung
  if (bon.mwst_zeilen.length > 0) {
    pushLine(twoCol('MwSt%', 'Netto   MwSt   Brutto'))
    for (const z of bon.mwst_zeilen) {
      pushLine(twoCol(
        `${z.satz}%`,
        `${fmt(z.netto)}  ${fmt(z.mwst)}  ${fmt(z.brutto)}`,
      ))
    }
    pushSep()
  }

  // Zahlungen
  for (const z of bon.zahlungen) {
    pushLine(twoCol(ZAHLUNGSART[z.art], fmt(z.betrag)))
    if (z.wechselgeld && z.wechselgeld > 0) {
      pushLine(twoCol('  Wechselgeld', fmt(z.wechselgeld)))
    }
    if (z.referenz) pushLine(`  Ref: ${z.referenz}`)
  }

  // TSE-Block
  if (bon.tseNr) {
    pushSep('=')
    pushLine('TSE-Daten (KassenSichV)')
    pushLine(`TSE-Nr:     ${bon.tseNr}`)
    if (bon.tseSerial) pushLine(`Seriennr:   ${bon.tseSerial.slice(0, 30)}`)
    if (bon.tseSig)    pushLine(`Signatur:   ${bon.tseSig.slice(0, 20)}...`)
    pushSep('=')
  }

  // Footer
  pushLine('')
  push(...CMD.ALIGN_CENTER)
  pushLine(bon.isRetoure ? 'Retoure erfolgreich' : 'Vielen Dank fuer Ihren Einkauf!')
  pushLine('www.valeo-erp.de')
  pushLine('')

  // Schnitt
  push(...CMD.LINE_FEED)
  push(...CMD.LINE_FEED)
  push(...CMD.LINE_FEED)
  push(...CMD.CUT_PARTIAL)

  // Alles zusammenfügen
  const total = chunks.reduce((s, c) => s + c.length, 0)
  const result = new Uint8Array(total)
  let offset = 0
  for (const chunk of chunks) {
    result.set(chunk, offset)
    offset += chunk.length
  }
  return result
}

// ── BonDruck-Service ──────────────────────────────────────────────────────────

export class BonDruckService {
  private _method: BonDruckMethod = 'none'
  private _usbDevice: USBDevice | null = null
  private _usbInterface = 0
  private _usbEndpoint = 1
  private _serialPort: SerialPort | null = null
  private _serialWriter: WritableStreamDefaultWriter<Uint8Array> | null = null

  get isConnected(): boolean {
    return this._method !== 'none' && this._method !== 'browser'
  }

  get method(): BonDruckMethod {
    return this._method
  }

  get label(): string {
    switch (this._method) {
      case 'usb':     return 'Drucker verbunden (USB)'
      case 'serial':  return 'Drucker verbunden (Seriell)'
      case 'browser': return 'Browser-Druck'
      default:        return 'Kein Drucker'
    }
  }

  /** Verbindung herstellen. Gibt true zurück wenn Hardware-Drucker gefunden. */
  async connect(): Promise<boolean> {
    // 1. WebUSB
    if ('usb' in navigator) {
      try {
        const device = await (navigator as Navigator & { usb: USB }).usb.requestDevice({
          filters: [
            { vendorId: 0x04b8 }, // Epson
            { vendorId: 0x0519 }, // Star Micronics
            { vendorId: 0x0dd4 }, // Bixolon
            { vendorId: 0x1fc9 }, // Citizen
          ],
        })
        await device.open()
        await device.selectConfiguration(1)
        const iface = device.configuration?.interfaces?.[0]
        if (iface) {
          await device.claimInterface(iface.interfaceNumber)
          const ep = iface.alternate.endpoints.find(
            (e: { direction?: string }) => e.direction === 'out',
          )
          if (ep) {
            this._usbInterface = iface.interfaceNumber
            this._usbEndpoint = ep.endpointNumber
            this._usbDevice = device
            this._method = 'usb'
            return true
          }
        }
        await device.close()
      } catch {
        // User cancelled or no device found
      }
    }

    // 2. WebSerial
    if ('serial' in navigator) {
      try {
        const port = await (navigator as Navigator & { serial: Serial }).serial.requestPort({
          filters: [],
        })
        await port.open({ baudRate: 9600 })
        this._serialWriter = port.writable?.getWriter() ?? null
        if (this._serialWriter) {
          this._serialPort = port
          this._method = 'serial'
          return true
        }
      } catch {
        // User cancelled or no port
      }
    }

    // 3. Fallback: Browser-Druck
    this._method = 'browser'
    return false
  }

  /** Kassenschublade öffnen */
  async openDrawer(): Promise<void> {
    const cmd = new Uint8Array([...CMD.INIT, ...CMD.OPEN_DRAWER])
    await this._send(cmd)
  }

  /** Bon drucken */
  async print(bon: BonData): Promise<void> {
    if (this._method === 'browser') {
      this._printBrowser(bon)
      return
    }
    if (this._method === 'none') {
      // Auto-fallback to browser
      this._method = 'browser'
      this._printBrowser(bon)
      return
    }
    const bytes = buildBonBytes(bon)
    await this._send(bytes)
  }

  private async _send(bytes: Uint8Array): Promise<void> {
    if (this._method === 'usb' && this._usbDevice) {
      await this._usbDevice.transferOut(this._usbEndpoint, bytes)
    } else if (this._method === 'serial' && this._serialWriter) {
      await this._serialWriter.write(bytes)
    }
  }

  private _printBrowser(bon: BonData): void {
    const fmt = (n: number) => new Intl.NumberFormat('de-DE', { style: 'currency', currency: 'EUR' }).format(n)
    const sign = bon.isRetoure ? '-' : ''

    const posHtml = bon.positionen.map((p) => `
      <tr>
        <td>${escapeHtml(`${p.menge} × ${p.bezeichnung}`)}${p.rabatt_pct ? ` <small>(-${escapeHtml(p.rabatt_pct)}%)</small>` : ''}</td>
        <td style="text-align:right">${escapeHtml(`${sign}${fmt(p.gesamtpreis)}`)}</td>
      </tr>`).join('')

    const zahlHtml = bon.zahlungen.map((z) => `
      <tr>
        <td>${escapeHtml(({ bar: 'Bar', ec: 'EC-Karte', paypal: 'PayPal', gift_card: 'Geschenkkarte', b2b: 'B2B' }[z.art]))}</td>
        <td style="text-align:right">${escapeHtml(fmt(z.betrag))}</td>
      </tr>${z.wechselgeld ? `<tr><td style="padding-left:1rem">Wechselgeld</td><td style="text-align:right">${escapeHtml(fmt(z.wechselgeld))}</td></tr>` : ''}`).join('')

    const html = `
      <!DOCTYPE html><html><head><meta charset="utf-8">
      <style>
        body { font-family: 'Courier New', monospace; font-size: 12px; width: 80mm; margin: 0 auto; }
        h2 { text-align: center; font-size: 16px; margin: 4px 0; }
        table { width: 100%; border-collapse: collapse; }
        td { padding: 2px 0; }
        hr { border: 1px dashed #000; }
        .total { font-weight: bold; font-size: 14px; }
        .center { text-align: center; }
        .tse { font-size: 10px; word-break: break-all; }
      </style></head><body>
      <h2>${bon.isRetoure ? 'RETOURE' : 'KASSENBON'}</h2>
      <p class="center">${escapeHtml(bon.filiale ?? 'VALEO Landhandel')}</p>
      <hr>
      <table>
        <tr><td>Bon-Nr:</td><td>${escapeHtml(bon.bonNr)}</td></tr>
        <tr><td>Datum:</td><td>${escapeHtml(bon.datum.toLocaleString('de-DE'))}</td></tr>
        <tr><td>Kassierer:</td><td>${escapeHtml(bon.kassierer)}</td></tr>
      </table>
      <hr>
      <table>${posHtml}</table>
      <hr>
      <table class="total">
        <tr><td>GESAMT</td><td style="text-align:right">${escapeHtml(`${sign}${fmt(bon.gesamt)}`)}</td></tr>
      </table>
      <hr>
      <table>${zahlHtml}</table>
      ${bon.tseNr ? `<hr><p class="tse">TSE-Nr: ${escapeHtml(bon.tseNr)}</p>` : ''}
      <hr><p class="center">Vielen Dank!</p>
      </body></html>`

    const w = window.open('', '_blank', 'width=400,height=600')
    if (w) {
      w.document.write(html)
      w.document.close()
      w.focus()
      setTimeout(() => { w.print(); w.close() }, 500)
    }
  }

  async disconnect(): Promise<void> {
    try {
      if (this._serialWriter) { this._serialWriter.releaseLock(); this._serialWriter = null }
      if (this._serialPort) { await this._serialPort.close(); this._serialPort = null }
      if (this._usbDevice) { await this._usbDevice.close(); this._usbDevice = null }
    } catch { /* ignore */ }
    this._method = 'none'
  }
}

// Singleton
export const bonDruck = new BonDruckService()
