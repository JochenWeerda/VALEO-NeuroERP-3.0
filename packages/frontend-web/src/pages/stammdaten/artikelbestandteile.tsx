import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'stammdaten/artikelbestandteile',
  'stammdaten-artikelbestandteile',
  () => import('./stammdaten/artikelbestandteile-legacy'),
)
