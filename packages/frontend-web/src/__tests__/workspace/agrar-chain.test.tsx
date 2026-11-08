import { render, screen } from '@testing-library/react'
import { AxiosError } from 'axios'
import { MemoryRouter } from '@/app/routing/test-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import { apiClient } from '@/lib/api-client'
import {
  AGRAR_CHAIN_PATH,
  AGRAR_NEXT_STEP_LINKS,
  AgrarChainWidget,
  agrarChainLinkFor,
  agrarChainLinkForHint,
  agrarChainParams,
  hasChainProjection,
  loadAgrarChainHints,
  loadVisibleAgrarChain,
  AGRAR_CONTRACTS_PARAMS,
  AGRAR_CONTRACTS_PATH,
  OPEN_KONTRAKTE_PARAMS,
  OPEN_KONTRAKTE_PATH,
  parseAgrarChainHint,
  pickAbrufProjection,
  queriesFromAgrarContractIndex,
  queriesFromKontraktIndex,
  situationalItemsFromAgrarChain,
  WORKSPACE_FACHAKTIONEN,
  emptyUserContext,
  rankWorkspaceItems,
  type AgrarChainHint,
  type AgrarChainQuery,
} from '@/workspace'
import { defaultHomeSignals } from '@/workspace/home-signals'

vi.mock('@/lib/api-client', () => ({
  apiClient: {
    get: vi.fn(),
  },
}))

function httpError(status: number, code = 'ERR_BAD_REQUEST'): AxiosError {
  return new AxiosError('request failed', code, undefined, undefined, {
    status,
    statusText: 'Error',
    data: {},
    headers: {},
    config: { headers: {} as never },
  })
}

const projected: AgrarChainQuery = {
  contract_ref: 'K-1',
  source_model: 'kon',
  contract_status: 'OFFEN',
  disposition_status: 'FREIGEGEBEN',
}

