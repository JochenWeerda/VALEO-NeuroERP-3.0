import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function LieferscheinErstellenPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="agrar/lieferschein-erstellen" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="agrar/lieferschein-erstellen" />
}
void madeByStudioRuntimeWireDeclaration
