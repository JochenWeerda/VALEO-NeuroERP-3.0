import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'service/anfrage-detail',
  'service-anfrage-detail',
  () => import('./anfrage-detail-legacy'),
)
