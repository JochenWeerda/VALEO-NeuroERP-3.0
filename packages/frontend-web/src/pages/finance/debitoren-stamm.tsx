import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'finance/debitoren/new',
  'finance-debitoren-new',
  () => import('./debitoren-stamm-legacy'),
)
