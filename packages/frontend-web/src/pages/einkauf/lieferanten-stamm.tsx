import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'einkauf/lieferanten-stamm',
  'einkauf-lieferanten-stamm',
  () => import('./einkauf/lieferanten-stamm-legacy'),
)
