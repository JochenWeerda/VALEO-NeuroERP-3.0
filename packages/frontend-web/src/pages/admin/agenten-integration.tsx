import { createStammNativeDetailPage } from '@/components/mask-builder'

export { AgentenIntegrationWorkspace } from './agenten-integration-legacy'

export default createStammNativeDetailPage(
  'admin/agenten-integration',
  'admin-agenten-integration',
  () => import('./agenten-integration-legacy'),
)
