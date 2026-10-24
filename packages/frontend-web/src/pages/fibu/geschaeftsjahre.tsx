import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'fibu/geschaeftsjahre',
  'fibu-geschaeftsjahre',
  () => import('./geschaeftsjahre-legacy'),
)
