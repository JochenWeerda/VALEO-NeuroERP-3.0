import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'finance/kreditor',
  'finance-kreditoren-stamm',
  () => import('./kreditoren-stamm-legacy'),
)
