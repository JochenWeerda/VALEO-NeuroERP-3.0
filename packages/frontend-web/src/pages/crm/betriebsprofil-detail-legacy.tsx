import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/betriebsprofil',
  'crm-betriebsprofil-stamm',
  () => import('./detail-legacy'),
)
