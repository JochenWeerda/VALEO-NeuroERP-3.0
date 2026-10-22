import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'finance/bankkonten-stamm',
  'finance-bankkonten-stamm',
  () => import('./finance/bankkonten-stamm-legacy'),
)
