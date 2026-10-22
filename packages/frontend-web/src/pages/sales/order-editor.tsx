import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'verkauf/auftraege/neu',
  'verkauf-auftraege-neu',
  () => import('./sales/order-editor-legacy'),
)
