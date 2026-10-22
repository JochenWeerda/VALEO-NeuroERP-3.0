import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'futtermittel/mischfuttermittel/stamm/new',
  'futtermittel-mischfuttermittel-stamm-new',
  () => import('./futtermittel/mischfuttermittel-stamm-legacy'),
)
