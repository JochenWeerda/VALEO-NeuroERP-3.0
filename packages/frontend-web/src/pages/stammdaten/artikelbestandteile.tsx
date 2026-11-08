import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'stammdaten/artikelbestandteile',
  'stammdaten-artikelbestandteile',
  () => import('./artikelbestandteile-legacy'),
)
