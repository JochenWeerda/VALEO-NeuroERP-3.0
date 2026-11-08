import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function DividendenPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="aktien/dividenden" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="aktien/dividenden" />
}
void madeByStudioRuntimeWireDeclaration
