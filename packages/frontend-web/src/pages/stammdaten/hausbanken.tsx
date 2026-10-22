import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'stammdaten/hausbanken',
  'stammdaten-hausbanken',
  () => import('./stammdaten/hausbanken-legacy'),
)
