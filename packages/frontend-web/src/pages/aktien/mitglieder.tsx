import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function MitgliederPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="aktien/mitglieder" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="aktien/mitglieder" />
}
void madeByStudioRuntimeWireDeclaration
