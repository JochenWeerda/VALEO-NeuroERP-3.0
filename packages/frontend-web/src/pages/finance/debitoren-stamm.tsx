import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'finance/debitor',
  'finance-debitoren-stamm',
  () => import('./debitoren-stamm-legacy'),
)
