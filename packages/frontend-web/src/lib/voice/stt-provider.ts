/**
 * Speech-to-Text Adapter-Contract (UIX-072).
 *
 * Einheitliche Schnittstelle fuer Diktat/Sprach-Eingabe. Datenschutz-Vertrag:
 * kein Audio-Persist; Server-Provider verwirft Audio nach der Transkription;
 * Transkript-Inhalte werden nie geloggt (Telemetrie nur Metadaten).
 */

export type SttProviderId = 'webspeech' | 'server'

declare global {
  interface Window {
    __VALEO_STT_PROVIDER__?: SttProvider
  }
}

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

export class WebSpeechSttProvider implements SttProvider {
  readonly id: SttProviderId = 'webspeech'
  private recognition: {
    lang: string
    interimResults: boolean
    start: () => void
    stop: () => void
    onresult: ((event: unknown) => void) | null
    onerror: ((event: { error?: string; message?: string }) => void) | null
  } | null = null
  private partialCbs: Array<(t: string) => void> = []
  private finalCbs: Array<(t: string, c?: number) => void> = []
  private errorCbs: Array<(e: SttError) => void> = []

  constructor() {
    if (typeof window === 'undefined') return
    const speechWindow = window as unknown as {
      SpeechRecognition?: new () => WebSpeechSttProvider['recognition']
      webkitSpeechRecognition?: new () => WebSpeechSttProvider['recognition']
    }
    const Ctor = speechWindow.SpeechRecognition ?? speechWindow.webkitSpeechRecognition
    this.recognition = Ctor ? new Ctor() : null
    if (!this.recognition) return
    this.recognition.onresult = (event: unknown) => {
      const resultEvent = event as {
        results?: ArrayLike<{ isFinal?: boolean; 0?: { transcript?: string; confidence?: number } }>
      }
      const results = resultEvent.results
      if (!results) return
      const latest = results[results.length - 1]
      const text = latest?.[0]?.transcript?.trim() ?? ''
      if (!text) return
      if (latest.isFinal) {
        for (const cb of this.finalCbs) cb(text, latest[0]?.confidence)
      } else {
        for (const cb of this.partialCbs) cb(text)
      }
    }
    this.recognition.onerror = (event) => {
      const code = event.error ?? 'webspeech_error'
      for (const cb of this.errorCbs) cb({ code, message: event.message ?? code })
    }
  }

  isAvailable(): boolean {
    return this.recognition !== null
  }

  start(opts: SttStartOptions): void {
    if (!this.recognition) return
    this.recognition.lang = opts.lang
    this.recognition.interimResults = opts.interim
    this.recognition.start()
  }

  stop(): void {
    this.recognition?.stop()
  }

  onPartial(cb: (text: string) => void): void {
    this.partialCbs.push(cb)
  }

  onFinal(cb: (text: string, confidence?: number) => void): void {
    this.finalCbs.push(cb)
  }

  onError(cb: (err: SttError) => void): void {
    this.errorCbs.push(cb)
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

export function createDefaultSttProvider(config: VoiceConfig = { enabled: true, provider: 'webspeech' }): SttProvider | null {
  const injectedProvider = typeof window === 'undefined' ? undefined : window.__VALEO_STT_PROVIDER__
  if (injectedProvider) {
    return injectedProvider
  }
  return selectSttProvider(config, {
    webspeech: () => new WebSpeechSttProvider(),
    server: () => new FakeSttProvider({ id: 'server', available: false }),
  })
}
