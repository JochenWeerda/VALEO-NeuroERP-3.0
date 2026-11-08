import type { LaunchpadSpace } from '@/app/navigation/launchpad-spaces'
import { orderLaunchpadTileIds } from './prioritization'
import type { UserContext } from './types'

export function prioritizeLaunchpadSpaces(
  spaces: LaunchpadSpace[],
  rankedTileIds: string[],
  context: Pick<UserContext, 'pinned' | 'surfaceLocked'>,
): LaunchpadSpace[] {
  return spaces.map((space) => ({
    ...space,
    pages: space.pages.map((page) => {
      const orderedIds = orderLaunchpadTileIds(
        page.tiles.map((tile) => tile.id),
        rankedTileIds,
        context,
      )
      const byId = new Map(page.tiles.map((tile) => [tile.id, tile]))
      return {
        ...page,
        tiles: orderedIds.flatMap((id) => {
          const tile = byId.get(id)
          return tile ? [tile] : []
        }),
      }
    }),
  }))
}
