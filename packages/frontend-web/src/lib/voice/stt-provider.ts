/**
 * Speech-to-Text Adapter-Contract (UIX-072).
 *
 * Einheitliche Schnittstelle fuer Diktat/Sprach-Eingabe. Datenschutz-Vertrag:
 * kein Audio-Persist; Server-Provider verwirft Audio nach der Transkription;
 * Transkript-Inhalte werden nie geloggt (Telemetrie nur Metadaten).
 */

export type SttProviderId = 'webspeech' | 'server'

export interface SttStartOptions {
  lang: 'de-DE'
  interim: boolean
}

export interface SttError {
  code: string
  message: string
}

export interface SttProvider {
  readonly id: SttProviderId
  isAvailable(): boolean
  start(opts: SttStartOptions): void
  stop(): void
  onPartial(cb: (text: string) => void): void
  onFinal(cb: (text: string, confidence?: number) => void): void
  onError(cb: (err: SttError) => void): void
}

/** Telemetrie-Shape (UIX-072) — bewusst OHNE Transkript-Inhalt. */
export interface VoiceTelemetry {
  used: boolean
  provider: SttProviderId
  duration_s: number
  target: 'field' | 'omnibox'
}

/**
 * Test-/Fallback-Double: emittiert partial/final/error programmatisch.
 * Auch als Basisklasse fuer echte Provider nutzbar (Listener-Verwaltung).
 */
export class FakeSttProvider implements SttProvider {
  readonly id: SttProviderId
  private available: boolean
  private partialCbs: Array<(t: string) => void> = []
  private finalCbs: Array<(t: string, c?: number) => void> = []
  private errorCbs: Array<(e: SttError) => void> = []
  started = false
  stopped = false
  lastOptions?: SttStartOptions

  constructor(opts: { id?: SttProviderId; available?: boolean } = {}) {
    this.id = opts.id ?? 'webspeech'
    this.available = opts.available ?? true
  }

  isAvailable(): boolean {
    return this.available
  }

  start(opts: SttStartOptions): void {
    this.started = true
    this.stopped = false
    this.lastOptions = opts
  }

  stop(): void {
    this.stopped = true
    this.started = false
  }

  onPartial(cb: (t: string) => void): void {
    this.partialCbs.push(cb)
  }

  onFinal(cb: (t: string, c?: number) => void): void {
    this.finalCbs.push(cb)
  }

  onError(cb: (e: SttError) => void): void {
    this.errorCbs.push(cb)
  }

  // ── Test-Steuerung ──────────────────────────────────────────────────────────
  emitPartial(text: string): void {
    for (const cb of this.partialCbs) cb(text)
  }

  emitFinal(text: string, confidence?: number): void {
    for (const cb of this.finalCbs) cb(text, confidence)
  }

  emitError(error: SttError): void {
    for (const cb of this.errorCbs) cb(error)
  }
}

export interface VoiceConfig {
  enabled: boolean
  provider: SttProviderId
}

/**
 * Waehlt einen verfuegbaren Provider gemaess Konfiguration mit Fallback-Kette
 * webspeech → server → disabled (null). Reine Auswahl, testbar ueber Factories.
 */
export function selectSttProvider(
  config: VoiceConfig,
  factories: Partial<Record<SttProviderId, () => SttProvider>>,
): SttProvider | null {
  if (!config.enabled) return null
  const chain: SttProviderId[] = config.provider === 'server' ? ['server', 'webspeech'] : ['webspeech', 'server']
  for (const id of chain) {
    const factory = factories[id]
    if (!factory) continue
    const provider = factory()
    if (provider.isAvailable()) return provider
  }
  return null
}
