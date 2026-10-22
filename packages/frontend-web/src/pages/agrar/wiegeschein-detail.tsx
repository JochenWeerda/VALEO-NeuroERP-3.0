import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function WiegescheinDetailPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="agrar/wiegeschein-detail" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="agrar/wiegeschein-detail" />
}
void madeByStudioRuntimeWireDeclaration
