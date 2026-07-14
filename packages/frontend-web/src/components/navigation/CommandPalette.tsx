/**
 * Command Palette - Herzstueck der modernen Navigation
 * Ersetzt Ribbon-Overload durch beschreibbare Aktionen.
 */

import { useCallback, useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { useNavigate } from '@/app/routing/typed-router'
import { Command as CommandIcon, HelpCircle, Search, Zap } from 'lucide-react'
import { VoiceBar } from '@/components/mask-builder/renderers/VoiceBar'
import { globalSearch, QUICK_ACTIONS } from '@/lib/api/global-search'
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command'
import { createMCPMetadata } from '@/design/mcp-schemas/component-metadata'
import { useActionDispatch } from '@/features/ki-usability/context/ActionDispatchHooks'
import { useFeature } from '@/hooks/useFeature'
import {
  fetchMaskRegistry,
  fetchOmniboxCatalog,
  recordOmniboxSignal,
  sha256Hex,
} from '@/lib/api/mask-registry'
import { useNavigationShortcuts } from '@/app/navigation/nav-runtime'
import { compileIntents, normalize } from '@/lib/omnibox/intent-compiler'
import { detectCommandIntent } from '@/lib/omnibox/command-compiler'
import type { CommandDraftIntent, FormPrefillIntent, NavigateIntent } from '@/lib/omnibox/types'
import { createDefaultSttProvider } from '@/lib/voice/stt-provider'
import { compileVoiceNavigation } from '@/lib/voice/voice-navigation'
import {
  buildPaletteCommands,
  enrichCommandsWithOmniboxCatalog,
  type PaletteCommand,
} from './command-palette-model'

interface CommandPaletteProps {
  open: boolean
  onOpenChange: (_open: boolean) => void
}

export const commandPaletteMCP = createMCPMetadata('CommandPalette', 'navigation', {
  accessibility: {
    role: 'dialog',
    ariaLabel: 'Command palette for quick navigation',
    keyboardShortcuts: ['Ctrl+K', 'Cmd+K', 'Escape'],
    focusable: true,
  },
  intent: {
    purpose: 'Quick access to all system functions via search',
    userActions: ['search', 'select', 'navigate'],
    businessDomain: 'core',
  },
  mcpHints: {
    autoFillable: true,
    explainable: true,
    testable: true,
    contextAware: true,
  },
})

export function CommandPalette({ open, onOpenChange }: CommandPaletteProps): JSX.Element {
  const agrarEnabled = useFeature('agrar')
  const navigationShortcuts = useNavigationShortcuts()
  const { dispatch } = useActionDispatch()
  const navigate = useNavigate()
  const [search, setSearch] = useState<string>('')
  const [lastVoiceQuery, setLastVoiceQuery] = useState<string | null>(null)
  const voiceProvider = useMemo(() => createDefaultSttProvider(), [])

  const dataSearchQuery = useQuery({
    queryKey: ['global-search', search],
    queryFn: () => globalSearch(search),
    enabled: open && search.trim().length >= 2,
    staleTime: 30_000,
  })

  const maskRegistryQuery = useQuery({
    queryKey: ['ui', 'mask-registry', 'command-palette'],
    queryFn: fetchMaskRegistry,
    enabled: open,
    staleTime: 5 * 60 * 1000,
  })

  // UIX-060: Omnibox-Katalog liefert kuratierte Synonyme + reale Listen-Routen
  // je Maske — angereichert in den Command-Katalog fuer besseres Matching und
  // um bisher nur per Menue erreichbare Masken ueber die Omnibox findbar zu machen.
  const omniboxCatalogQuery = useQuery({
    queryKey: ['ui', 'mask-registry', 'omnibox-catalog'],
    queryFn: fetchOmniboxCatalog,
    enabled: open,
    staleTime: 5 * 60 * 1000,
  })

  const commands = useMemo<PaletteCommand[]>(() => {
    const base = buildPaletteCommands({
      agrarEnabled,
      navigationShortcuts,
      maskRegistry: maskRegistryQuery.data?.masks,
    })
    return enrichCommandsWithOmniboxCatalog(base, omniboxCatalogQuery.data, agrarEnabled)
  }, [agrarEnabled, maskRegistryQuery.data?.masks, navigationShortcuts, omniboxCatalogQuery.data])

  // UIX-060 Omnibox: Mehrwort-Eingaben werden zu Navigations-Plänen mit
  // Filter-Vorschau kompiliert ("Verstanden als") — Enter navigiert nur.
  const intentPlans = useMemo(() => {
    if (search.trim().length < 3) return []
    return compileIntents(search, commands)
  }, [commands, search])

  // UIX-060: Vorschlag annehmen → anonymes Telemetrie-Signal (SHA-256, kein
  // Klartext) fire-and-forget, dann navigieren. Telemetrie darf die Navigation
  // nie blockieren, daher best-effort ohne await im UI-Pfad.
  const acceptIntent = useCallback(
    (plan: NavigateIntent) => {
      const rawScreenId = plan.command.actionParams?.screenId ?? plan.command.actionParams?.maskId
      const matchedScreenId = typeof rawScreenId === 'string' ? rawScreenId : null
      void sha256Hex(normalize(search))
        .then((intentHash) => {
          if (!intentHash) return
          return recordOmniboxSignal({
            intent_hash: intentHash,
            matched_screen_id: matchedScreenId,
            confidence: plan.confidence,
            accepted: true,
          })
        })
        // Telemetrie ist Sekundaerdatum — Fehler duerfen den Nutzerfluss nicht stoeren.
        .catch(() => undefined)
      navigate(plan.routePath)
      onOpenChange(false)
    },
    [navigate, onOpenChange, search],
  )

  const acceptVoiceText = useCallback(
    (text: string) => {
      const normalized = normalize(text)
      setLastVoiceQuery(normalized)
      const plan = compileVoiceNavigation(text, commands)
      if (plan.kind === 'navigate') {
        navigate(plan.routePath)
        onOpenChange(false)
        return
      }
      setSearch(text)
    },
    [commands, navigate, onOpenChange],
  )

  // UIX-070: erkennt in der Eingabe ein Aktions-Verb fuer die benannte Maske und
  // erzeugt — streng nach der Sicherheitsmatrix — einen Command-/Prefill-Plan.
  const commandIntent = useMemo(() => {
    if (search.trim().length < 3 || intentPlans.length === 0) return null
    if (lastVoiceQuery && normalize(search) === lastVoiceQuery) return null
    const catalog = omniboxCatalogQuery.data ?? []
    const tokens = new Set(normalize(search).split(' ').filter(Boolean))
    const navCommand = intentPlans[0].command
    // Command-Erkennung ist unabhaengig vom Navigations-Ranking: der Screen muss
    // per Synonym/Titel benannt sein UND ein Aktions-Verb getroffen werden
    // (Verb + Sicherheitsmatrix entscheidet detectCommandIntent).
    for (const entry of catalog) {
      if (!entry.route || !entry.actions?.length) continue
      const named = [...entry.synonyms, entry.title].some((s) =>
        normalize(s).split(' ').some((w) => w.length >= 3 && tokens.has(w)),
      )
      if (!named) continue
      const detected = detectCommandIntent(search, {
        screenId: entry.screen_id,
        route: entry.route,
        actions: entry.actions,
        navigateCommand: navCommand,
      })
      if (detected && (detected.kind === 'commandDraft' || detected.kind === 'formPrefill')) {
        return detected
      }
    }
    return null
  }, [intentPlans, lastVoiceQuery, omniboxCatalogQuery.data, search])

  const acceptCommandIntent = useCallback(
    (plan: CommandDraftIntent | FormPrefillIntent) => {
      void sha256Hex(normalize(search))
        .then((intentHash) => {
          if (!intentHash) return
          return recordOmniboxSignal({
            intent_hash: intentHash,
            matched_screen_id: plan.screenId,
            confidence: plan.confidence,
            accepted: true,
          })
        })
        .catch(() => undefined)
      // v1: in die Ziel-Maske navigieren; die Aktion wird dort per bestehendem
      // Ritual/Prefill ausgeloest (kein Auto-Submit, kein Gate-Bypass).
      const sep = plan.routePath.includes('?') ? '&' : '?'
      navigate(`${plan.routePath}${sep}omniboxAction=${encodeURIComponent(plan.actionKey ?? '')}`)
      onOpenChange(false)
    },
    [navigate, onOpenChange, search],
  )

  const filteredCommands = useMemo(() => {
    const searchLower = search.trim().toLowerCase()
    if (searchLower.length === 0) {
      return commands
    }
    return commands.filter((cmd) => {
      return (
        cmd.label.toLowerCase().includes(searchLower) ||
        cmd.keywords.some((keyword) => keyword.toLowerCase().includes(searchLower))
      )
    })
  }, [commands, search])

  const groupedCommands = useMemo(() => {
    return filteredCommands.reduce<Record<string, PaletteCommand[]>>((accumulator, cmd) => {
      if (accumulator[cmd.category] === undefined) {
        accumulator[cmd.category] = []
      }
      accumulator[cmd.category].push(cmd)
      return accumulator
    }, {})
  }, [filteredCommands])

  return (
    <CommandDialog
      open={open}
      onOpenChange={onOpenChange}
      aria-label="Command palette"
      data-mcp-component="command-palette"
    >
      <CommandInput
        placeholder="Aktion suchen... (z.B. 'Auftrag', 'Buchung')"
        value={search}
        onValueChange={setSearch}
        autoFocus
      />
      {voiceProvider ? (
        <div className="border-b px-3 py-2">
          <VoiceBar
            provider={voiceProvider}
            target="omnibox"
            onCommit={acceptVoiceText}
            label="Omnibox-Diktat"
          />
        </div>
      ) : null}
      <CommandList className="max-h-[400px]">
        <CommandEmpty>
          {search.trim().length > 0
            ? `Keine Ergebnisse für "${search.trim()}"`
            : 'Keine Aktionen gefunden.'}
          <div className="mt-2 text-xs text-muted-foreground">
            Tipp: Versuche allgemeinere Begriffe wie &quot;Auftrag&quot; oder &quot;Kunde&quot;
          </div>
        </CommandEmpty>

        {commandIntent && (commandIntent.kind === 'commandDraft' || commandIntent.kind === 'formPrefill') && (
          <CommandGroup heading="Aktion vorbereiten">
            <CommandItem
              key={`command:${commandIntent.screenId}:${commandIntent.actionKey}`}
              value={`${search} command:${commandIntent.actionKey}`}
              onSelect={() => acceptCommandIntent(commandIntent)}
              data-mcp-action={`omnibox-command:${commandIntent.actionKey}`}
              data-mcp-intent={commandIntent.kind}
              data-omnibox-command-kind={commandIntent.kind}
              data-omnibox-confidence={commandIntent.confidence.toFixed(2)}
            >
              <Zap className="mr-2 h-4 w-4 text-status-warning" />
              <span>{commandIntent.label}</span>
              <span className="ml-2 rounded border border-border bg-muted px-1.5 text-xs text-muted-foreground group-data-[selected=true]:text-accent-foreground">
                {commandIntent.kind === 'commandDraft' ? 'bestätigen' : 'vorfüllen'}
              </span>
              {commandIntent.kind === 'commandDraft' && commandIntent.missingFields.length > 0 && (
                <span className="ml-2 text-xs text-muted-foreground group-data-[selected=true]:text-accent-foreground">
                  {commandIntent.missingFields.length} Feld(er) offen
                </span>
              )}
            </CommandItem>
          </CommandGroup>
        )}

        {intentPlans.length > 0 && (
          <>
            <CommandGroup heading="Verstanden als">
              {intentPlans.map((plan) => (
                <CommandItem
                  key={`intent:${plan.command.id}`}
                  // value enthält den Suchtext, damit cmdk die Vorschau nie wegfiltert
                  value={`${search} intent:${plan.command.id}`}
                  onSelect={() => acceptIntent(plan)}
                  data-mcp-action={`omnibox-intent:${plan.command.id}`}
                  data-mcp-intent="navigate"
                  data-omnibox-confidence={plan.confidence.toFixed(2)}
                >
                  <Search className="mr-2 h-4 w-4" />
                  <span>{plan.label}</span>
                  {plan.filters.map((f) => (
                    <span
                      key={`${f.key}:${f.value}`}
                      className="ml-2 rounded border border-border bg-muted px-1.5 text-xs text-muted-foreground group-data-[selected=true]:text-accent-foreground"
                    >
                      {f.key === 'q' ? `„${f.label}"` : f.label}
                    </span>
                  ))}
                  {/* Konfidenz-Badge: gedaempft, aber auf der Selected-Row (bernstein) */}
                  {/* lesbar — sonst faellt der Kontrast unter WCAG AA (axe-Gate). */}
                  <span className="ml-auto text-xs text-muted-foreground group-data-[selected=true]:text-accent-foreground">
                    {Math.round(plan.confidence * 100)} %
                  </span>
                </CommandItem>
              ))}
            </CommandGroup>
            <CommandSeparator />
          </>
        )}

        {Object.entries(groupedCommands).map(([category, cmds], idx) => (
          <div key={category}>
            {idx > 0 && <CommandSeparator />}
            <CommandGroup heading={category}>
              {cmds.map((cmd) => {
                const Icon = cmd.icon
                return (
                  <CommandItem
                    key={cmd.id}
                    value={cmd.label}
                    keywords={cmd.keywords}
                    onSelect={() => {
                      void dispatch(cmd.actionId, cmd.actionParams).then((ok) => {
                        if (ok) {
                          onOpenChange(false)
                        }
                      })
                    }}
                    data-mcp-action={cmd.id}
                    data-mcp-intent={cmd.mcp?.intent}
                    data-mcp-domain={cmd.mcp?.businessDomain}
                  >
                    <Icon className="mr-2 h-4 w-4" />
                    <span>{cmd.label}</span>
                    {cmd.hint && (
                      <span className="ml-2 text-xs text-muted-foreground">{cmd.hint}</span>
                    )}
                    {cmd.shortcut && (
                      <kbd className="ml-auto rounded bg-muted px-1 text-xs text-muted-foreground">
                        {cmd.shortcut}
                      </kbd>
                    )}
                    {cmd.mcp?.requiredScopes && !cmd.shortcut && (
                      <span className="ml-auto text-xs text-muted-foreground">{cmd.mcp.requiredScopes[0]}</span>
                    )}
                  </CommandItem>
                )
              })}
            </CommandGroup>
          </div>
        ))}

        {/* Quick Actions — filtered by search */}
        {(() => {
          const searchLower = search.trim().toLowerCase()
          const matchingActions = QUICK_ACTIONS.filter(
            (a) =>
              searchLower.length === 0 ||
              a.label.toLowerCase().includes(searchLower) ||
              a.keywords.some((k) => k.includes(searchLower)),
          )
          if (matchingActions.length === 0) return null
          return (
            <>
              <CommandSeparator />
              <CommandGroup heading="Schnellaktionen">
                {matchingActions.map((action) => (
                  <CommandItem
                    key={action.id}
                    value={action.label}
                    keywords={action.keywords}
                    onSelect={() => {
                      navigate(action.path)
                      onOpenChange(false)
                    }}
                  >
                    <Zap className="mr-2 h-4 w-4 text-status-warning" aria-hidden="true" />
                    {action.label}
                  </CommandItem>
                ))}
              </CommandGroup>
            </>
          )
        })()}

        {/* Data search results */}
        {dataSearchQuery.data && dataSearchQuery.data.results.length > 0 && (
          <>
            <CommandSeparator />
            <CommandGroup heading="Datensätze">
              {dataSearchQuery.data.results.map((result) => (
                <CommandItem
                  key={`${result.type}-${result.id}`}
                  value={result.label}
                  onSelect={() => {
                    navigate(result.path)
                    onOpenChange(false)
                  }}
                >
                  <Search className="mr-2 h-4 w-4 text-muted-foreground" aria-hidden="true" />
                  <span>{result.label}</span>
                  {result.sublabel && (
                    <span className="ml-2 text-xs text-muted-foreground">{result.sublabel}</span>
                  )}
                </CommandItem>
              ))}
            </CommandGroup>
          </>
        )}

        {(search.toLowerCase().includes('ai') || search.toLowerCase().includes('help') || search.toLowerCase().includes('hilfe')) && (
          <>
            <CommandSeparator />
            <CommandGroup heading="Ask VALEO">
              <CommandItem
                value="Ask VALEO"
                onSelect={() => {
                  void dispatch('ai-ask-valeo', { eventName: 'open-ask-valeo' }).then((ok) => {
                    if (ok) {
                      onOpenChange(false)
                    }
                  })
                }}
              >
                <HelpCircle className="mr-2 h-4 w-4" />
                Ask VALEO öffnen
              </CommandItem>
            </CommandGroup>
          </>
        )}
      </CommandList>

      {/* Tastenkürzel-Hinweis */}
      <div className="flex items-center justify-end border-t px-3 py-2 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <CommandIcon className="h-3 w-3" />
          <span>K</span>
          <span className="mx-1 opacity-50">/</span>
          <kbd className="rounded bg-muted px-1 py-0.5">Ctrl</kbd>
          <span>+</span>
          <kbd className="rounded bg-muted px-1 py-0.5">K</kbd>
          <span className="ml-1">schließen</span>
        </span>
      </div>
    </CommandDialog>
  )
}
