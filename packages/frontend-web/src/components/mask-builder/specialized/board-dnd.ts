export const ORDER_DRAG_PREFIX = 'order:'
export const RESOURCE_DROP_PREFIX = 'resource:'
export const TIMELINE_DROP_PREFIX = 'timeline:'

export function orderDragId(orderId: string): string {
  return `${ORDER_DRAG_PREFIX}${orderId}`
}

export function resourceDropId(resourceId: string): string {
  return `${RESOURCE_DROP_PREFIX}${resourceId}`
}

export function timelineDropId(resourceId: string): string {
  return `${TIMELINE_DROP_PREFIX}${resourceId}`
}

function resourceIdFromOver(overId: string): string | null {
  if (overId.startsWith(RESOURCE_DROP_PREFIX)) return overId.slice(RESOURCE_DROP_PREFIX.length)
  if (overId.startsWith(TIMELINE_DROP_PREFIX)) return overId.slice(TIMELINE_DROP_PREFIX.length)
  return null
}

/** Mappt dnd-kit active/over auf denselben Assign-POST wie zuvor. */
export function resolveBoardDrop(
  activeId: string,
  overId: string | null | undefined,
): { orderId: string; resourceId: string } | null {
  if (!overId) return null
  if (!activeId.startsWith(ORDER_DRAG_PREFIX)) return null
  const resourceId = resourceIdFromOver(overId)
  const orderId = activeId.slice(ORDER_DRAG_PREFIX.length)
  if (!orderId || !resourceId || orderId === resourceId) return null
  return { orderId, resourceId }
}
