import { useCallback, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { Pin, PinOff, Search } from 'lucide-react'
import { useTranslation } from 'react-i18next'
import { Link, useNavigate, type RouteTarget } from '@/app/routing/typed-router'
import {
  situationalItemsFromInboxQueue,
  type InboxQueueSnapshot,
} from '@/components/adaptive-workspace/inbox'
import {
  ABRUFE_AUTH_ERROR,
  fetchOpenAbrufe,
} from '@/components/mask-builder/specialized/load-abrufe'
import { useNavSections } from '@/app/navigation/nav-runtime'
import { resolveLaunchpadSpaces } from '@/app/navigation/launchpad-spaces'
import {
  pinTile,
  setSurfaceLocked,
  unpinTile,
} from '@/app/navigation/launchpad-personalization'
import { LaunchpadBoard } from '@/components/navigation/LaunchpadBoard'
import { Button } from '@/components/ui/button'
import { useAuth } from '@/hooks/useAuth'
import { auth } from '@/lib/auth'
import { tenantFromToken } from '@/lib/tenant-from-token'
import { useFeature } from '@/hooks/useFeature'
import { useLaunchpadPersonalization } from '@/hooks/useLaunchpadPersonalization'
import { useWorkspaceCompositionOverlay } from '@/hooks/useWorkspaceCompositionOverlay'
import { WorkspaceCompositionHost } from '@/studio/WorkspaceCompositionHost'
import { WORKSPACE_FACHAKTIONEN } from './registry'
import { authorizeFachaktionen, mapFachaktionToCommand } from './command-mapping'
import { rankedLaunchpadTileIds, workspaceNow } from './home-signals'
import { mergeHomeSignals, signalFromOpenAbrufe, useWorkspaceLiveSignals } from './live-signals'
import { rankWorkspaceItems } from './prioritization'
import { useRankingAdvisor } from './ranking-advisor'
import { userContextFromPersonalization } from './user-context'
import { situationalItemsFromAgrarChain } from './agrar-chain'
import { AgrarChainWidget, useAgrarChainView } from './AgrarChainWidget'
import {
  personalizeHomeComposition,
  resolveHomeComposition,
  signalsForHomeSpecialists,
} from './home-composition'
import { requestExistingCommandPalette } from './request-command-palette'
import { openInboxItemInMask } from './sibling-slots'
import type { TypedFachaktion } from './types'

function pinKeys(action: TypedFachaktion): string[] {
  return action.launchpadTileId ? [action.id, action.launchpadTileId] : [action.id]
}

export function AdaptiveWorkspaceLayer(): JSX.Element {
  const sections = useNavSections()
  const { i18n } = useTranslation()
  const { user } = useAuth()
  const tenantId = tenantFromToken(auth.getAccessToken())
  const { overlay, setOverlay } = useLaunchpadPersonalization()
  const navigate = useNavigate()
  const commandPaletteEnabled = useFeature('commandPalette')
  const [spaceId, setSpaceId] = useState('')
  const [pageBySpace, setPageBySpace] = useState<Record<string, string>>({})

  const catalogSpaces = useMemo(
    () => resolveLaunchpadSpaces(sections, i18n.resolvedLanguage ?? i18n.language),
    [i18n.language, i18n.resolvedLanguage, sections],
  )

  const context = useMemo(
    () =>
      userContextFromPersonalization({
        overlay,
        roles: user?.roles ?? [],
        scopes: user?.scopes ?? [],
        locale: (i18n.resolvedLanguage ?? i18n.language ?? 'de').split('-')[0],
      }),
    [i18n.language, i18n.resolvedLanguage, overlay, user?.roles, user?.scopes],
  )

  const now = useMemo(() => workspaceNow(), [])
  const rankingAdvisor = useRankingAdvisor()
  const liveSignals = useWorkspaceLiveSignals(now)
  const accessToken = auth.getAccessToken()
  const hasAbrufeSession = Boolean(accessToken)
  const openAbrufe = useQuery({
    queryKey: ['disposition', 'kontrakt-abrufe'],
    queryFn: fetchOpenAbrufe,
    enabled: hasAbrufeSession,
    retry: false,
  })
  const dispositionSignal = useMemo(
    () =>
      hasAbrufeSession && openAbrufe.isSuccess
        ? signalFromOpenAbrufe(openAbrufe.data ?? [])
        : null,
    [hasAbrufeSession, openAbrufe.data, openAbrufe.isSuccess],
  )
  const chain = useAgrarChainView()
  const chainWork = useMemo(() => situationalItemsFromAgrarChain(chain), [chain])
  const [inboxQueue, setInboxQueue] = useState<InboxQueueSnapshot>({ status: 'pending', items: [] })
  const onInboxQueue = useCallback((snapshot: InboxQueueSnapshot) => {
    setInboxQueue(snapshot)
  }, [])
  const inboxWork = useMemo(
    () => situationalItemsFromInboxQueue(inboxQueue, liveSignals),
    [inboxQueue, liveSignals],
  )
  const baseHomeComposition = useMemo(
    () => resolveHomeComposition(undefined, user?.sub, tenantId),
    [tenantId, user?.sub],
  )
  const { overlay: compositionOverlay } = useWorkspaceCompositionOverlay(
    baseHomeComposition.composition.personalization,
  )
  const homeComposition = useMemo(
    () => personalizeHomeComposition(baseHomeComposition, compositionOverlay),
    [baseHomeComposition, compositionOverlay],
  )
  const specialistKinds = homeComposition.kinds
  const abrufeAuthHint = useMemo(() => {
    if (!specialistKinds.includes('disposition_board')) {
      return null
    }
    if (!hasAbrufeSession) {
      return ABRUFE_AUTH_ERROR
    }
    if (!openAbrufe.isError) {
      return null
    }
    return openAbrufe.error instanceof Error ? openAbrufe.error.message : 'Abrufe nicht lesbar.'
  }, [hasAbrufeSession, openAbrufe.error, openAbrufe.isError, specialistKinds])
  const signals = useMemo(
    () => signalsForHomeSpecialists(
      mergeHomeSignals(
        mergeHomeSignals(mergeHomeSignals(liveSignals, chainWork.signals), inboxWork.signals),
        dispositionSignal ? [dispositionSignal] : [],
      ),
      specialistKinds,
    ),
    [chainWork.signals, dispositionSignal, inboxWork.signals, liveSignals, specialistKinds],
  )

  const ranked = useMemo(() => {
    const actions = authorizeFachaktionen(WORKSPACE_FACHAKTIONEN, user ? user.scopes : undefined)
    const inboxActions = specialistKinds.includes('inbox') ? inboxWork.actions : []
    return rankWorkspaceItems({
      actions: [...actions, ...chainWork.actions, ...inboxActions],
      context: {
        ...context,
        scopes: user ? context.scopes : actions.flatMap((action) => action.requiredScopes),
      },
      signals,
      now,
      advisor: rankingAdvisor,
    }).slice(0, 5)
  }, [chainWork.actions, context, inboxWork.actions, now, rankingAdvisor, signals, specialistKinds, user])

  const rankedTileIds = useMemo(
    () => rankedLaunchpadTileIds(ranked.map((item) => item.action)),
    [ranked],
  )

  const activeSpaceId = catalogSpaces.some((space) => space.id === spaceId)
    ? spaceId
    : (catalogSpaces[0]?.id ?? '')

  return (
    <div className="flex flex-col gap-4" data-testid="adaptive-workspace-layer">
      <header className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-foreground">Start</h1>
          <p className="text-sm text-muted-foreground">
            Wo bin ich, was kann ich tun, was ist wichtig.
          </p>
        </div>
        <Button
          type="button"
          variant={overlay.surfaceLocked ? 'default' : 'outline'}
          className="h-11"
          aria-pressed={overlay.surfaceLocked}
          aria-label={overlay.surfaceLocked ? 'Oberfläche gelöst' : 'Oberfläche fixieren'}
          onClick={() => setOverlay((current) => setSurfaceLocked(current, !current.surfaceLocked))}
        >
          {overlay.surfaceLocked ? 'Oberfläche fixiert' : 'Oberfläche fixieren'}
        </Button>
      </header>

      <section aria-label="Dialog" data-testid="workspace-dialog-layer">
        <h2 className="text-lg font-semibold text-foreground">Dialog</h2>
        <p className="mt-1 text-sm text-muted-foreground">Strg+K öffnet die Suche.</p>
        <Button
          type="button"
          variant="outline"
          className="mt-2 h-11 max-w-lg justify-start"
          aria-label="Suche öffnen"
          data-testid="workspace-dialog-palette"
          disabled={!commandPaletteEnabled}
          onClick={() => {
            if (!commandPaletteEnabled) {
              return
            }
            requestExistingCommandPalette()
          }}
        >
          <Search className="mr-2 h-4 w-4" aria-hidden="true" />
          <span>Suche</span>
          <kbd className="ml-auto rounded bg-muted px-2 py-0.5 text-xs">Strg+K</kbd>
        </Button>
      </section>

      <section aria-label="Handlungsbedarf" data-testid="workspace-work-items">
        <h2 className="text-lg font-semibold text-foreground">Handlungsbedarf</h2>
        {abrufeAuthHint ? (
          <p
            className="mt-2 text-sm text-status-error"
            role="alert"
            data-testid="workspace-abrufe-error"
          >
            {abrufeAuthHint}
          </p>
        ) : null}
        <ul className="mt-2 flex flex-col gap-2">
          {ranked.map((item) => {
            const command = mapFachaktionToCommand(item.action)
            const path = typeof command.actionParams.path === 'string' ? command.actionParams.path : item.action.target.route
            const pinned = pinKeys(item.action).some((key) => (overlay.pinnedTileIds ?? []).includes(key))
            return (
              <li
                key={item.action.id}
                className="flex flex-wrap items-center justify-between gap-2 rounded-(--radius) border border-border bg-card px-3 py-2"
                data-fachaktion-id={item.action.id}
                data-catalog-id={item.action.catalogId}
                data-kind={item.action.kind}
              >
                <div className="min-w-0">
                  <Link
                    to={path as RouteTarget}
                    className="text-sm font-medium text-foreground underline-offset-4 hover:underline"
                  >
                    {item.action.label}
                  </Link>
                  {item.action.kind === 'prepare-command' ? (
                    <p className="text-2xs tracking-wide uppercase text-muted-foreground">vorbereiten — nicht buchen</p>
                  ) : null}
                  <p className="truncate text-xs text-muted-foreground">{item.reasonCodes.join(' · ')}</p>
                </div>
                <Button
                  type="button"
                  variant="ghost"
                  className="h-11"
                  aria-pressed={pinned}
                  aria-label={pinned ? `${item.action.label} lösen` : `${item.action.label} pinnen`}
                  onClick={() => {
                    setOverlay((current) =>
                      pinKeys(item.action).reduce(
                        (next, key) => (pinned ? unpinTile(next, key) : pinTile(next, key)),
                        current,
                      ),
                    )
                  }}
                >
                  {pinned ? <PinOff className="h-4 w-4" /> : <Pin className="h-4 w-4" />}
                </Button>
              </li>
            )
          })}
        </ul>
      </section>

      <AgrarChainWidget view={chain} />

      {specialistKinds.length > 0 ? (
        <WorkspaceCompositionHost
          key={`${homeComposition.composition.id}:${homeComposition.composition.studioVersion}:${specialistKinds.join(',')}`}
          composition={homeComposition.composition}
          variant="embedded"
          onOpenMask={(item) => openInboxItemInMask(item, navigate)}
          onQueue={onInboxQueue}
        />
      ) : null}

      {catalogSpaces.length > 0 ? (
        <LaunchpadBoard
          catalogSpaces={catalogSpaces}
          spaceId={activeSpaceId}
          onSpaceIdChange={setSpaceId}
          pageBySpace={pageBySpace}
          onPageBySpaceChange={setPageBySpace}
          rankedTileIds={rankedTileIds}
        />
      ) : null}
    </div>
  )
}
