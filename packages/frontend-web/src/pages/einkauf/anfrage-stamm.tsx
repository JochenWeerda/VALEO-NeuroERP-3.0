import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'einkauf/anfrage',
  'einkauf-anfrage-stamm',
  () => import('./anfrage-stamm-legacy'),
)
