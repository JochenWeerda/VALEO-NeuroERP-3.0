import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'finance/kreditoren-stamm',
  'finance-kreditoren-stamm',
  () => import('./finance/kreditoren-stamm-legacy'),
)
