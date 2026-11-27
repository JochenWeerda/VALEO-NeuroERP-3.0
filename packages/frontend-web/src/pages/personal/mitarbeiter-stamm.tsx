import { createStammNativeDetailPage } from '@/components/mask-builder'

/**
 * Native Stamm + Create: personal/mitarbeiter/neu → POST /api/v1/personal/mitarbeiter.
 * Route /personal/mitarbeiter/neu und /personal/mitarbeiter/:id.
 */
export default createStammNativeDetailPage(
  'personal/mitarbeiter/neu',
  'personal-mitarbeiter-neu',
)
