import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'verkauf/kunden-stamm',
  'verkauf-kunden-stamm',
  () => import('./kunden-stamm-legacy'),
)
