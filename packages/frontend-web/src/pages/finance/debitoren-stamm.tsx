import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'finance/debitoren/new',
  'finance-debitoren-new',
  () => import('./finance/debitoren-stamm-legacy'),
)
