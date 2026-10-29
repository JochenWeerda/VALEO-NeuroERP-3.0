import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'stammdaten/artikelverpackung',
  'stammdaten-artikelverpackung',
  () => import('./artikelverpackung-legacy'),
)
