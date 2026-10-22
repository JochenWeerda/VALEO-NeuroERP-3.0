import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'sales/delivery-editor',
  'sales-delivery-editor',
  () => import('./sales/delivery-editor-legacy'),
)
