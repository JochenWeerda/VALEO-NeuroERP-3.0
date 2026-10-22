import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'verkauf/kunden-stamm-enhanced',
  'verkauf-kunden-stamm-enhanced',
  () => import('./verkauf/kunden-stamm-enhanced-legacy'),
)
