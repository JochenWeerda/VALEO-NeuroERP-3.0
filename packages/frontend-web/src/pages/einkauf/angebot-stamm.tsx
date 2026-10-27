import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'einkauf/angebot',
  'einkauf-angebot-stamm',
  () => import('./angebot-stamm-legacy'),
)
