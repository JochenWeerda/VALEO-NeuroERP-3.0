/**
 * Command Palette - Herzstueck der modernen Navigation
 * Ersetzt Ribbon-Overload durch beschreibbare Aktionen.
 */

import { useMemo, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { HelpCircle } from 'lucide-react'
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
import { fetchMaskRegistry } from '@/lib/api/mask-registry'
import { useNavigationShortcuts } from '@/app/navigation/nav-runtime'
import { buildPaletteCommands, type PaletteCommand } from './command-palette-model'

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
  const [search, setSearch] = useState<string>('')

  const maskRegistryQuery = useQuery({
    queryKey: ['ui', 'mask-registry', 'command-palette'],
    queryFn: fetchMaskRegistry,
    enabled: open,
    staleTime: 5 * 60 * 1000,
  })

  const commands = useMemo<PaletteCommand[]>(() => {
    return buildPaletteCommands({
      agrarEnabled,
      navigationShortcuts,
      maskRegistry: maskRegistryQuery.data?.masks,
    })
  }, [agrarEnabled, maskRegistryQuery.data?.masks, navigationShortcuts])

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
      />
      <CommandList>
        <CommandEmpty>
          Keine Aktionen gefunden.
          <div className="mt-2 text-xs text-muted-foreground">
            Tipp: Versuche allgemeinere Begriffe wie &quot;Auftrag&quot; oder &quot;Kunde&quot;
          </div>
        </CommandEmpty>

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
                    {cmd.mcp?.requiredScopes && (
                      <span className="ml-2 text-xs text-muted-foreground">{cmd.mcp.requiredScopes[0]}</span>
                    )}
                  </CommandItem>
                )
              })}
            </CommandGroup>
          </div>
        ))}

        {(search.toLowerCase().includes('ai') || search.toLowerCase().includes('help')) && (
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
                Ask VALEO oeffnen
              </CommandItem>
            </CommandGroup>
          </>
        )}
      </CommandList>
    </CommandDialog>
  )
}
