import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'service/anfrage',
  'service-anfrage-stamm',
  () => import('./detail-legacy'),
)
