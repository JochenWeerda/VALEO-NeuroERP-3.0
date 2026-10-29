import { describe, expect, it } from 'vitest'
import { orderDragId, resolveBoardDrop, resourceDropId, timelineDropId } from '@/components/mask-builder/specialized/board-dnd'

describe('resolveBoardDrop', () => {
  it('mappt dnd-kit IDs auf Auftrag und Ressource', () => {
    expect(resolveBoardDrop(orderDragId('ord-1'), resourceDropId('tour-1'))).toEqual({
      orderId: 'ord-1',
      resourceId: 'tour-1',
    })
  })

  it('ignoriert Drop ohne Ziel oder gleiche IDs', () => {
    expect(resolveBoardDrop(orderDragId('ord-1'), null)).toBeNull()
    expect(resolveBoardDrop(orderDragId('ord-1'), orderDragId('ord-2'))).toBeNull()
    expect(resolveBoardDrop(orderDragId('same'), resourceDropId('same'))).toBeNull()
  })

  it('mappt Drop auf die Zeitachse auf dieselbe Ressource', () => {
    expect(resolveBoardDrop(orderDragId('ord-1'), timelineDropId('tour-1'))).toEqual({
      orderId: 'ord-1',
      resourceId: 'tour-1',
    })
  })
})
