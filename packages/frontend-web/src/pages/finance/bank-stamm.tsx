import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'finance/bank-stamm',
  'finance-bank-stamm',
  () => import('./bank-stamm-legacy'),
)