describe('agrar chain mapping', () => {
  it('mappt next_step auf bestehende Routen und laesst done/blocked ohne Buchungs-Klick', () => {
    expect(AGRAR_NEXT_STEP_LINKS.disposition.route).toBe('/disposition/touren-disposition')
    expect(AGRAR_NEXT_STEP_LINKS.waage.route).toBe('/waage/wiegungen')
    expect(AGRAR_NEXT_STEP_LINKS.qualitaet.route).toBe('/annahme/qualitaets-check')
    expect(AGRAR_NEXT_STEP_LINKS.abrechnung.route).toBe('/annahme/abrechnung')
    expect(agrarChainLinkFor('abrechnung')).toMatchObject({
      route: '/annahme/abrechnung',
      clickable: true,
    })
    expect(
      agrarChainLinkForHint({
        next_step: 'abrechnung',
      }),
    ).toMatchObject({ route: '/annahme/abrechnung', clickable: true })
    expect(agrarChainLinkFor('done')).toMatchObject({ route: null, clickable: false })
    expect(agrarChainLinkFor('blocked')).toMatchObject({ route: null, clickable: false })
  })

  it('nimmt aus dem Kontrakt-Index nur vorhandene Felder und mixt kein AgrarContract', () => {
    expect(hasChainProjection({ contract_ref: 'K-1', source_model: 'kon' })).toBe(false)
    expect(
      queriesFromKontraktIndex({
        items: [
          { contract_id: 'K-1', status: 'OFFEN' },
          { id: 'K-2', status: 'OFFEN', lieferstatus: 'FREIGEGEBEN' },
          { party_id: 'ohne-id', status: 'OFFEN' },
        ],
      }),
    ).toEqual([
      { contract_ref: 'K-1', source_model: 'kon', contract_status: 'OFFEN' },
      {
        contract_ref: 'K-2',
        source_model: 'kon',
        contract_status: 'OFFEN',
        disposition_status: 'FREIGEGEBEN',
      },
    ])
    expect(queriesFromKontraktIndex({ items: [{ contract_id: 'K-9' }] })).toEqual([])
    expect(queriesFromKontraktIndex({ items: [{ contract_id: 'A-1', status: 'open' }] })).toEqual([])
    expect(
      queriesFromAgrarContractIndex({
        items: [
          { id: 'A-1', status: 'open' },
          { id: 'A-2', status: 'fulfilled' },
          { id: 'skip', status: 'OFFEN' },
        ],
      }),
    ).toEqual([
      { contract_ref: 'A-1', source_model: 'agrar', contract_status: 'open' },
      { contract_ref: 'A-2', source_model: 'agrar', contract_status: 'fulfilled' },
    ])
    expect(pickAbrufProjection([{ status: 'OFFEN' }, { status: 'FREIGEGEBEN' }])).toEqual({
      disposition_status: 'FREIGEGEBEN',
    })
    expect(pickAbrufProjection([{ status: 'FREIGEGEBEN' }, { status: 'GELIEFERT' }])).toEqual({
      disposition_status: 'GELIEFERT',
    })
    // Kon-Abruf GELIEFERT + kanonischer Wiegeschein → weighing_present (kein Fake-QS).
    expect(
      pickAbrufProjection([
        { status: 'FREIGEGEBEN' },
        { status: 'GELIEFERT', wiegeschein_id: 'wt-probe-1' },
      ]),
    ).toEqual({
      disposition_status: 'GELIEFERT',
      weighing_present: true,
    })
    expect(pickAbrufProjection([{ status: 'OFFEN', wiegeschein_nr: 'WS-1' }])).toEqual({
      disposition_status: 'OFFEN',
      weighing_present: true,
    })
    expect(parseAgrarChainHint({ contract_ref: 'K-1', source_model: 'kon', next_step: 'waage', reason: 'x' })).toEqual(
      {
        contract_ref: 'K-1',
        source_model: 'kon',
        next_step: 'waage',
        reason: 'x',
      },
    )
    expect(
      parseAgrarChainHint({
        contract_ref: 'A-9',
        source_model: 'agrar',
        next_step: 'abrechnung',
        reason: 'agrar_qs_final_settlement_offen',
      }),
    ).toEqual({
      contract_ref: 'A-9',
      source_model: 'agrar',
      next_step: 'abrechnung',
      reason: 'agrar_qs_final_settlement_offen',
    })
    expect(
      agrarChainParams({
        contract_ref: 'A-9',
        source_model: 'agrar',
        contract_status: 'fulfilled',
      }).quality_is_final,
    ).toBeUndefined()
    expect(agrarChainParams(projected).tenant_id).toBeUndefined()
    expect(agrarChainParams(projected).status).toBeUndefined()
    expect(
      agrarChainParams({ contract_ref: 'A-1', source_model: 'agrar', contract_status: 'open' }),
    ).toEqual({
      contract_ref: 'A-1',
      source_model: 'agrar',
      contract_status: 'open',
    })
  })
})

