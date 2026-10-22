import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'sales/delivery-editor-new',
  'sales-delivery-editor-new',
  () => import('./sales/delivery-editor-new-legacy'),
)
