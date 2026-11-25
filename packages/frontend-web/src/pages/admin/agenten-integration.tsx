import { IntakeWeighingPage } from '@/components/mask-builder/specialized/intake/domain-runtime'

/** Named export bleibt fuer Control-Center-Surfaces (keine zyklische Route). */
export { AgentenIntegrationWorkspace } from './agenten-integration-legacy'

/** Native admin_workbench: ScreenDefinition admin/agenten-integration (Batch 28b). */
export default function AgentenIntegrationPage(): JSX.Element {
  return <IntakeWeighingPage screenId="admin/agenten-integration" />
}