describe('agrar chain load', () => {
  beforeEach(() => {
    vi.mocked(apiClient.get).mockReset()
  })

  it('ruft den GET nicht ohne Statusfelder auf', async () => {
    const state = await loadAgrarChainHints([{ contract_ref: 'K-1', source_model: 'kon' }])
    expect(state).toEqual({ status: 'empty' })
    expect(apiClient.get).not.toHaveBeenCalled()
  })

  it('liest offene KonContracte und projiziert agrar-chain ohne Agrar-Mix', async () => {
    vi.mocked(apiClient.get).mockImplementation(async (path: string) => {
      if (path === OPEN_KONTRAKTE_PATH) {
        return { data: { items: [{ contract_id: 'K-1', status: 'OFFEN' }], total: 1 } }
      }
      if (path === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      if (String(path).includes('/dispositionen')) {
        return { data: [] }
      }
      return {
        data: {
          contract_ref: 'K-1',
          source_model: 'kon',
          next_step: 'disposition',
          reason: 'kontrakt_offen_abruf_fehlt_oder_offen',
        },
      }
    })

    const state = await loadVisibleAgrarChain()
    expect(apiClient.get).toHaveBeenCalledWith(OPEN_KONTRAKTE_PATH, { params: OPEN_KONTRAKTE_PARAMS })
    expect(apiClient.get).toHaveBeenCalledWith(AGRAR_CHAIN_PATH, {
      params: { contract_ref: 'K-1', source_model: 'kon', contract_status: 'OFFEN' },
    })
    expect(state).toEqual({
      status: 'ready',
      hints: [
        {
          contract_ref: 'K-1',
          source_model: 'kon',
          next_step: 'disposition',
          reason: 'kontrakt_offen_abruf_fehlt_oder_offen',
        },
      ],
    })
  })

  it('bleibt bei leerem Index ohne Fake-Zeilen und ohne Chain-GET', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: { items: [], total: 0 } } as never)
    const state = await loadVisibleAgrarChain()
    expect(state).toEqual({ status: 'empty' })
    expect(apiClient.get).toHaveBeenCalledTimes(2)
    expect(apiClient.get).toHaveBeenCalledWith(AGRAR_CONTRACTS_PATH, { params: AGRAR_CONTRACTS_PARAMS })
  })

  it('projiziert AgrarContract open auf source_model=agrar ohne Fake-QS', async () => {
    vi.mocked(apiClient.get).mockImplementation(async (path: string) => {
      if (path === OPEN_KONTRAKTE_PATH) {
        return { data: { items: [] } }
      }
      if (path === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [{ id: 'A-1', status: 'open' }] } }
      }
      return {
        data: {
          contract_ref: 'A-1',
          source_model: 'agrar',
          next_step: 'waage',
          reason: 'agrar_kontrakt_open_einstieg_waage',
        },
      }
    })

    const state = await loadVisibleAgrarChain()
    expect(apiClient.get).toHaveBeenCalledWith(AGRAR_CHAIN_PATH, {
      params: { contract_ref: 'A-1', source_model: 'agrar', contract_status: 'open' },
    })
    expect(state).toEqual({
      status: 'ready',
      hints: [
        {
          contract_ref: 'A-1',
          source_model: 'agrar',
          next_step: 'waage',
          reason: 'agrar_kontrakt_open_einstieg_waage',
        },
      ],
    })
  })

  it('laesst Server-next_step abrechnung bei agrar fulfilled unangetastet', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({
      data: {
        contract_ref: 'A-settle',
        source_model: 'agrar',
        next_step: 'abrechnung',
        reason: 'agrar_qs_final_settlement_offen',
      },
    } as never)

    const state = await loadAgrarChainHints([
      { contract_ref: 'A-settle', source_model: 'agrar', contract_status: 'fulfilled' },
    ])
    expect(state).toEqual({
      status: 'ready',
      hints: [
        {
          contract_ref: 'A-settle',
          source_model: 'agrar',
          next_step: 'abrechnung',
          reason: 'agrar_qs_final_settlement_offen',
        },
      ],
    })
    expect(apiClient.get).toHaveBeenCalledWith(AGRAR_CHAIN_PATH, {
      params: { contract_ref: 'A-settle', source_model: 'agrar', contract_status: 'fulfilled' },
    })
  })

  it('blendet bei 401 aus und zeigt andere Fehler', async () => {
    vi.mocked(apiClient.get).mockRejectedValue(httpError(401))
    expect(await loadVisibleAgrarChain()).toEqual({ status: 'hidden' })

    vi.mocked(apiClient.get).mockRejectedValue(httpError(500))
    expect(await loadVisibleAgrarChain()).toEqual({
      status: 'error',
      message: 'Agrar-Kette nicht lesbar (HTTP 500).',
    })
  })
})

