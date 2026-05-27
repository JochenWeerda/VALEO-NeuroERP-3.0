import { Package, Search, ShieldCheck, ShoppingCart, Users, Zap } from 'lucide-react'
import type { AiShortcut } from '@/app/navigation/types'
import { resolveRoutePathFromModule } from '@/app/navigation/route-paths'

export const AI_SHORTCUTS: AiShortcut[] = [
  {
    id: 'ai-ask-valeo',
    label: 'Ask VALEO (AI-Copilot)',
    icon: Zap,
    type: 'event',
    eventName: 'open-ask-valeo',
    keywords: ['ai', 'copilot', 'assistant'],
  },
  {
    id: 'ai-search',
    label: 'Semantische Suche',
    icon: Search,
    type: 'event',
    eventName: 'open-semantic-search',
    keywords: ['search', 'semantic'],
  },
  {
    id: 'ai-compliance',
    label: 'Compliance-Check durchfuehren',
    icon: ShieldCheck,
    type: 'navigate',
    path: resolveRoutePathFromModule('@/pages/admin/compliance-dashboard', 'admin/compliance'),
    keywords: ['compliance', 'audit'],
  },
  {
    id: 'ai-voice-lager',
    label: 'Lager - Voice-Befehl',
    icon: Package,
    type: 'event',
    eventName: 'voice-intent',
    eventPayload: { domain: 'lager' },
    keywords: ['lager', 'wareneingang', 'inventur', 'umlagerung', 'voice'],
  },
  {
    id: 'ai-voice-einkauf',
    label: 'Einkauf - Voice-Befehl',
    icon: ShoppingCart,
    type: 'event',
    eventName: 'voice-intent',
    eventPayload: { domain: 'einkauf' },
    keywords: ['einkauf', 'bestellung', 'lieferant', 'voice', 'beschaffung'],
  },
  {
    id: 'ai-voice-hr',
    label: 'Personal - Voice-Befehl',
    icon: Users,
    type: 'event',
    eventName: 'voice-intent',
    eventPayload: { domain: 'hr' },
    keywords: ['personal', 'hr', 'mitarbeiter', 'abwesenheit', 'lohnlauf', 'voice'],
  },
]
