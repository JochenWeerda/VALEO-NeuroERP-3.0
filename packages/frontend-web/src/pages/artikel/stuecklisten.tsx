import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function StuecklistenPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="artikel/stuecklisten" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="artikel/stuecklisten" />
}
void madeByStudioRuntimeWireDeclaration
