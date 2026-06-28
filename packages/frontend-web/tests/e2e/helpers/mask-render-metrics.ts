import type { Page } from '@playwright/test'

export type MaskBenchmarkVariant = 'legacy' | 'pilot'

export type MaskBenchmarkDomain = 'sales-order' | 'kontrakt'

export type MaskRenderMetrics = {
  domain: MaskBenchmarkDomain
  variant: MaskBenchmarkVariant
  entityId: string
  shellReadyMs: number
  initialApiRequests: number
  initialTransferBytes: number
  positionsVisibleMs: number
  positionsApiRequests: number
  domTableNodes: number
  measuredAt: string
}

type ApiObservation = {
  url: string
  bytes: number
}

function isApiRequest(url: string): boolean {
  return /\/api\/v1\//.test(url)
}

function median(values: number[]): number {
  if (values.length === 0) return 0
  const sorted = [...values].sort((a, b) => a - b)
  const mid = Math.floor(sorted.length / 2)
  return sorted.length % 2 === 0 ? (sorted[mid - 1] + sorted[mid]) / 2 : sorted[mid]
}

export function aggregateMetricRuns(runs: MaskRenderMetrics[]): MaskRenderMetrics {
  if (runs.length === 0) {
    throw new Error('aggregateMetricRuns requires at least one run')
  }
  const first = runs[0]
  return {
    domain: first.domain,
    variant: first.variant,
    entityId: first.entityId,
    shellReadyMs: median(runs.map((run) => run.shellReadyMs)),
    initialApiRequests: median(runs.map((run) => run.initialApiRequests)),
    initialTransferBytes: median(runs.map((run) => run.initialTransferBytes)),
    positionsVisibleMs: median(runs.map((run) => run.positionsVisibleMs)),
    positionsApiRequests: median(runs.map((run) => run.positionsApiRequests)),
    domTableNodes: median(runs.map((run) => run.domTableNodes)),
    measuredAt: new Date().toISOString(),
  }
}

export async function measureMaskRender(
  page: Page,
  options: {
    domain: MaskBenchmarkDomain
    variant: MaskBenchmarkVariant
    entityId: string
    path: string
    waitForShellReady: (page: Page) => Promise<void>
    positionsRowSelector: string
    revealPositions: (page: Page) => Promise<void>
  },
): Promise<MaskRenderMetrics> {
  const initialObservations: ApiObservation[] = []
  const positionsObservations: ApiObservation[] = []
  let phase: 'initial' | 'positions' = 'initial'

  const onRequest = (request: { url: () => string; response: () => Promise<{ body: () => Promise<Buffer> } | null> }) => {
    if (!isApiRequest(request.url())) return
    void request.response().then(async (response) => {
      if (!response) return
      const body = await response.body().catch(() => Buffer.from(''))
      const observation = { url: request.url(), bytes: body.byteLength }
      if (phase === 'initial') {
        initialObservations.push(observation)
      } else {
        positionsObservations.push(observation)
      }
    })
  }

  page.on('request', onRequest)

  const startedAt = Date.now()
  await page.goto(options.path, { waitUntil: 'domcontentloaded' })
  await options.waitForShellReady(page)
  const shellReadyMs = Date.now() - startedAt

  phase = 'positions'
  const positionsStartedAt = Date.now()
  await options.revealPositions(page)
  await page.locator(options.positionsRowSelector).first().waitFor({ state: 'visible', timeout: 45_000 })
  const positionsVisibleMs = Date.now() - positionsStartedAt

  page.off('request', onRequest)

  const domTableNodes = await page.locator(options.positionsRowSelector).count()

  return {
    domain: options.domain,
    variant: options.variant,
    entityId: options.entityId,
    shellReadyMs,
    initialApiRequests: initialObservations.length,
    initialTransferBytes: initialObservations.reduce((sum, item) => sum + item.bytes, 0),
    positionsVisibleMs,
    positionsApiRequests: positionsObservations.length,
    domTableNodes,
    measuredAt: new Date().toISOString(),
  }
}

export type MaskAbComparison = {
  domain: MaskBenchmarkDomain
  legacy: MaskRenderMetrics
  pilot: MaskRenderMetrics
  deltas: {
    shellReadyMs: number
    shellReadyPct: number
    initialApiRequests: number
    initialTransferBytes: number
    initialTransferPct: number
    positionsVisibleMs: number
    domTableNodes: number
  }
  pocPassed: boolean
  pocNotes: string[]
}

export function compareMaskMetrics(legacy: MaskRenderMetrics, pilot: MaskRenderMetrics): MaskAbComparison {
  const shellReadyPct = legacy.shellReadyMs > 0
    ? ((legacy.shellReadyMs - pilot.shellReadyMs) / legacy.shellReadyMs) * 100
    : 0
  const initialTransferPct = legacy.initialTransferBytes > 0
    ? ((legacy.initialTransferBytes - pilot.initialTransferBytes) / legacy.initialTransferBytes) * 100
    : 0

  const notes: string[] = []
  if (pilot.initialApiRequests <= legacy.initialApiRequests) {
    notes.push('Pilot reduziert oder gleicht initiale API-Requests.')
  } else {
    notes.push('Pilot hat mehr initiale API-Requests als Legacy.')
  }
  if (pilot.initialTransferBytes < legacy.initialTransferBytes) {
    notes.push('Pilot uebertraegt weniger Bytes beim Erstload.')
  }
  if (pilot.domTableNodes <= legacy.domTableNodes) {
    notes.push('Pilot haelt weniger Tabellen-DOM-Knoten nach Positionsanzeige.')
  }
  if (pilot.positionsApiRequests >= 1) {
    notes.push('Pilot laedt Positionsdaten separat (lazy Tab-Endpoint).')
  }

  const pocPassed =
    pilot.initialTransferBytes <= legacy.initialTransferBytes &&
    pilot.domTableNodes <= legacy.domTableNodes &&
    pilot.shellReadyMs <= legacy.shellReadyMs * 1.25

  return {
    domain: legacy.domain,
    legacy,
    pilot,
    deltas: {
      shellReadyMs: legacy.shellReadyMs - pilot.shellReadyMs,
      shellReadyPct,
      initialApiRequests: legacy.initialApiRequests - pilot.initialApiRequests,
      initialTransferBytes: legacy.initialTransferBytes - pilot.initialTransferBytes,
      initialTransferPct,
      positionsVisibleMs: legacy.positionsVisibleMs - pilot.positionsVisibleMs,
      domTableNodes: legacy.domTableNodes - pilot.domTableNodes,
    },
    pocPassed,
    pocNotes: notes,
  }
}
