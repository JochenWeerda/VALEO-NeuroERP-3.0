import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'finance/ap-invoice',
  'einkauf-rechnungseingang',
  () => import('./rechnungseingang-legacy'),
)
