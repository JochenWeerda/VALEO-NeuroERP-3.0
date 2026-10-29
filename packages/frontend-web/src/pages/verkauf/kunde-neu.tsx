import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'verkauf/kunde-neu',
  'verkauf-kunde-neu',
  () => import('./kunde-neu-legacy'),
)
