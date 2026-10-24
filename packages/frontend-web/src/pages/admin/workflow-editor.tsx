import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function WorkflowEditorPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/workflow-editor" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/workflow-editor" />
}
void madeByStudioRuntimeWireDeclaration
