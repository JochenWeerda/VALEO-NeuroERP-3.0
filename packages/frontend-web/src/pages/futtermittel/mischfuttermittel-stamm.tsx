import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'futtermittel/mischfuttermittel',
  'futtermittel-mischfuttermittel-stamm',
  () => import('./mischfuttermittel-stamm-legacy'),
)
