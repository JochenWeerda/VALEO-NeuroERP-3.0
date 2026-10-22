import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'stammdaten/artikel-stoffstrom',
  'stammdaten-artikel-stoffstrom',
  () => import('./stammdaten/artikel-stoffstrom-legacy'),
)
