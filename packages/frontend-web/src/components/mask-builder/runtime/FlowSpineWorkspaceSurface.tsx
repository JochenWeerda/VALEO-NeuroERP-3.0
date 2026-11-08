import type { ScreenDefinition } from '../schema'
import { useFlowSpineWorkspaceRuntime } from './useFlowSpineWorkspaceRuntime'
import { FlowSpineWorkspaceRenderer } from '../renderers/FlowSpineWorkspaceRenderer'

export default function FlowSpineWorkspaceSurface({ contract }: { contract: NonNullable<ScreenDefinition['flowSpineWorkspace']> }): JSX.Element {
  const state = useFlowSpineWorkspaceRuntime(contract.processKey)
  return <FlowSpineWorkspaceRenderer state={state} />
}
