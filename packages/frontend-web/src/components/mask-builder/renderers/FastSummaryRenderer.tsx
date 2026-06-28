import { memo } from 'react'
import { ScreenSummaryGrid } from './ScreenSummaryGrid'
import type { ScreenSummaryItem } from '../schema'

export const FastSummaryRenderer = memo(function FastSummaryRenderer({
  items,
}: {
  items: ScreenSummaryItem[]
}): JSX.Element | null {
  if (items.length === 0) return null
  return <ScreenSummaryGrid items={items} />
})
