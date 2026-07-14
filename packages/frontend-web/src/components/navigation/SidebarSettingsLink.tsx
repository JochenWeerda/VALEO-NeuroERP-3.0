import { NavLink } from '@/app/routing/typed-router'
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
          'flex min-h-11 items-center gap-3 rounded-[8px] px-3 py-2 text-sm font-medium transition-colors',
          'hover:bg-(--sidebar-item-hover-bg) hover:text-white',
          isActive ? 'bg-(--sidebar-item-active-bg) text-white' : 'text-[hsl(210,20%,75%)]',
        )
      }
      title={collapsed ? 'Einstellungen' : undefined}
    >
      <Settings className="h-5 w-5" />
      {!collapsed && <span>Einstellungen</span>}
    </NavLink>
  )
}
