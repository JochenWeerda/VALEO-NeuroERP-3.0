import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/opportunity',
  'crm-opportunity-detail',
  () => import('./opportunity-detail-legacy'),
)