describe('AgrarChainWidget', () => {
  beforeEach(() => {
    vi.mocked(apiClient.get).mockReset()
  })

  it('zeigt keine Kette bei leerem Kontrakt-Index', async () => {
    vi.mocked(apiClient.get).mockResolvedValue({ data: { items: [] } } as never)
    render(
      <MemoryRouter>
        <AgrarChainWidget />
      </MemoryRouter>,
    )
    expect(screen.getByTestId('workspace-agrar-chain')).toHaveAttribute('data-chain-status', 'pending')
    expect(await screen.findByText('keine Kette')).toBeInTheDocument()
    expect(apiClient.get).toHaveBeenCalledWith(OPEN_KONTRAKTE_PATH, { params: OPEN_KONTRAKTE_PARAMS })
    expect(apiClient.get).toHaveBeenCalledWith(AGRAR_CONTRACTS_PATH, { params: AGRAR_CONTRACTS_PARAMS })
    expect(
      vi.mocked(apiClient.get).mock.calls.some((call) => String(call[0]).includes('/workspace/agrar-chain')),
    ).toBe(false)
  })

  it('zeigt next_step als Handlungsbedarf-Link und done nur als Status', async () => {
    vi.mocked(apiClient.get).mockImplementation(async (_path, config) => {
      const params = (config as { params?: { contract_ref?: string } } | undefined)?.params
      if (params?.contract_ref === 'K-1') {
        return {
          data: {
            contract_ref: 'K-1',
            source_model: 'kon',
            next_step: 'waage',
            reason: 'abruf_freigegeben_waage_fehlt',
          },
        }
      }
      return {
        data: {
          contract_ref: 'K-9',
          source_model: 'kon',
          next_step: 'done',
          reason: 'kontrakt_erledigt_oder_settlement_posted',
        },
      }
    })

    render(
      <MemoryRouter>
        <AgrarChainWidget
          queries={[
            projected,
            { contract_ref: 'K-9', source_model: 'kon', contract_status: 'ERLEDIGT' },
          ]}
        />
      </MemoryRouter>,
    )

    const waage = await screen.findByRole('link', { name: 'K-1: Waage' })
    expect(waage).toHaveAttribute('href', '/waage/wiegungen')
    expect(screen.getByText('K-9: Abgeschlossen')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'K-9: Abgeschlossen' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /buchen|submit|freigeben/i })).not.toBeInTheDocument()
  })

  it('landet mit Lieferstatus FREIGEGEBEN auf dem Waage-Link', async () => {
    vi.mocked(apiClient.get).mockImplementation(async (path: string) => {
      if (path === OPEN_KONTRAKTE_PATH) {
        return { data: { items: [{ contract_id: 'K-2', status: 'OFFEN' }] } }
      }
      if (path === AGRAR_CONTRACTS_PATH) {
        return { data: { items: [] } }
      }
      if (String(path).includes('/dispositionen')) {
        return { data: [{ id: 'd-1', status: 'FREIGEGEBEN' }] }
      }
      return {
        data: {
          contract_ref: 'K-2',
          source_model: 'kon',
          next_step: 'waage',
          reason: 'abruf_freigegeben_waage_fehlt',
        },
      }
    })

    render(
      <MemoryRouter>
        <AgrarChainWidget />
      </MemoryRouter>,
    )

    const waage = await screen.findByRole('link', { name: 'K-2: Waage' })
    expect(waage).toHaveAttribute('href', '/waage/wiegungen')
    expect(apiClient.get).toHaveBeenCalledWith(AGRAR_CHAIN_PATH, {
      params: {
        contract_ref: 'K-2',
        source_model: 'kon',
        contract_status: 'OFFEN',
        disposition_status: 'FREIGEGEBEN',
      },
    })
  })

  it('sendet contract_status fuer AgrarContract: open=Waage, fulfilled=Qualitaet, cancelled ohne Buchungs-Klick', async () => {
    vi.mocked(apiClient.get).mockImplementation(async (path: string, config) => {
      if (path === OPEN_KONTRAKTE_PATH) {
        return { data: { items: [] } }
      }
      if (path === AGRAR_CONTRACTS_PATH) {
        return {
          data: {
            items: [
              { id: 'A-open', status: 'open' },
              { id: 'A-done', status: 'fulfilled' },
              { id: 'A-stop', status: 'cancelled' },
            ],
          },
        }
      }
      const params = (config as { params?: Record<string, string> } | undefined)?.params ?? {}
      expect(params.status).toBeUndefined()
      expect(params.quality_is_final).toBeUndefined()
      expect(params.source_model).toBe('agrar')
      const nextStep =
        params.contract_status === 'open'
          ? 'waage'
          : params.contract_status === 'fulfilled'
            ? 'qualitaet'
            : 'blocked'
      return {
        data: {
          contract_ref: params.contract_ref,
          source_model: 'agrar',
          next_step: nextStep,
          reason: `mapped_${params.contract_status}`,
        },
      }
    })

    render(
      <MemoryRouter>
        <AgrarChainWidget />
      </MemoryRouter>,
    )

    const waage = await screen.findByRole('link', { name: 'A-open: Waage' })
    expect(waage).toHaveAttribute('href', '/waage/wiegungen')
    expect(screen.getByRole('link', { name: 'A-done: Qualitaet' })).toHaveAttribute(
      'href',
      '/annahme/qualitaets-check',
    )
    expect(screen.getByText('A-stop: Blockiert')).toBeInTheDocument()
    expect(screen.queryByRole('link', { name: 'A-stop: Blockiert' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /buchen|submit|freigeben/i })).not.toBeInTheDocument()
    expect(apiClient.get).toHaveBeenCalledWith(AGRAR_CHAIN_PATH, {
      params: { contract_ref: 'A-open', source_model: 'agrar', contract_status: 'open' },
    })
    expect(apiClient.get).toHaveBeenCalledWith(AGRAR_CHAIN_PATH, {
      params: { contract_ref: 'A-done', source_model: 'agrar', contract_status: 'fulfilled' },
    })
    expect(apiClient.get).toHaveBeenCalledWith(AGRAR_CHAIN_PATH, {
      params: { contract_ref: 'A-stop', source_model: 'agrar', contract_status: 'cancelled' },
    })
  })

  it('zeigt Server-next_step abrechnung bei agrar fulfilled als Abrechnung-Link, nicht Qualitaet', async () => {
    vi.mocked(apiClient.get).mockImplementation(async (path: string, config) => {
      if (path === OPEN_KONTRAKTE_PATH) {
        return { data: { items: [] } }
      }
      if (path === AGRAR_CONTRACTS_PATH) {
        return {
          data: {
            items: [
              { id: 'A-settle', status: 'fulfilled' },
              { id: 'A-qs', status: 'fulfilled' },
            ],
          },
        }
      }
      const params = (config as { params?: Record<string, unknown> } | undefined)?.params ?? {}
      expect(params.status).toBeUndefined()
      expect(params.quality_is_final).toBeUndefined()
      expect(params.source_model).toBe('agrar')
      expect(params.contract_status).toBe('fulfilled')
      const nextStep = params.contract_ref === 'A-settle' ? 'abrechnung' : 'qualitaet'
      return {
        data: {
          contract_ref: params.contract_ref,
          source_model: 'agrar',
          next_step: nextStep,
          reason: nextStep === 'abrechnung' ? 'agrar_qs_final_settlement_offen' : 'agrar_fulfilled_qualitaet',
        },
      }
    })

    render(
      <MemoryRouter>
        <AgrarChainWidget />
      </MemoryRouter>,
    )

    const abrechnung = await screen.findByRole('link', { name: 'A-settle: Abrechnung' })
    expect(abrechnung).toHaveAttribute('href', '/annahme/abrechnung')
    expect(screen.getByRole('link', { name: 'A-qs: Qualitaet' })).toHaveAttribute(
      'href',
      '/annahme/qualitaets-check',
    )
    expect(screen.queryByRole('link', { name: 'A-settle: Qualitaet' })).not.toBeInTheDocument()
    expect(screen.queryByRole('button', { name: /buchen|submit|freigeben|speichern/i })).not.toBeInTheDocument()
    expect(apiClient.get).toHaveBeenCalledWith(AGRAR_CHAIN_PATH, {
      params: { contract_ref: 'A-settle', source_model: 'agrar', contract_status: 'fulfilled' },
    })
    expect(apiClient.get).toHaveBeenCalledWith(AGRAR_CHAIN_PATH, {
      params: { contract_ref: 'A-qs', source_model: 'agrar', contract_status: 'fulfilled' },
    })
    expect(
      vi.mocked(apiClient.get).mock.calls.some((call) => {
        const params = (call[1] as { params?: Record<string, unknown> } | undefined)?.params
        return params?.quality_is_final === true
      }),
    ).toBe(false)
  })

  it('blendet die Sektion bei 401 aus und verschluckt 500 nicht', async () => {
    vi.mocked(apiClient.get).mockRejectedValue(httpError(401))
    const hidden = render(
      <MemoryRouter>
        <AgrarChainWidget />
      </MemoryRouter>,
    )
    await vi.waitFor(() => {
      expect(hidden.container.querySelector('[data-testid="workspace-agrar-chain"]')).toBeNull()
    })
    hidden.unmount()

    vi.mocked(apiClient.get).mockRejectedValue(httpError(503))
    render(
      <MemoryRouter>
        <AgrarChainWidget />
      </MemoryRouter>,
    )
    expect(await screen.findByRole('alert')).toHaveTextContent('Agrar-Kette nicht lesbar (HTTP 503).')
  })
})

