import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Stamm + Create: ScreenDefinition crm/betriebsprofil
 * (POST /api/v1/crm/betriebsprofile). Frueher fehlende ScreenId crm/betriebsprofil-detail.
 */
export default createStammNativeDetailPage(
  'crm/betriebsprofil',
  'crm-betriebsprofil-detail',
)
