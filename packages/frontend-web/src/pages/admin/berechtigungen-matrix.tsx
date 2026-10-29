import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function BerechtigungenMatrixPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/berechtigungen-matrix" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="admin/berechtigungen-matrix" />
}
void madeByStudioRuntimeWireDeclaration