function hint(
  contractRef: string,
  source: AgrarChainHint['source_model'],
  nextStep: AgrarChainHint['next_step'],
  reason: string,
): AgrarChainHint {
  return { contract_ref: contractRef, source_model: source, next_step: nextStep, reason }
}

describe('situative Agrar-Ketten-Signale', () => {
  const loaded = {
    status: 'ready' as const,
    hints: [
      hint('K-OFF', 'kon', 'disposition', 'kontrakt_offen_abruf_fehlt_oder_offen'),
      hint('K-2', 'kon', 'waage', 'abruf_freigegeben_waage_fehlt'),
      hint('K-G', 'kon', 'qualitaet', 'abruf_geliefert_oder_wiegeschein_vorhanden'),
      hint('A-settle', 'agrar', 'abrechnung', 'annahme_oder_qs_fertig_settlement_offen'),
      hint('K-9', 'kon', 'done', 'kontrakt_erledigt_oder_settlement_posted'),
      hint('K-X', 'kon', 'blocked', 'kontrakt_oder_abruf_storniert'),
    ],
  }

  it('gibt geladene Klick-Schritte als situative Signale auf bestehenden Routen', () => {
    const { actions, signals } = situationalItemsFromAgrarChain(loaded)
    expect(actions.map((action) => [action.label, action.target.route, action.layer])).toEqual([
      ['K-OFF: Disposition', AGRAR_NEXT_STEP_LINKS.disposition.route, 'situational'],
      ['K-2: Waage', '/waage/wiegungen', 'situational'],
      ['K-G: Qualitaet', '/annahme/qualitaets-check', 'situational'],
      ['A-settle: Abrechnung', '/annahme/abrechnung', 'situational'],
    ])
    expect(signals.map((signal) => signal.relatedActionIds[0])).toEqual(actions.map((action) => action.id))
    expect(signals.every((signal) => signal.layer === 'situational' && signal.kind === 'open-task' && signal.severity === 3)).toBe(true)
    expect(JSON.stringify({ actions, signals })).not.toContain('quality_is_final')
    expect(actions.some((action) => action.label.includes('Abgeschlossen') || action.label.includes('Blockiert'))).toBe(false)
  })

  it('blendet leere Liste, 401 und Fehler aus und schiebt done nicht nach vorn', () => {
    expect(situationalItemsFromAgrarChain({ status: 'empty' })).toEqual({ actions: [], signals: [] })
    expect(situationalItemsFromAgrarChain({ status: 'hidden' })).toEqual({ actions: [], signals: [] })
    expect(situationalItemsFromAgrarChain({ status: 'error', message: 'Agrar-Kette nicht lesbar (HTTP 401).' })).toEqual({
      actions: [],
      signals: [],
    })
    expect(situationalItemsFromAgrarChain({ status: 'pending' })).toEqual({ actions: [], signals: [] })

    const now = new Date('2026-10-22T08:00:00')
    const chain = situationalItemsFromAgrarChain({
      status: 'ready',
      hints: [loaded.hints[1], loaded.hints[4]],
    })
    const ranked = rankWorkspaceItems({
      actions: [...WORKSPACE_FACHAKTIONEN, ...chain.actions],
      context: emptyUserContext({
        scopes: WORKSPACE_FACHAKTIONEN.flatMap((action) => action.requiredScopes),
        pinned: ['workspace.document-inbox'],
      }),
      signals: [...defaultHomeSignals(now), ...chain.signals],
      now,
    }).slice(0, 5)

    expect(ranked[0]?.action.id).toBe('workspace.document-inbox')
    expect(ranked[0]?.reasonCodes).toContain('pinned')
    const waage = ranked.find((item) => item.action.id === 'agrar.chain.kon.K-2.waage')
    expect(waage?.action.target.route).toBe('/waage/wiegungen')
    expect(waage?.reasonCodes).toEqual(expect.arrayContaining(['layer:situational', 'signal:open-task', 'severity:3']))
    expect(waage?.reasonCodes).not.toContain('pinned')
    expect(ranked.some((item) => item.action.id.includes('.done') || item.action.label.includes('Abgeschlossen'))).toBe(false)
    expect((ranked[0]?.score ?? 0) > (waage?.score ?? 0)).toBe(true)
  })
})
