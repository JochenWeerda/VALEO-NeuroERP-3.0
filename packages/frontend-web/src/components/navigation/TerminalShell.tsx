import { type ReactNode, Suspense, lazy } from 'react'
import { Link, NavLink } from '@/app/routing/react-router-compat'
import { Home, Package, ClipboardList, BarChart2, LogOut } from 'lucide-react'
import { clsx } from 'clsx'

const BarcodeScanner = lazy(() =>
  import('@/components/ui/barcode-scanner').then((m) => ({ default: m.BarcodeScanner })),
)

interface TerminalShellProps {
  children: ReactNode
  /** Module title shown in header */
  title?: string
}

const NAV_ITEMS = [
  { to: '/lager', label: 'Start', icon: Home },
  { to: '/lager/wareneingang', label: 'Eingang', icon: Package },
  { to: '/lager/inventur', label: 'Inventur', icon: ClipboardList },
  { to: '/lager/auswertungen', label: 'Berichte', icon: BarChart2 },
]

/**
 * Simplified shell for warehouse terminal and scanner devices.
 * Features: 56px touch targets, bottom navigation, high contrast,
 * no complex sidebar — optimised for gloved hands and bright environments.
 */
export function TerminalShell({ children, title = 'Lager' }: TerminalShellProps): JSX.Element {
  return (
    <div className="flex h-screen flex-col bg-background" data-mcp-component="terminal-shell">
      {/* Compact top header */}
      <header
        className="flex h-14 items-center justify-between border-b bg-[hsl(215,30%,14%)] px-4 text-white"
        role="banner"
      >
        <Link to="/lager" className="flex items-center gap-2 focus:outline-none focus:ring-2 focus:ring-white/30 rounded">
          <img src="/branding/valeo-erp-logo.png" alt="VALEO ERP" className="h-8 w-8 rounded object-cover" />
          <span className="text-sm font-semibold">{title}</span>
        </Link>
        <Link
          to="/"
          className="flex items-center gap-1 rounded px-2 py-1 text-xs text-white/70 hover:text-white focus:outline-none focus:ring-2 focus:ring-white/30"
          aria-label="Zurück zur Hauptanwendung"
        >
          <LogOut className="h-4 w-4" aria-hidden="true" />
          <span className="hidden sm:inline">Zurück</span>
        </Link>
      </header>

      {/* Main content area */}
      <main
        className="flex-1 overflow-y-auto p-4"
        role="main"
        aria-label="Lager-Terminal Inhalt"
        id="terminal-main-content"
      >
        {children}
      </main>

      {/* Bottom navigation — 56px touch targets (WCAG 2.5.5 for terminal use) */}
      <nav
        className="flex border-t bg-[hsl(215,30%,14%)]"
        role="navigation"
        aria-label="Lager-Navigation"
      >
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === '/lager'}
            className={({ isActive }) =>
              clsx(
                'flex flex-1 flex-col items-center justify-center gap-1 py-3',
                'text-xs font-medium transition-colors',
                'focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-inset focus-visible:ring-white/30',
                'min-h-[56px]',
                isActive
                  ? 'bg-primary/20 text-white'
                  : 'text-white/60 hover:bg-[hsl(215,30%,20%)] hover:text-white',
              )
            }
          >
            <Icon className="h-5 w-5" aria-hidden="true" />
            <span>{label}</span>
          </NavLink>
        ))}
      </nav>
    </div>
  )
}
