import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'lager/massebilanz',
  'lager-massebilanz',
  () => import('./lager/massebilanz-legacy'),
)
