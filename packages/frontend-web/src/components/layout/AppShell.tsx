import { type ComponentType, type FormEvent, type ReactNode, type SVGProps, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { NavLink } from 'react-router-dom'
import {
  BarChart3,
  FileText,
  Loader2,
  Menu,
  Package,
  Receipt,
  Search,
  Truck,
  X,
} from 'lucide-react'

import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { cn } from '@/lib/utils'
import { toast } from '@/hooks/use-toast'
import {
  type GlobalSearchSummary,
  type SearchDomainKey,
  performGlobalSearch,
} from '@/features/global-search'
import { GlobalStatusIndicator } from './GlobalStatusIndicator'

interface AppShellProps {
  children: ReactNode
}

interface NavigationItem {
  label: string
  to: string
  icon: ComponentType<SVGProps<SVGSVGElement>>
  end?: boolean
}

const navigation: NavigationItem[] = [
  { label: 'Dashboard', to: '/', icon: BarChart3, end: true },
  { label: 'Vertraege', to: '/contracts', icon: FileText },
  { label: 'Bestand', to: '/inventory', icon: Package },
  { label: 'Wiegen', to: '/weighing', icon: Truck },
  { label: 'Sales', to: '/sales', icon: Receipt },
]

const tenantLabel = import.meta.env.VITE_TENANT_ID ?? 'UNASSIGNED'

const domainLabels: Record<SearchDomainKey, string> = {
  contracts: 'Vertraege',
  inventoryLots: 'Lagerlose',
  weighingTickets: 'Wiegetickets',
  salesOrders: 'Auftraege',
  salesInvoices: 'Rechnungen',
}

const SEARCH_DOMAINS: SearchDomainKey[] = [
  'contracts',
  'inventoryLots',
  'weighingTickets',
  'salesOrders',
  'salesInvoices',
]

const numberFormatter = new Intl.NumberFormat('de-DE')

function GlobalSearch(): ReactNode {
  const [term, setTerm] = useState<string>('')
  const [summary, setSummary] = useState<GlobalSearchSummary | null>(null)

  const searchMutation = useMutation({
    mutationFn: performGlobalSearch,
    onMutate: () => {
      setSummary(null)
    },
    onSuccess: (result) => {
      setSummary(result)

      const totalMatches = SEARCH_DOMAINS.reduce<number>(
        (aggregate, key) => aggregate + result.totals[key],
        0
      )
      const hasMatches = totalMatches > 0

      const descriptionParts = SEARCH_DOMAINS.map((key) =>
        `${domainLabels[key]}: ${numberFormatter.format(result.totals[key])}`
      )

      toast({
        title: hasMatches ? `Suche abgeschlossen (${totalMatches})` : 'Keine Treffer gefunden',
        description: descriptionParts.join(' | '),
      })

      const failedDomains = SEARCH_DOMAINS.reduce<string[]>((accumulator, key) => {
        const message = result.errors[key]
        if (message !== undefined && message !== null && message !== '') {
          accumulator.push(`${domainLabels[key]}: ${message}`)
        }
        return accumulator
      }, [])

      if (failedDomains.length > 0) {
        toast({
          variant: 'destructive',
          title: 'Teilweise fehlgeschlagen',
          description: failedDomains.join(' | '),
        })
      }

      setTerm('')
    },
    onError: (error: unknown) => {
      const message = error instanceof Error ? error.message : 'Unbekannter Fehler'
      toast({
        variant: 'destructive',
        title: 'Suche fehlgeschlagen',
        description: message,
      })
    },
  })

  const handleSubmit = async (event: FormEvent<HTMLFormElement>): Promise<void> => {
    event.preventDefault()
    const trimmed = term.trim()

    if (trimmed.length === 0) {
      toast({
        title: 'Suche',
        description: 'Bitte einen Suchbegriff angeben.',
      })
      return
    }

    await searchMutation.mutateAsync(trimmed)
  }

  const isSearching = searchMutation.isPending

  const domainTotals = SEARCH_DOMAINS.map((key) => ({
    key,
    label: domainLabels[key],
    count: summary?.totals[key] ?? 0,
  }))

  const domainErrors = SEARCH_DOMAINS.reduce<
    Array<{ key: SearchDomainKey; label: string; message: string }>
  >((accumulator, key) => {
    const message = summary?.errors[key]
    if (message !== undefined && message !== null && message !== '') {
      accumulator.push({ key, label: domainLabels[key], message })
    }
    return accumulator
  }, [])

  return (
    <div className="relative w-full max-w-xl">
      <form
        onSubmit={handleSubmit}
        className="flex w-full items-center gap-2"
        role="search"
        aria-label="Globale Suche"
      >
        <div className="relative flex-1">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={term}
            onChange={(event) => setTerm(event.target.value)}
            onFocus={() => setSummary(null)}
            placeholder="Global suchen (Beta)"
            className="pl-9"
            aria-label="Suchbegriff"
            disabled={isSearching}
          />
        </div>
        <Button type="submit" variant="secondary" disabled={isSearching}>
          {isSearching ? (
            <>
              <Loader2 aria-hidden className="mr-2 h-4 w-4 animate-spin" />
              Suche...
            </>
          ) : (
            'Suchen'
          )}
        </Button>
      </form>

      {summary !== null ? (
        <div className="absolute left-0 right-0 top-[calc(100%+0.75rem)] z-40 rounded-2xl border border-slate-200 bg-white p-4 shadow-xl">
          <div className="flex items-start justify-between gap-4">
            <div>
              <p className="text-sm font-semibold text-slate-700">
                Ergebnisse fuer "{summary.term}"
              </p>
              <p className="text-xs text-slate-400">
                Dauer {numberFormatter.format(summary.durationMs)} ms
              </p>
            </div>
            <Button
              type="button"
              variant="ghost"
              size="sm"
              onClick={() => setSummary(null)}
            >
              Schliessen
            </Button>
          </div>

          <dl className="mt-4 grid grid-cols-1 gap-2 sm:grid-cols-2">
            {domainTotals.map(({ key, label, count }) => (
              <div
                key={key}
                className="flex items-center justify-between rounded-xl bg-slate-50 px-3 py-2 text-sm"
              >
                <dt className="text-slate-500">{label}</dt>
                <dd className="font-semibold text-slate-900">
                  {numberFormatter.format(count)}
                </dd>
              </div>
            ))}
          </dl>

          {domainErrors.length > 0 ? (
            <div className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-3 py-2 text-xs text-rose-600">
              <p className="font-semibold">Fehler bei Domain-Abfragen</p>
              <ul className="mt-2 space-y-1">
                {domainErrors.map(({ key, label, message }) => (
                  <li key={key} className="leading-snug">
                    <span className="font-medium">{label}:</span> {message}
                  </li>
                ))}
              </ul>
            </div>
          ) : null}
        </div>
      ) : null}
    </div>
  )
}

export default function AppShell({ children }: AppShellProps): ReactNode {
  const [sidebarOpen, setSidebarOpen] = useState<boolean>(false)

  const closeSidebar = (): void => {
    setSidebarOpen(false)
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-white focus:px-4 focus:py-2 focus:text-sm focus:shadow-lg"
      >
        Zum Inhalt springen
      </a>

      <div className="lg:hidden" aria-hidden={!sidebarOpen}>
        <div
          className={cn(
            'fixed inset-0 z-40 bg-slate-900/60 transition-opacity',
            sidebarOpen ? 'pointer-events-auto opacity-100' : 'pointer-events-none opacity-0'
          )}
          onClick={closeSidebar}
        />
        <nav
          className={cn(
            'fixed inset-y-0 left-0 z-50 flex w-72 max-w-full flex-col bg-white shadow-xl transition-transform duration-200',
            sidebarOpen ? 'translate-x-0' : '-translate-x-full'
          )}
          aria-label="Hauptnavigation mobil"
        >
          <div className="flex items-center justify-between border-b border-slate-200 px-4 py-4">
            <div>
              <p className="text-sm font-medium text-slate-500">Tenant</p>
              <p className="text-base font-semibold text-slate-900">{tenantLabel}</p>
            </div>
            <Button
              variant="ghost"
              size="icon"
              onClick={closeSidebar}
              aria-label="Navigation schliessen"
            >
              <X className="h-5 w-5" />
            </Button>
          </div>
          <div className="flex-1 overflow-y-auto px-4 py-6">
            <ul className="space-y-2">
              {navigation.map((item) => (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    end={item.end}
                    className={({ isActive }): string =>
                      cn(
                        'flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-primary/10 text-primary'
                          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                      )
                    }
                    onClick={closeSidebar}
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </div>
        </nav>
      </div>

      <aside
        className="hidden lg:fixed lg:inset-y-0 lg:flex lg:w-72 lg:flex-col lg:border-r lg:border-slate-200 lg:bg-white lg:shadow-sm"
        aria-label="Hauptnavigation"
      >
        <div className="flex h-20 flex-shrink-0 items-center border-b border-slate-200 px-6">
          <div>
            <p className="text-xs font-semibold uppercase tracking-wider text-primary">Valero NeuroERP</p>
            <p className="text-sm text-slate-500">Tenant {tenantLabel}</p>
          </div>
        </div>
        <div className="flex flex-1 flex-col justify-between px-4 py-6">
          <nav>
            <ul className="space-y-1">
              {navigation.map((item) => (
                <li key={item.to}>
                  <NavLink
                    to={item.to}
                    end={item.end}
                    className={({ isActive }): string =>
                      cn(
                        'flex items-center gap-3 rounded-xl px-3 py-2 text-sm font-medium transition-colors',
                        isActive
                          ? 'bg-primary/10 text-primary'
                          : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
                      )
                    }
                  >
                    <item.icon className="h-4 w-4" />
                    <span>{item.label}</span>
                  </NavLink>
                </li>
              ))}
            </ul>
          </nav>
          <div className="mt-8 rounded-xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500 shadow-inner">
            <p className="font-semibold text-slate-700">Support</p>
            <p>Bei Fragen bitte das Ops-Team informieren.</p>
          </div>
        </div>
      </aside>

      <div className="lg:pl-72">
        <header className="sticky top-0 z-30 flex h-20 items-center border-b border-slate-200 bg-white/80 backdrop-blur">
          <div className="flex flex-1 items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
            <div className="flex items-center gap-3">
              <Button
                variant="ghost"
                size="icon"
                className="lg:hidden"
                onClick={() => setSidebarOpen(true)}
                aria-label="Navigation oeffnen"
              >
                <Menu className="h-5 w-5" />
              </Button>
              <GlobalSearch />
            </div>
            <div className="flex items-center gap-4">
              <GlobalStatusIndicator />
              <div className="flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1">
                <span className="text-xs font-semibold uppercase text-slate-500">Tenant</span>
                <span className="text-sm font-medium text-slate-900">{tenantLabel}</span>
              </div>
              <Button variant="outline" size="sm">
                Einstellungen
              </Button>
            </div>
          </div>
        </header>

        <main id="main-content" className="min-h-[calc(100vh-5rem)] bg-transparent">
          <div className="mx-auto w-full max-w-7xl px-4 py-8 sm:px-6 lg:px-10">
            {children}
          </div>
        </main>
      </div>
    </div>
  )
}
