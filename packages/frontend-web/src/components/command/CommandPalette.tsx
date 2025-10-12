/**
 * Command Palette (Cmd+K / Ctrl+K)
 * Quick navigation and actions for VALEO NeuroERP
 */

import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import {
  CommandDialog,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
  CommandSeparator,
} from '@/components/ui/command'
import {
  FileText, Users, Package, TrendingUp, Settings, 
  Search, Plus, Calculator, Shield, Zap
} from 'lucide-react'

type CommandAction = {
  id: string
  label: string
  icon: JSX.Element
  action: () => void
  category: 'navigation' | 'actions' | 'ai'
  keywords?: string[]
}

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export function CommandPalette() {
  const navigate = useNavigate()
  const [open, setOpen] = useState(false)

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

  // Define commands
  const commands: CommandAction[] = [
    // Navigation
    {
      id: 'nav-kunden',
      label: 'Kunden-Liste',
      icon: <Users className="h-4 w-4" />,
      action: () => navigate('/verkauf/kunden-liste'),
      category: 'navigation',
      keywords: ['kunden', 'crm', 'customer']
    },
    {
      id: 'nav-artikel',
      label: 'Artikel-Stammdaten',
      icon: <Package className="h-4 w-4" />,
      action: () => navigate('/artikel/liste'),
      category: 'navigation',
      keywords: ['artikel', 'products', 'lager']
    },
    {
      id: 'nav-rechnungen',
      label: 'Rechnungen',
      icon: <FileText className="h-4 w-4" />,
      action: () => navigate('/fibu/rechnungen'),
      category: 'navigation',
      keywords: ['rechnung', 'invoice', 'finance']
    },
    {
      id: 'nav-dashboard',
      label: 'Verkaufs-Dashboard',
      icon: <TrendingUp className="h-4 w-4" />,
      action: () => navigate('/dashboard/sales-dashboard'),
      category: 'navigation',
      keywords: ['dashboard', 'kpi', 'analytics']
    },
    {
      id: 'nav-bestand',
      label: 'Bestandsübersicht',
      icon: <Package className="h-4 w-4" />,
      action: () => navigate('/lager/bestandsuebersicht'),
      category: 'navigation',
      keywords: ['lager', 'bestand', 'inventory']
    },
    {
      id: 'nav-einstellungen',
      label: 'System-Einstellungen',
      icon: <Settings className="h-4 w-4" />,
      action: () => navigate('/einstellungen/system'),
      category: 'navigation',
      keywords: ['settings', 'config', 'admin']
    },

    // Actions
    {
      id: 'action-new-customer',
      label: 'Neuer Kunde anlegen',
      icon: <Plus className="h-4 w-4" />,
      action: () => navigate('/verkauf/kunde/neu'),
      category: 'actions',
      keywords: ['neu', 'create', 'kunde', 'customer']
    },
    {
      id: 'action-new-invoice',
      label: 'Neue Rechnung erstellen',
      icon: <Plus className="h-4 w-4" />,
      action: () => navigate('/fibu/rechnung/neu'),
      category: 'actions',
      keywords: ['neu', 'create', 'rechnung', 'invoice']
    },
    {
      id: 'action-bestellvorschlag',
      label: 'Bestellvorschlag generieren',
      icon: <Calculator className="h-4 w-4" />,
      action: () => navigate('/workflows/trigger'),
      category: 'actions',
      keywords: ['bestellung', 'order', 'ai', 'workflow']
    },

    // AI Features
    {
      id: 'ai-ask-valeo',
      label: 'Ask VALEO (AI-Copilot)',
      icon: <Zap className="h-4 w-4" />,
      action: () => {
        // Trigger Ask VALEO Dialog
        window.dispatchEvent(new CustomEvent('open-ask-valeo'))
      },
      category: 'ai',
      keywords: ['ai', 'copilot', 'assistant', 'help']
    },
    {
      id: 'ai-search',
      label: 'Semantische Suche',
      icon: <Search className="h-4 w-4" />,
      action: () => {
        // Trigger Semantic Search Dialog
        window.dispatchEvent(new CustomEvent('open-semantic-search'))
      },
      category: 'ai',
      keywords: ['search', 'find', 'semantic', 'rag']
    },
    {
      id: 'ai-compliance',
      label: 'Compliance-Check durchführen',
      icon: <Shield className="h-4 w-4" />,
      action: () => navigate('/admin/compliance'),
      category: 'ai',
      keywords: ['compliance', 'audit', 'check']
    },
  ]

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

