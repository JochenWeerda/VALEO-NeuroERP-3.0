import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'finance/bank-account',
  'finance-bank-account-stamm',
  () => import('./stamm-legacy'),
)
