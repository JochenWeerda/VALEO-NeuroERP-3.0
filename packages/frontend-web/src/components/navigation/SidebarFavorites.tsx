import { NavLink } from 'react-router-dom'
import { clsx } from 'clsx'
import type { NavItem } from '@/app/navigation/types'

type SidebarFavorite = {
  item: NavItem
  path: string
}

type SidebarFavoritesProps = {
  favorites: SidebarFavorite[]
  onNavigate?: () => void
}

export default function SidebarFavorites({ favorites, onNavigate }: SidebarFavoritesProps): JSX.Element | null {
  if (favorites.length === 0) {
    return null
  }

  return (
    <div className="mb-3 rounded-[8px] border border-[var(--sidebar-border)] bg-[hsl(215,30%,18%)] p-2">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-[hsl(210,20%,70%)]">Favoriten</p>
      <div className="space-y-1">
        {favorites.map((favorite) => {
          const FavoriteIcon = favorite.item.icon
          return (
            <NavLink
              key={`fav-${favorite.item.id}`}
              to={favorite.path}
              onClick={onNavigate}
              className={({ isActive }) =>
                clsx(
                  'flex min-h-11 items-center gap-2 rounded-[8px] px-2 py-1.5 text-xs font-medium transition-colors',
                  'hover:bg-[var(--sidebar-item-hover-bg)] hover:text-white',
                  isActive ? 'bg-[var(--sidebar-item-active-bg)] text-white' : 'text-[hsl(210,20%,75%)]',
                )
              }
            >
              <FavoriteIcon className="h-3.5 w-3.5 flex-shrink-0" />
              <span className="truncate">{favorite.item.label}</span>
            </NavLink>
          )
        })}
      </div>
    </div>
  )
}
