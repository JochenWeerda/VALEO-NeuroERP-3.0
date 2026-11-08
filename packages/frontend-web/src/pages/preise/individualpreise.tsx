import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'preise/individualpreise',
  'preise-individualpreise',
  () => import('./individualpreise-legacy'),
)
