import { MadeByStudioDetailRuntimeWire } from '@/components/mask-builder/made-by-studio-runtime-wire'

export default function VoranmeldungPage(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="annahme/voranmeldung" />
}

function madeByStudioRuntimeWireDeclaration(): JSX.Element {
  return <MadeByStudioDetailRuntimeWire screenId="annahme/voranmeldung" />
}
void madeByStudioRuntimeWireDeclaration
