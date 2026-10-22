import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'lager/massebilanz',
  'lager-massebilanz',
  () => import('./massebilanz-legacy'),
)
