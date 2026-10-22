import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function PflanzenschutzPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="agrar/schlaege/pflanzenschutz" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="agrar/schlaege/pflanzenschutz" />
}
void madeByStudioRuntimeWireDeclaration
