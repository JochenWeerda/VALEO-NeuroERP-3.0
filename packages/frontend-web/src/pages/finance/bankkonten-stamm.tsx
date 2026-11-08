import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'finance/bankkonto',
  'finance-bankkonten-stamm',
  () => import('./bankkonten-stamm-legacy'),
)
