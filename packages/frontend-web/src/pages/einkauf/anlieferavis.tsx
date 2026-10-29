import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'einkauf/anlieferavis',
  'einkauf-anlieferavis',
  () => import('./anlieferavis-legacy'),
)
