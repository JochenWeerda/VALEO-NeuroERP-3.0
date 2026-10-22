import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'verkauf/kunden-stamm',
  'verkauf-kunden-stamm',
  () => import('./verkauf/kunden-stamm-legacy'),
)
