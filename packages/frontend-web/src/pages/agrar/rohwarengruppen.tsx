import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Create: POST /api/v1/rohware/gruppen (responseIdKey=gruppe_nr).
 * Legacy-Workspace (Schemata/Staffeln) bleibt als Rollback unter *-legacy.
 */
export default createStammNativeDetailPage(
  'agrar/rohwarengruppen',
  'agrar-rohwarengruppen',
)
