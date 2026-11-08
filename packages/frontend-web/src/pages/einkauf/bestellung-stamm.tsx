import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'einkauf/purchase-order',
  'einkauf-bestellung-stamm',
  () => import('./bestellung-stamm-legacy'),
)
