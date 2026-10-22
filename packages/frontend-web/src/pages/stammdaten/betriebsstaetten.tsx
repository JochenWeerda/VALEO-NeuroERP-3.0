import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'stammdaten/betriebsstaetten',
  'stammdaten-betriebsstaetten',
  () => import('./stammdaten/betriebsstaetten-legacy'),
)
