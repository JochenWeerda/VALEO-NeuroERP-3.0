import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function BranchesPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/branches" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/branches" />
}
void madeByStudioRuntimeWireDeclaration
