import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'stammdaten/mengeneinheiten',
  'stammdaten-mengeneinheiten',
  () => import('./stammdaten/mengeneinheiten-legacy'),
)
