import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'futtermittel/einzelfuttermittel',
  'futtermittel-einzelfuttermittel-stamm',
  () => import('./einzelfuttermittel-stamm-legacy'),
)
