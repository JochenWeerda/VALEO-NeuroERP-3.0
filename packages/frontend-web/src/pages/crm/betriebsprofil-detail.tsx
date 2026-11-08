import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/betriebsprofil-detail',
  'crm-betriebsprofil-detail',
  () => import('./betriebsprofil-detail-legacy'),
)
