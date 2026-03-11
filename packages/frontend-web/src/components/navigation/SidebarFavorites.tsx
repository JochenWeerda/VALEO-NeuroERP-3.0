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
    <div className="mb-3 rounded-md border bg-muted/30 p-2">
      <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-muted-foreground">Favoriten</p>
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
                  'flex items-center gap-2 rounded-md px-2 py-1.5 text-xs font-medium transition-colors',
                  'hover:bg-accent hover:text-accent-foreground',
                  isActive ? 'bg-accent text-accent-foreground' : 'text-muted-foreground',
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
