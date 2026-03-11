import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'
import { Settings } from 'lucide-react'

type SidebarSettingsLinkProps = {
  collapsed: boolean
  path: string
}

export default function SidebarSettingsLink({ collapsed, path }: SidebarSettingsLinkProps): JSX.Element {
  return (
    <NavLink
      to={path}
      className={({ isActive }) =>
        clsx(
          'flex items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors',
          'hover:bg-accent hover:text-accent-foreground',
          isActive ? 'bg-accent' : 'text-muted-foreground',
        )
      }
      title={collapsed ? 'Einstellungen' : undefined}
    >
      <Settings className="h-5 w-5" />
      {!collapsed && <span>Einstellungen</span>}
    </NavLink>
  )
}
