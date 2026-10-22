import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'futtermittel/einzelfuttermittel/stamm/new',
  'futtermittel-einzelfuttermittel-stamm-new',
  () => import('./futtermittel/einzelfuttermittel-stamm-legacy'),
)
