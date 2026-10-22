import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/opportunity/new',
  'crm-opportunity-new',
  () => import('./opportunity-detail-legacy'),
)
