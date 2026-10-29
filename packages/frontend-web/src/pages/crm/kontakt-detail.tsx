import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'crm/kontakte/new',
  'crm-kontakte-new',
  () => import('./kontakt-detail-legacy'),
)
