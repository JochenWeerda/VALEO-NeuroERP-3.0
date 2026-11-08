import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'kontrakte/mengenzeitraeume',
  'kontrakte-mengenzeitraeume',
  () => import('./mengenzeitraeume-legacy'),
)
