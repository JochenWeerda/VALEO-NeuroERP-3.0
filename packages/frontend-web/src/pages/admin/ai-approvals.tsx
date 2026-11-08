import { createStammNativeDetailPage } from '@/components/mask-builder'

export default createStammNativeDetailPage(
  'admin/ai-approvals',
  'admin-ai-approvals',
  () => import('./ai-approvals-legacy'),
)
