import { NativeListPage } from '@/components/mask-builder'

/**
 * Native Liste: ScreenDefinition admin/ai-approvals
 * Offene Eingangsrechnungen + Freigabe-Aktion — Parität zur Legacy-Worklist.
 */
export default function AiApprovalsPage(): JSX.Element {
  return <NativeListPage screenId="admin/ai-approvals" testId="screen-admin/ai-approvals" />
}
