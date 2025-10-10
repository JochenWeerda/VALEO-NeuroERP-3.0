import { Outlet, NavLink } from 'react-router-dom'
import { Menu } from 'lucide-react'

const nav = [
  { to: '/contracts', label: 'Contracts' },
  { to: '/pricing', label: 'Pricing' },
  { to: '/inventory', label: 'Inventory' },
  { to: '/weighing', label: 'Weighing' },
  { to: '/sales', label: 'Sales' },
  { to: '/document', label: 'Document' },
]

export default function AppLayout() {
  return (
    <div className="min-h-screen bg-background text-foreground">
      <header className="border-b">
        <div className="container flex items-center gap-3 py-3">
          <Menu className="h-5 w-5 opacity-60" />
          <h1 className="text-lg font-semibold">VALEO NeuroERP</h1>
          <nav className="ml-auto flex gap-4">
            {nav.map((n) => (
              <NavLink
                key={n.to}
                to={n.to}
                className={({ isActive }) =>
                  `text-sm ${isActive ? 'font-semibold underline' : 'opacity-80 hover:opacity-100'}`
                }
              >
                {n.label}
              </NavLink>
            ))}
          </nav>
        </div>
      </header>
      <main className="container py-6">
        <Outlet />
      </main>
    </div>
  )
}