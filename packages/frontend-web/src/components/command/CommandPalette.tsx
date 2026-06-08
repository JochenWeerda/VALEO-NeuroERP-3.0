/**
 * Command Palette (Cmd+K / Ctrl+K)
 * Quick navigation and actions for VALEO NeuroERP
 */

import { useMemo, useState, useEffect } from 'react'
import { useNavigate } from '@/app/routing/typed-router'
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command'
import { ACTION_SHORTCUTS } from '@/app/navigation/action-shortcuts'
import { AI_SHORTCUTS } from '@/app/navigation/ai-shortcuts'
import { useNavigationShortcuts } from '@/app/navigation/nav-runtime'

type CommandAction = {
  id: string
  label: string
  icon: JSX.Element
  action: () => void
  category: 'navigation' | 'actions' | 'ai'
  keywords?: string[]
}

export function CommandPalette() {
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)
  const navigationShortcuts = useNavigationShortcuts()

  // Keyboard shortcut: Cmd+K / Ctrl+K
  useEffect(() => {
    const down = (e: KeyboardEvent) => {
      if (e.key === 'k' && (e.metaKey || e.ctrlKey)) {
        e.preventDefault()
        setOpen((open) => !open)
      }
    }

    document.addEventListener('keydown', down)
    return () => document.removeEventListener('keydown', down)
  }, [])

  const navigationCommands = useMemo<CommandAction[]>(
    () =>
      navigationShortcuts.map((shortcut) => {
        const Icon = shortcut.icon
        return {
          id: `nav-${shortcut.id}`,
          label: shortcut.label,
          icon: <Icon className="h-4 w-4" />,
          action: () => navigate(shortcut.path),
          category: 'navigation' as const,
          keywords: shortcut.keywords,
        }
      }),
    [navigate, navigationShortcuts],
  )

  const actionCommands = useMemo<CommandAction[]>(
    () =>
      ACTION_SHORTCUTS.map((shortcut) => {
        const Icon = shortcut.icon
        return {
          id: shortcut.id,
          label: shortcut.label,
          icon: <Icon className="h-4 w-4" />,
          action: () => navigate(shortcut.path),
          category: 'actions' as const,
          keywords: shortcut.keywords,
        }
      }),
    [navigate],
  )

  const aiCommands = useMemo<CommandAction[]>(
    () =>
      AI_SHORTCUTS.map((shortcut) => {
        const Icon = shortcut.icon
        const base = {
          id: shortcut.id,
          label: shortcut.label,
          icon: <Icon className="h-4 w-4" />,
          category: 'ai' as const,
          keywords: shortcut.keywords,
        }
        if (shortcut.type === 'navigate') {
          return {
            ...base,
            action: () => navigate(shortcut.path),
          }
        }
        return {
          ...base,
          action: () =>
            window.dispatchEvent(
              new CustomEvent(shortcut.eventName, { detail: shortcut.eventPayload }),
            ),
        }
      }),
    [navigate],
  )

  const commands: CommandAction[] = [...navigationCommands, ...actionCommands, ...aiCommands]

  const handleSelect = (command: CommandAction) => {
    command.action()
    setOpen(false)
  }

  return (
    <CommandDialog open={open} onOpenChange={setOpen}>
      <CommandInput placeholder="Suche nach Seiten, Aktionen oder frage VALEO..." />
      <CommandList>
        <CommandEmpty>Keine Ergebnisse gefunden.</CommandEmpty>
        
        <CommandGroup heading="Navigation">
          {commands
            .filter((cmd) => cmd.category === 'navigation')
            .map((cmd) => (
              <CommandItem
                key={cmd.id}
                onSelect={() => handleSelect(cmd)}
                className="gap-2"
              >
                {cmd.icon}
                <span>{cmd.label}</span>
              </CommandItem>
            ))}
        </CommandGroup>
        
        <CommandSeparator />
        
        <CommandGroup heading="Aktionen">
          {commands
            .filter((cmd) => cmd.category === 'actions')
            .map((cmd) => (
              <CommandItem
                key={cmd.id}
                onSelect={() => handleSelect(cmd)}
                className="gap-2"
              >
                {cmd.icon}
                <span>{cmd.label}</span>
              </CommandItem>
            ))}
        </CommandGroup>
        
        <CommandSeparator />
        
        <CommandGroup heading="KI-Funktionen">
          {commands
            .filter((cmd) => cmd.category === 'ai')
            .map((cmd) => (
              <CommandItem
                key={cmd.id}
                onSelect={() => handleSelect(cmd)}
                className="gap-2"
              >
                {cmd.icon}
                <span>{cmd.label}</span>
              </CommandItem>
            ))}
        </CommandGroup>
      </CommandList>
    </CommandDialog>
  )
}

