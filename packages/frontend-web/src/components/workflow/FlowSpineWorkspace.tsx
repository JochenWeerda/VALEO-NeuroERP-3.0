import { useFlowSpineWorkspaceRuntime } from '@/components/mask-builder/runtime/useFlowSpineWorkspaceRuntime'
import { FlowSpineWorkspaceRenderer } from '@/components/mask-builder/renderers/FlowSpineWorkspaceRenderer'

export function FlowSpineWorkspace({ processKey, instanceId }: { processKey: string; instanceId?: string }): JSX.Element {
  return <FlowSpineWorkspaceRenderer state={useFlowSpineWorkspaceRuntime(processKey, instanceId)} />
}
export default FlowSpineWorkspace
