import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'preise/individualpreise',
  'preise-individualpreise',
  () => import('./preise/individualpreise-legacy'),
)
