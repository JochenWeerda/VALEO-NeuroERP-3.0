import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'service/anfrage/neu',
  'service-anfrage-neu',
  () => import('./anfrage-neu-legacy'),
)
